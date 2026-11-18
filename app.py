# -*- coding: utf-8 -*-
"""出海雷达 · AI 出海营销助手（Streamlit 演示）

五步：客户分析 → 客户联系 → 方案撰写 → 执行交付 → 数据复盘
运行：streamlit run app.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

import llm
import offline
import prompts
import scoring

BASE = Path(__file__).parent
STEPS = ["① 客户分析", "② 客户联系", "③ 方案撰写", "④ 执行交付", "⑤ 数据复盘"]

st.set_page_config(page_title="出海雷达 · AI 出海营销助手", page_icon="🧭", layout="wide")


# ---------------------------------------------------------------- 数据
@st.cache_data
def load_json(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


DATA = load_json("customers.json")
FLAGS = load_json("review_flags.json")
CAMPAIGN = load_json("campaign.json")
CUSTOMERS = {c["id"]: c for c in DATA["customers"]}
RANKED = scoring.rank(DATA["customers"], FLAGS)


# ---------------------------------------------------------------- 状态
def init_state() -> None:
    st.session_state.setdefault("step_idx", 0)
    st.session_state.setdefault("cid", "c01")
    st.session_state.setdefault("results", {})
    st.session_state.setdefault("api_key_input", "")


init_state()


def customer() -> dict:
    return CUSTOMERS[st.session_state["cid"]]


def cached(step: str):
    return st.session_state["results"].get(f"{step}:{st.session_state['cid']}")


def generate(step: str, builder, fallback) -> dict:
    """统一入口：有 key 走模型，失败或无 key 走离线兜底。"""
    key = f"{step}:{st.session_state['cid']}"
    with st.spinner("AI 正在生成…"):
        system, user = builder()
        out = llm.chat_json(system, user)
        if out is None:
            out = fallback()
            out["_source"] = "offline"
        elif "_error" in out:
            st.session_state["last_error"] = out["_error"]
            out = fallback()
            out["_source"] = "offline"
        else:
            out["_source"] = "llm"
        st.session_state["results"][key] = out
        st.session_state.pop("last_error", None)
    st.rerun()


def source_note(result: dict) -> None:
    if not result:
        return
    if result.get("_source") == "llm":
        st.caption(f"由 {llm.model_name()} 生成")
    else:
        st.caption("离线模式：以下为预置结果（配置 API Key 后可切换为模型生成）")


# ---------------------------------------------------------------- 侧边栏
def sidebar() -> None:
    with st.sidebar:
        st.markdown("### 🧭 出海雷达")
        st.caption("TikTok 出海营销 · 内部销售工作台")

        idx = st.radio(
            "步骤",
            range(len(STEPS)),
            index=st.session_state["step_idx"],
            format_func=lambda i: STEPS[i],
            key=f"nav_{st.session_state['step_idx']}",
            label_visibility="collapsed",
        )
        if idx != st.session_state["step_idx"]:
            st.session_state["step_idx"] = idx
            st.rerun()

        st.divider()
        options = [r["id"] for r in RANKED]
        names = {r["id"]: f"{r['name']}" for r in RANKED}
        cid = st.selectbox(
            "当前客户",
            options,
            index=options.index(st.session_state["cid"]) if st.session_state["cid"] in options else 0,
            format_func=lambda c: names[c],
        )
        if cid != st.session_state["cid"]:
            st.session_state["cid"] = cid
            st.rerun()

        row = next(r for r in RANKED if r["id"] == cid)
        if row["verdict"] == "红牌排除":
            st.error(f"该客户已红牌排除：{row['note']}")
        elif "黄牌" in row["verdict"]:
            st.warning(f"黄牌提示：{row['note']}")

        st.divider()
        st.markdown("**模型状态**")
        if llm.enabled():
            if llm.model_is_free():
                st.success(f"已连接 · {llm.model_name()}（免费额度）")
            else:
                st.warning(f"已连接 · {llm.model_name()}（非免费模型）")
            st.caption("免费额度可能临近过期，实际计费以百炼控制台为准")
        else:
            st.info("离线模式（使用预置结果）")
            key = st.text_input("DASHSCOPE_API_KEY", type="password", key="api_key_input", placeholder="sk-...")
            if key and key.strip() != os.environ.get("DASHSCOPE_API_KEY"):
                os.environ["DASHSCOPE_API_KEY"] = key.strip()
                st.rerun()
            st.caption("Key 只存在于本次进程内存，不写文件、不读环境变量")

        st.divider()
        if st.button("↺ 清空本会话结果", width="stretch"):
            st.session_state["results"] = {}
            st.rerun()
        st.caption("演示数据：全部客户与投放数据均为虚构。")


# ---------------------------------------------------------------- 步骤一
def step_analysis() -> None:
    st.subheader("① 潜在客户分析：先跟谁，为什么")
    st.caption("规则打分负责排序，人工红黄牌负责否决——机器给分，人做判断。")

    df = pd.DataFrame(
        [
            {
                "排名": i,
                "客户": r["name"],
                "总分": r["total"],
                "意图": r["dims"]["intent"],
                "付费": r["dims"]["budget"],
                "适配": r["dims"]["fit"],
                "触达": r["dims"]["reach"],
                "结论": r["verdict"],
            }
            for i, r in enumerate(RANKED, 1)
        ]
    )
    st.dataframe(df, hide_index=True, width="stretch", height=430)

    c = customer()
    st.divider()
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown(f"#### {c['name']}")
        st.write(c["one_liner"])
        st.markdown("**档案信号**")
        for s in c["signals"]:
            st.markdown(f"- {s}")
        st.markdown("**可引用原文**")
        for sn in c["snippets"]:
            st.caption(f"— {sn['source']}：{sn['text']}")
    with right:
        t = c["tiktok"]
        st.markdown("**TikTok 现状**")
        st.write(f"粉丝 {t['followers']:,} · 近 90 天 {t['posts_90d']} 条 · 最高 {t['top_views']:,} 播放")
        st.write(f"平均播放 {t['avg_views']:,} · 最后更新 {t['last_post'] or '—'}")
        st.markdown("**投放状态**")
        st.write("在投：" + ("是" if c["ads"]["active"] else "否") + (f"（{c['ads']['note']}）" if c["ads"]["note"] else ""))
        st.markdown("**已知风险**")
        for r in c.get("risk", []):
            st.markdown(f"- {r}")

    st.divider()
    result = cached("analysis")
    if st.button("🤖 生成优先跟进判断", type="primary", key="btn_analysis"):
        generate("analysis", lambda: prompts.analysis(c), lambda: offline.analysis(c))

    if result:
        st.success(result["verdict"])
        st.markdown("**为什么是它**")
        for r in result.get("reasons", []):
            st.markdown(f"- {r}")
        if result.get("risks"):
            st.markdown("**风险与前置条件**")
            for r in result["risks"]:
                st.markdown(f"- {r}")
        st.info(f"切入点：{result.get('entry_point', '')}")
        source_note(result)


# ---------------------------------------------------------------- 步骤二
def step_outreach() -> None:
    st.subheader("② 潜在客户联系：发什么，怎么跟")
    st.caption("每条文案都必须能指回客户的某条公开信息，销售才敢发。")

    c = customer()
    result = cached("outreach")

    if st.button("✉️ 生成触达文案与跟进节奏", type="primary", key="btn_outreach"):
        analysis = cached("analysis") or offline.analysis(c)
        generate("outreach", lambda: prompts.outreach(c, analysis), lambda: offline.outreach(c, analysis))

    if not result:
        st.info("点击上方按钮生成三渠道文案。")
        return

    tabs = st.tabs([ch["name"] for ch in result.get("channels", [])])
    for tab, ch in zip(tabs, result.get("channels", [])):
        with tab:
            if ch.get("subject"):
                st.markdown(f"**主题：** {ch['subject']}")
            st.code(ch.get("body", ""), language=None)
            st.caption(f"钩子来源：{ch.get('hook_source', '—')}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 跟进节奏")
        st.dataframe(
            pd.DataFrame(result.get("followups", [])).rename(
                columns={"day": "时间", "channel": "渠道", "action": "动作"}
            ),
            hide_index=True,
            width="stretch",
        )
    with col2:
        st.markdown("##### 回复分类 → 下一步")
        st.dataframe(
            pd.DataFrame(result.get("reply_playbook", [])).rename(
                columns={"intent": "客户回复", "next": "下一步动作"}
            ),
            hide_index=True,
            width="stretch",
        )
    source_note(result)


# ---------------------------------------------------------------- 步骤三
def step_proposal() -> None:
    st.subheader("③ 方案撰写：一页纸，销售讲 30 分钟")
    st.caption("方案不是作文，是把客户的具体情况填进结构里。")

    c = customer()
    result = cached("proposal")

    if st.button("📄 生成服务方案", type="primary", key="btn_proposal"):
        analysis = cached("analysis") or offline.analysis(c)
        generate("proposal", lambda: prompts.proposal(c, analysis), lambda: offline.proposal(c, analysis))

    if not result:
        st.info("点击上方按钮生成方案。")
        return

    left, right = st.columns([1.4, 1])
    with left:
        st.markdown(f"**目标**：{result.get('goal', '')}")
        st.markdown(f"**现状判断**：{result.get('insight', '')}")
        st.markdown(f"**核心打法**：{result.get('strategy', '')}")
    with right:
        st.markdown("##### KPI 与基准")
        st.dataframe(
            pd.DataFrame(result.get("kpi", [])).rename(
                columns={"metric": "指标", "target": "目标", "benchmark": "行业参考"}
            ),
            hide_index=True,
            width="stretch",
        )

    st.markdown("##### 内容矩阵")
    st.dataframe(
        pd.DataFrame(result.get("content_matrix", [])).rename(
            columns={"pillar": "栏目", "angle": "角度", "example": "示例选题"}
        ),
        hide_index=True,
        width="stretch",
    )

    col1, col2 = st.columns([1, 1.3])
    with col1:
        st.markdown("##### 达人配比")
        st.dataframe(
            pd.DataFrame(result.get("creator_mix", [])).rename(
                columns={"tier": "层级", "count": "条数", "budget": "预算"}
            ),
            hide_index=True,
            width="stretch",
        )
    with col2:
        st.markdown("##### 交付节奏")
        st.dataframe(
            pd.DataFrame(result.get("timeline", [])).rename(
                columns={"week": "时间", "deliverable": "交付物"}
            ),
            hide_index=True,
            width="stretch",
        )

    st.markdown("##### 报价三档")
    cols = st.columns(max(1, len(result.get("pricing", []))))
    for col, p in zip(cols, result.get("pricing", [])):
        with col:
            with st.container(border=True):
                st.markdown(f"**{p.get('tier')}**")
                st.markdown(f"### {p.get('price')}")
                st.caption(p.get("scope", ""))

    md = _proposal_markdown(c, result)
    st.download_button("⬇ 下载方案（Markdown）", md, file_name=f"{c['name']}_方案.md", mime="text/markdown")
    source_note(result)


def _proposal_markdown(c: dict, r: dict) -> str:
    lines = [f"# {c['name']} · TikTok 出海营销方案", "", f"**目标**：{r.get('goal', '')}", "", f"**现状判断**：{r.get('insight', '')}", "", f"**核心打法**：{r.get('strategy', '')}", "", "## 内容矩阵", ""]
    for m in r.get("content_matrix", []):
        lines.append(f"- **{m.get('pillar')}**（{m.get('angle')}）：{m.get('example')}")
    lines += ["", "## KPI", ""]
    for k in r.get("kpi", []):
        lines.append(f"- {k.get('metric')}：目标 {k.get('target')}（参考 {k.get('benchmark')}）")
    lines += ["", "## 报价", ""]
    for p in r.get("pricing", []):
        lines.append(f"- {p.get('tier')}：{p.get('price')} —— {p.get('scope')}")
    lines += ["", "## 节奏", ""]
    for t in r.get("timeline", []):
        lines.append(f"- {t.get('week')}：{t.get('deliverable')}")
    return "\n".join(lines)


# ---------------------------------------------------------------- 步骤四
def step_delivery() -> None:
    st.subheader("④ 执行交付：方案变任务，给一个样例")
    st.caption("方案到执行之间的翻译，最容易失真。")

    c = customer()
    result = cached("delivery")

    if st.button("🗂 拆解任务并生成交付样例", type="primary", key="btn_delivery"):
        proposal = cached("proposal") or offline.proposal(c, offline.analysis(c))
        generate("delivery", lambda: prompts.delivery(c, proposal), lambda: offline.delivery(c, proposal))

    if not result:
        st.info("点击上方按钮生成任务清单与样例。")
        return

    st.markdown("##### 任务清单")
    st.dataframe(
        pd.DataFrame(result.get("tasks", [])).rename(
            columns={"owner": "负责人", "due": "截止", "deliverable": "交付物", "acceptance": "验收标准"}
        ),
        hide_index=True,
        width="stretch",
    )

    st.markdown("##### 交付样例：15 秒脚本")
    for s in result.get("scripts", []):
        with st.expander(f"{s.get('name')}", expanded=False):
            st.markdown(f"**0-2s｜钩子**　{s.get('hook', '')}")
            st.markdown(f"**2-8s｜演示**　{s.get('body', '')}")
            st.markdown(f"**12-15s｜行动**　{s.get('cta', '')}")
    source_note(result)


# ---------------------------------------------------------------- 步骤五
def step_review() -> None:
    st.subheader("⑤ 数据复盘：判断效果，提出下一轮")
    st.caption("复盘不是“要优化”，是定位到某一层，并且只改一个变量。")

    c = customer()
    m = _metrics()
    bm = CAMPAIGN["benchmark"]

    cols = st.columns(5)
    for col, (label, key, fmt) in zip(
        cols,
        [("CPM", "cpm", "$"), ("CTR", "ctr", "%"), ("CPA", "cpa", "$"), ("ROAS", "roas", "x"), ("3 秒完播", "video_3s_view_rate", "%")],
    ):
        value = m[key]
        target = bm[key]
        ok = value <= target if key in ("cpm", "cpa") else value >= target
        col.metric(label, f"{fmt}{value}" if fmt in ("$", "x") else f"{value}%", f"目标 {fmt}{target}" if fmt in ("$", "x") else f"目标 {target}%")

    st.dataframe(
        pd.DataFrame(
            [
                {"指标": k.upper(), "实际": m[k], "目标": bm[k], "状态": "达标" if _ok(k, m[k], bm[k]) else "未达标"}
                for k in ("cpm", "ctr", "cpa", "roas", "video_3s_view_rate")
            ]
        ),
        hide_index=True,
        width="stretch",
    )
    st.caption(f"统计周期 {CAMPAIGN['period']} · 花费 ${CAMPAIGN['spend_usd']:,} · 转化 {CAMPAIGN['conversions']} 单")

    result = cached("review")
    if st.button("📊 生成复盘结论", type="primary", key="btn_review"):
        kpi = (cached("proposal") or offline.proposal(c, offline.analysis(c))).get("kpi", [])
        generate("review", lambda: prompts.review(c, m, kpi), lambda: offline.review(c, m, kpi))

    if result:
        st.error(f"瓶颈定位：**{result.get('bottleneck')}**")
        st.markdown(f"**诊断**：{result.get('diagnosis', '')}")
        st.markdown("**下一轮动作**")
        for a in result.get("actions", []):
            st.markdown(f"- {a}")
        ab = result.get("ab_test", {})
        st.info(f"下一轮实验：只改「{ab.get('variable')}」 · 假设：{ab.get('hypothesis')} · 观察：{ab.get('metric')}")
        source_note(result)


def _metrics() -> dict:
    s, i, c_, v, r = (
        CAMPAIGN["spend_usd"],
        CAMPAIGN["impressions"],
        CAMPAIGN["clicks"],
        CAMPAIGN["conversions"],
        CAMPAIGN["revenue_usd"],
    )
    return {
        "cpm": round(s / i * 1000, 2),
        "ctr": round(c_ / i * 100, 2),
        "cpc": round(s / c_, 2),
        "cvr": round(v / c_ * 100, 2),
        "cpa": round(s / v, 2),
        "roas": round(r / s, 2),
        "aov": round(r / v, 2),
        "video_3s_view_rate": round(CAMPAIGN["video_3s_view_rate"] * 100, 1),
    }


def _ok(key: str, value: float, target: float) -> bool:
    return value <= target if key in ("cpm", "cpa") else value >= target


# ---------------------------------------------------------------- 主流程
sidebar()

st.title("出海雷达 · AI 出海营销助手")
st.caption("从 12 家候选客户里挑出该跟的那一家，一路走到复盘。｜演示数据，全部虚构")

if llm.enabled():
    _warn = llm.model_warning()
    if _warn:
        st.warning(f"{_warn} 如需切换模型，改 free_models.json 的 default_model 后重启应用。")

if "last_error" in st.session_state:
    st.warning(f"模型调用失败，已回退离线结果：{st.session_state['last_error']}")

[step_analysis, step_outreach, step_proposal, step_delivery, step_review][st.session_state["step_idx"]]()

st.divider()
nav_left, nav_mid, nav_right = st.columns([1, 2, 1])
with nav_left:
    if st.session_state["step_idx"] > 0 and st.button("← 上一步", width="stretch"):
        st.session_state["step_idx"] -= 1
        st.rerun()
with nav_right:
    if st.session_state["step_idx"] < len(STEPS) - 1 and st.button("下一步 →", width="stretch"):
        st.session_state["step_idx"] += 1
        st.rerun()

st.caption("本演示不含任何真实客户数据；KPI 基准为公开资料量级参考，实际执行需按客户校准。")
