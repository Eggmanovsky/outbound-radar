# -*- coding: utf-8 -*-
"""五个环节的 prompt 模板。

约定：每个 prompt 都要求模型只输出一个 JSON 对象，字段与 offline.py 的兜底结构一致，
这样"有模型"和"没模型"两种情况下界面渲染代码完全相同。
"""
from __future__ import annotations

import json

SYSTEM = (
    "你是出海营销服务商的 AI 销售助手，服务对象是公司内部的销售与运营。"
    "你熟悉 TikTok 美区/欧洲的达人营销、内容代运营与 Spark Ads 投放。"
    "你的输出必须务实、具体、可执行，避免空话套话；所有判断都要能指回给定的客户资料。"
    "只输出一个 JSON 对象，不要输出任何解释性文字。"
)


def _brief(customer: dict) -> str:
    """把客户档案压缩成给模型看的简报。"""
    keep = {
        "name": customer.get("name"),
        "category": customer.get("category"),
        "one_liner": customer.get("one_liner"),
        "market": customer.get("market"),
        "hq": customer.get("hq"),
        "headcount": customer.get("headcount"),
        "funding": customer.get("funding"),
        "signals": customer.get("signals"),
        "snippets": customer.get("snippets"),
        "tiktok": customer.get("tiktok"),
        "ads": customer.get("ads"),
        "competitors": customer.get("competitors"),
        "risk": customer.get("risk"),
    }
    return json.dumps(keep, ensure_ascii=False, indent=2)


def analysis(customer: dict) -> tuple[str, str]:
    user = f"""下面是候选客户的档案：

{_brief(customer)}

请判断：现在是否值得优先跟进这家客户，为什么。

输出 JSON：
{{
  "verdict": "一句话结论，必须包含'现在跟/现在不跟'和核心理由",
  "reasons": ["3-4 条理由，每条必须引用档案里的具体事实（融资、招聘、账号数据等）"],
  "risks": ["1-2 条风险或前置条件"],
  "entry_point": "第一次沟通时建议切入的角度，一句话"
}}"""
    return SYSTEM, user


def outreach(customer: dict, analysis_result: dict) -> tuple[str, str]:
    user = f"""客户档案：
{_brief(customer)}

客户分析结论：
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}

请为这家客户准备首次触达内容。

要求：
1. 三版文案分别用于 LinkedIn 私信、冷邮件、WhatsApp，语气自然像真人，不要模板腔；
2. 每版的第一句必须引用客户档案里的某个具体事实（snippets 或 signals），并在 hook_source 里注明引用了哪一条；
3. 邮件要有 subject，其余两版 subject 留空字符串；
4. 正文控制在 120 字（中文）或 80 词（英文）以内。

输出 JSON：
{{
  "channels": [
    {{"name": "LinkedIn 私信", "subject": "", "body": "...", "hook_source": "引用自：..."}},
    {{"name": "冷邮件", "subject": "...", "body": "...", "hook_source": "..."}},
    {{"name": "WhatsApp", "subject": "", "body": "...", "hook_source": "..."}}
  ],
  "followups": [
    {{"day": "D0", "channel": "LinkedIn", "action": "..."}},
    {{"day": "D3", "channel": "...", "action": "..."}},
    {{"day": "D7", "channel": "...", "action": "..."}},
    {{"day": "D14", "channel": "...", "action": "..."}}
  ],
  "reply_playbook": [
    {{"intent": "有兴趣", "next": "..."}},
    {{"intent": "要资料", "next": "..."}},
    {{"intent": "拒绝", "next": "..."}},
    {{"intent": "转介绍", "next": "..."}}
  ]
}}"""
    return SYSTEM, user


def proposal(customer: dict, analysis_result: dict) -> tuple[str, str]:
    user = f"""客户档案：
{_brief(customer)}

客户分析结论：
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}

请写一份一页纸的 TikTok 出海营销服务方案，销售要能拿它讲 30 分钟。

要求：
- 策略必须扣住这家客户的具体情况，不要写成通用模板；
- KPI 必须给目标值和行业参考区间（美区 TikTok 常见量级即可）；
- 报价给三档：试水 / 标准 / 深度；
- 内容矩阵 3-4 个栏目。

输出 JSON：
{{
  "goal": "3 个月目标，含可量化指标",
  "insight": "对客户现状的判断，2-3 句",
  "strategy": "核心打法，3-4 句",
  "content_matrix": [{{"pillar": "栏目名", "angle": "切入角度", "example": "一条具体选题"}}],
  "creator_mix": [{{"tier": "纳米/微型/腰部", "count": 40, "budget": "$4,000"}}],
  "kpi": [{{"metric": "CPM", "target": "$10 以内", "benchmark": "美区 $6-15"}}],
  "pricing": [{{"tier": "试水", "price": "$8k / 月", "scope": "包含什么"}}],
  "timeline": [{{"week": "W1", "deliverable": "..."}}]
}}"""
    return SYSTEM, user


def delivery(customer: dict, proposal_result: dict) -> tuple[str, str]:
    user = f"""客户：{customer.get('name')}
方案：
{json.dumps(proposal_result, ensure_ascii=False, indent=2)}

请把方案拆成可执行任务，并给出一个交付样例。

要求：
- 任务 5-7 条，覆盖达人、内容、投放、落地页、复盘；
- 每条验收标准必须可量化（如"3 秒完播率 ≥ 35%"）；
- 脚本 3 条，每条 15 秒，按 0-2s / 2-8s / 8-12s / 12-15s 分镜。

输出 JSON：
{{
  "tasks": [{{"owner": "达人BD", "due": "W1", "deliverable": "...", "acceptance": "..."}}],
  "scripts": [
    {{"name": "脚本 A", "hook": "0-2s ...", "body": "2-8s ...", "cta": "12-15s ..."}}
  ]
}}"""
    return SYSTEM, user


def review(customer: dict, metrics: dict, kpi: list) -> tuple[str, str]:
    user = f"""客户：{customer.get('name')}

本轮投放数据（已计算）：
{json.dumps(metrics, ensure_ascii=False, indent=2)}

方案设定的 KPI：
{json.dumps(kpi, ensure_ascii=False, indent=2)}

请做数据复盘。

要求：
1. 先判断瓶颈在哪一层：素材层 / 定向层 / 落地页层 / offer 层，只能选一个；
2. 诊断要说明指标之间的因果关系（比如完播低导致 CTR 低，进而推高 CPA）；
3. 下一轮动作 3 条，必须具体到可执行；
4. A/B 测试只改一个变量，并给出假设与观察指标。

输出 JSON：
{{
  "bottleneck": "素材层",
  "diagnosis": "2-3 句，说明因果链",
  "actions": ["3 条下一轮动作"],
  "ab_test": {{"variable": "只改哪个变量", "hypothesis": "预期发生什么", "metric": "看哪个指标"}}
}}"""
    return SYSTEM, user
