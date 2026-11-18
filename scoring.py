# -*- coding: utf-8 -*-
"""
客户优先级打分（规则层，不依赖大模型）

设计原则：
1. 分数由规则算出，可复现、可解释；大模型只负责把分数翻译成人话。
2. 机器分 + 人工红黄牌分开存放：facts 算分，review_flags.json 挂牌。
   红牌 = 直接排除；黄牌 = 可以跟，但必须先确认卡点。
3. 四个维度与 customers.json 的 icp 保持一致。
"""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).parent
DATA = BASE / "customers.json"
FLAGS = BASE / "review_flags.json"

# 与 customers.json 中 icp.dimensions 的权重保持一致
WEIGHTS = {"intent": 0.35, "budget": 0.30, "fit": 0.25, "reach": 0.10}

YELLOW_PENALTY = 8.0     # 黄牌扣分
STAGE_RANK_MAX = 3       # 融资轮次归一化上限


def _recency_score(months) -> float:
    """融资越近，付费窗口越大。"""
    if not months:
        return 0.25
    if months <= 6:
        return 1.0
    if months <= 9:
        return 0.75
    if months <= 12:
        return 0.50
    return 0.25


def _intent(f: dict) -> float:
    """出海意图：多语言站 + 招海外岗 + 海外社媒活跃。"""
    return (
        0.40 * float(bool(f.get("multi_language_site")))
        + 0.35 * float(bool(f.get("hiring_overseas")))
        + 0.25 * float(bool(f.get("tiktok_active")))
    )


def _budget(f: dict) -> float:
    """付费能力：融资新鲜度 60% + 轮次 40%。"""
    recency = _recency_score(f.get("funding_months_ago"))
    stage = min(int(f.get("funding_rank") or 0), STAGE_RANK_MAX) / STAGE_RANK_MAX
    return 0.6 * recency + 0.4 * stage


def _fit(f: dict) -> float:
    """内容适配度：能否被短视频讲清楚、是否 C 端、客单价够不够。"""
    return (
        0.50 * float(bool(f.get("demo_visual")))
        + 0.30 * float(bool(f.get("consumer_product")))
        + 0.20 * float((f.get("price_usd") or 0) >= 50)
    )


def _reach(f: dict) -> float:
    """可触达性：决策人找不找得到；已被收购的直接判死。"""
    if f.get("acquired"):
        return 0.0
    return 0.6 * float(bool(f.get("dm_public"))) + 0.4


def score_customer(customer: dict, flags: dict) -> dict:
    f = customer.get("facts", {})
    dims = {
        "intent": round(100 * _intent(f), 1),
        "budget": round(100 * _budget(f), 1),
        "fit": round(100 * _fit(f), 1),
        "reach": round(100 * _reach(f), 1),
    }
    raw = sum(dims[k] * WEIGHTS[k] for k in WEIGHTS)

    card = flags.get("cards", [])
    penalty = YELLOW_PENALTY if "yellow" in card else 0.0
    total = max(0.0, round(raw - penalty, 1))

    if "red" in card or f.get("acquired"):
        verdict = "红牌排除"
    elif total >= 60:
        verdict = "跟进（黄牌，先确认卡点）" if "yellow" in card else "跟进"
    else:
        verdict = "暂不跟进"

    return {
        "id": customer["id"],
        "name": customer["name"],
        "category": customer.get("category", ""),
        "dims": dims,
        "raw": round(raw, 1),
        "total": total,
        "cards": card,
        "note": flags.get("note", ""),
        "verdict": verdict,
    }


def rank(customers: list[dict], flags: dict) -> list[dict]:
    rows = [score_customer(c, flags.get(c["id"], {})) for c in customers]
    # 按分数排序，红牌不沉底：让“高分却被否”的对比直接可见
    return sorted(rows, key=lambda x: -x["total"])


def bar(value: float, width: int = 8) -> str:
    filled = int(round(value / 100 * width))
    return "█" * filled + "·" * (width - filled)


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    flags = json.loads(FLAGS.read_text(encoding="utf-8"))
    rows = rank(data["customers"], flags)

    print(f"{'#':<3}{'客户':<16}{'总分':>6}{'原始':>6}   {'意图':>4}{'付费':>4}{'适配':>4}{'触达':>4}  结论")
    print("-" * 82)
    for i, r in enumerate(rows, 1):
        d = r["dims"]
        mark = {"red": "🚫", "yellow": "⚠"}.get(r["cards"][0] if r["cards"] else "", " ")
        print(
            f"{i:<3}{r['name']:<16}{r['total']:>6.1f}{r['raw']:>6.1f}   "
            f"{d['intent']:>4.0f}{d['budget']:>4.0f}{d['fit']:>4.0f}{d['reach']:>4.0f}  {mark} {r['verdict']}"
        )
    print("-" * 82)

    follow = [r for r in rows if r["verdict"].startswith("跟进")]
    print(f"共 {len(rows)} 家，可跟进 {len(follow)} 家。")
    print()
    top = follow[0]
    print(f"首选：{top['name']}（{top['total']} 分，原始 {top['raw']} 分）")
    for k, label in (("intent", "出海意图"), ("budget", "付费能力"), ("fit", "内容适配"), ("reach", "可触达性")):
        print(f"  {label:<6}{bar(top['dims'][k])} {top['dims'][k]:.0f}")
    print()
    print("被否掉的（红牌）：")
    for r in rows:
        if r["verdict"] == "红牌排除":
            print(f"  · {r['name']}：{r['note']}")


if __name__ == "__main__":
    main()
