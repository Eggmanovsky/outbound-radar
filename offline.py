# -*- coding: utf-8 -*-
"""离线兜底内容。

没有 API key 或调用失败时，界面依然要能完整演示五个环节。
主案例 PawPal 是手写的（质量按真实交付标准），其余客户用模板从档案字段拼装。
"""
from __future__ import annotations

CURATED: dict[str, dict] = {
    "c01": {
        "analysis": {
            "verdict": "现在跟：刚融完 A 轮、在招美国市场经理、还有一条 8.2 万播放的爆款没被放大，典型的“有子弹没枪”。",
            "reasons": [
                "2026 年 8 月完成 $12M A 轮，按行业节奏 Q4 就要拿出增长数据，预算窗口就是现在。",
                "9 月挂出 US Marketing Manager，说明要建海外团队；但招人 2-3 个月，这段空窗期外包是唯一解。",
                "TikTok 号 90 天更了 20 条、单条最高 8.2 万播放，平均却不到 5000——内容有爆点，供给不稳定。",
                "Meta 广告库和 TikTok Creative Center 都查不到在投素材，爆款没有放大的通道。",
            ],
            "risks": [
                "A 轮后通常要求 6 个月内看到增长，方案必须承诺短期可量化的结果。",
                "宠物内容同质化严重，脚本不做差异化会被淹没。",
            ],
            "entry_point": "从“那条 8.2 万播放的猫视频为什么没有第二条”切入，直接谈素材供给与放大。",
        },
        "outreach": {
            "channels": [
                {
                    "name": "LinkedIn 私信",
                    "subject": "",
                    "body": "Kevin 你好，看到 PawPal 那条“猫第一次见到机器人”的视频跑了 8.2 万播放，但后面 20 条平均不到 5 千。内容有爆点，缺的是稳定供给和放大通道。我们帮 3 个 AI 硬件品牌做过同样的冷启动，想聊聊？",
                    "hook_source": "引用自：TikTok 热门视频（8.2 万播放）+ 近 90 天平均播放不足 5000",
                },
                {
                    "name": "冷邮件",
                    "subject": "你们那条 8.2 万播放的猫视频，为什么没有第二条",
                    "body": "Kevin 你好，我是做 TikTok 出海营销的。看 PawPal 的 TikTok，那条猫咪视频有 8.2 万播放、1400 条评论里全是问购买链接的，但后面 20 条平均不到 5 千，也没看到 Spark Ads 在放大。我们把这类“原生爆款”做成可复制的素材流水线，3 个 AI 硬件客户里最快的 4 周把 CPA 压到 30 美元以内。方便约 20 分钟聊聊吗？",
                    "hook_source": "引用自：TikTok 热门视频评论“多为询问购买链接”",
                },
                {
                    "name": "WhatsApp",
                    "subject": "",
                    "body": "Hi Kevin，我是做 TikTok 出海营销的。看到 PawPal 的猫咪视频有 8.2 万播放但没放大，我们做过同类的 AI 硬件冷启动，想跟您聊 15 分钟。",
                    "hook_source": "引用自：TikTok 账号数据",
                },
            ],
            "followups": [
                {"day": "D0", "channel": "LinkedIn", "action": "发送私信，附一条同类案例链接"},
                {"day": "D3", "channel": "邮件", "action": "换角度：发一份 2 页的素材诊断，指出 3 条可复用的爆款结构"},
                {"day": "D7", "channel": "LinkedIn", "action": "在其动态下互动，再补一句“我们算了你们 20 条的完播中位数”"},
                {"day": "D14", "channel": "邮件", "action": "最后一次：给两个具体时间选项，明确 20 分钟通话"},
            ],
            "reply_playbook": [
                {"intent": "有兴趣", "next": "24 小时内约通话，先问月预算、目标市场、现有团队三件事"},
                {"intent": "要资料", "next": "发一页纸方案 + 2 个同类案例，附报价区间"},
                {"intent": "拒绝", "next": "问是否可在季度末再联系，标记 90 天后跟进"},
                {"intent": "转介绍", "next": "请对方指认同行市场负责人，并给一段可直接转发的话"},
            ],
        },
        "proposal": {
            "goal": "3 个月内把美国站月销从约 200 台做到 500 台，ROAS ≥ 7.0。",
            "insight": "PawPal 的内容已经被验证过——问题不在产品表达，而在供给频率和放大能力。现有 20 条视频里出现过 8.2 万播放的爆款，说明钩子有效，但没有系统性地复制。",
            "strategy": "先用达人铺量把素材池做厚，筛出前 10% 的爆款；再用 Spark Ads 集中放大；自有账号承接自然流量，形成“测—放—接”的闭环。",
            "content_matrix": [
                {"pillar": "首次反应", "angle": "宠物第一次接触机器人", "example": "猫第一次见 PawPal 的 10 种反应"},
                {"pillar": "场景剧", "angle": "主人不在家时宠物在做什么", "example": "上班 8 小时，它自己玩了 6 小时"},
                {"pillar": "对比测评", "angle": "高价与廉价玩具的真实差距", "example": "199 美元和 29 美元，猫选哪个"},
                {"pillar": "用户证言", "angle": "真实家庭的 30 天使用反馈", "example": "养两只猫的家庭用了 30 天后"},
            ],
            "creator_mix": [
                {"tier": "纳米（1k-10k）", "count": 40, "budget": "$4,000"},
                {"tier": "微型（10k-50k）", "count": 10, "budget": "$3,500"},
                {"tier": "腰部（50k-500k）", "count": 2, "budget": "$4,000"},
            ],
            "kpi": [
                {"metric": "CPM", "target": "≤ $10", "benchmark": "美区 $6-15"},
                {"metric": "CTR", "target": "≥ 1.2%", "benchmark": "美区 0.8-1.5%"},
                {"metric": "3 秒完播率", "target": "≥ 35%", "benchmark": "美区 30-45%"},
                {"metric": "CPA", "target": "≤ $28", "benchmark": "AI 硬件 $25-45"},
                {"metric": "ROAS", "target": "≥ 7.0", "benchmark": "DTC 硬件 3-8"},
            ],
            "pricing": [
                {"tier": "试水", "price": "$8k / 月", "scope": "20 条达人视频 + 账号代运营 + 基础投放"},
                {"tier": "标准", "price": "$18k / 月", "scope": "50 条达人 + 内容矩阵 + Spark Ads 托管 + 周报"},
                {"tier": "深度", "price": "$35k / 3 个月", "scope": "全案：达人 + 直播测试 + 落地页优化 + 独立数据看板"},
            ],
            "timeline": [
                {"week": "W1", "deliverable": "达人名单与报价确认"},
                {"week": "W2", "deliverable": "首批 12 条素材交付"},
                {"week": "W3", "deliverable": "Spark Ads 起量"},
                {"week": "W4", "deliverable": "首次复盘与下一轮计划"},
            ],
        },
        "delivery": {
            "tasks": [
                {"owner": "达人 BD", "due": "W1", "deliverable": "40 位纳米 + 10 位微型达人名单", "acceptance": "北美占比 ≥ 60%，粉丝 1k-50k，全部含联系方式与历史报价"},
                {"owner": "内容", "due": "W2", "deliverable": "12 条脚本 + 30 条素材", "acceptance": "每条脚本都有 0-2s 钩子，预估 3 秒完播 ≥ 35%"},
                {"owner": "投放", "due": "W3", "deliverable": "Spark Ads 起量", "acceptance": "日预算 $300，CPM ≤ $10，跑满 5 天"},
                {"owner": "设计", "due": "W3", "deliverable": "2 版落地页 A/B", "acceptance": "移动端加载 < 2s，转化率 ≥ 3%"},
                {"owner": "数据", "due": "每周一", "deliverable": "投放周报", "acceptance": "覆盖曝光→转化全链路，含素材排名"},
                {"owner": "客户成功", "due": "W4", "deliverable": "首次复盘会", "acceptance": "输出 3 条下一轮动作 + 1 个 A/B 假设"},
            ],
            "scripts": [
                {"name": "脚本 A · 猫咪第一次见", "hook": "0-2s 猫咪耳朵竖起、脸凑近镜头", "body": "2-8s 机器人主动靠近并发声，猫后退半步又凑回来", "cta": "12-15s 你家猫会怎样？链接在主页"},
                {"name": "脚本 B · 上班 8 小时", "hook": "0-2s 门关上，屋里只剩猫和机器人", "body": "2-8s 机器人自己走动、发声，猫跟着它转", "cta": "12-15s 上班时，它替你陪猫"},
                {"name": "脚本 C · 199 和 29 的差距", "hook": "0-2s 两个玩具并排，价格直接打在画面上", "body": "2-8s 猫分别玩 10 秒，第 8 秒它走向贵的那个", "cta": "12-15s 贵 170 美元，猫替你做选择"},
            ],
        },
        "review": {
            "bottleneck": "素材层",
            "diagnosis": "3 秒完播 22%，比 35% 的基准低 13 个点，说明前 2 秒没抓住人；完播低直接拉低 CTR 到 0.9%，CPC 被推到 $1.11，CPA 因此停在 $41，比目标高 46%。CPM 与转化率基本达标，问题不在定向和落地页。",
            "actions": [
                "把前 2 秒全部重做：3 个钩子版本（宠物反应特写 / 价格对比 / 悬念提问），每条素材只换开头。",
                "把 10 月播放前 3 的视频拆成结构模板，交给纳米达人批量复制，保证下周起每天至少 2 条新素材。",
                "CPA 超 $35 的素材立即停投，预算集中到 CTR > 1.2% 的 3 条上。",
            ],
            "ab_test": {
                "variable": "只改前 2 秒钩子",
                "hypothesis": "宠物反应特写比价格对比更能拉住前 3 秒，3 秒完播可提升到 32% 以上",
                "metric": "3 秒完播率",
            },
        },
    }
}


def _first_signal(customer: dict, index: int = 0) -> str:
    signals = customer.get("signals") or ["暂无公开信号"]
    return signals[min(index, len(signals) - 1)]


def analysis(customer: dict) -> dict:
    curated = CURATED.get(customer["id"], {}).get("analysis")
    if curated:
        return curated
    return {
        "verdict": f"可以跟：{customer.get('one_liner', '')}，已有初步出海动作，但内容供给不足。",
        "reasons": [_first_signal(customer, i) for i in range(min(3, len(customer.get("signals") or [])))],
        "risks": customer.get("risk", [])[:2] or ["需要先确认预算与决策链。"],
        "entry_point": "从对方最近一次公开动作切入，先给判断再谈服务。",
    }


def outreach(customer: dict, analysis_result: dict) -> dict:
    curated = CURATED.get(customer["id"], {}).get("outreach")
    if curated:
        return curated
    name = customer.get("name", "客户")
    dm = (customer.get("dm") or {}).get("name", "您好")
    return {
        "channels": [
            {
                "name": "LinkedIn 私信",
                "subject": "",
                "body": f"{dm}你好，看到{_first_signal(customer)}。我们帮 AI 硬件品牌做过同类冷启动，想聊 15 分钟？",
                "hook_source": f"引用自：{_first_signal(customer)}",
            },
            {
                "name": "冷邮件",
                "subject": f"{name} 出海内容的一个具体问题",
                "body": f"{dm}你好，观察到{_first_signal(customer)}。这和我们在同类客户身上看到的模式一样：内容有起色，但供给不稳定、缺少放大。方便约 20 分钟吗？",
                "hook_source": f"引用自：{_first_signal(customer)}",
            },
            {
                "name": "WhatsApp",
                "subject": "",
                "body": f"{dm} 你好，我是做 TikTok 出海营销的，看到{_first_signal(customer)}，想约 15 分钟聊一下。",
                "hook_source": f"引用自：{_first_signal(customer)}",
            },
        ],
        "followups": [
            {"day": "D0", "channel": "LinkedIn", "action": "发送私信 + 一条同类案例"},
            {"day": "D3", "channel": "邮件", "action": "补一份内容诊断，给 3 条可执行建议"},
            {"day": "D7", "channel": "LinkedIn", "action": "互动其动态，再提一次具体数据"},
            {"day": "D14", "channel": "邮件", "action": "给出两个具体时间选项，收尾"},
        ],
        "reply_playbook": [
            {"intent": "有兴趣", "next": "24 小时内约通话，问预算、市场、团队"},
            {"intent": "要资料", "next": "发一页纸方案 + 案例"},
            {"intent": "拒绝", "next": "约季度末再联系"},
            {"intent": "转介绍", "next": "请对方指认同行负责人"},
        ],
    }


def proposal(customer: dict, analysis_result: dict) -> dict:
    curated = CURATED.get(customer["id"], {}).get("proposal")
    if curated:
        return curated
    return {
        "goal": "3 个月内跑通美国市场冷启动，ROAS ≥ 3.5。",
        "insight": f"{customer.get('one_liner', '')}产品本身有卖点，缺的是稳定的内容供给与放大能力。",
        "strategy": "达人铺量建立素材池 → 筛出爆款 → Spark Ads 放大 → 自有账号承接。",
        "content_matrix": [
            {"pillar": "开箱", "angle": "第一次使用", "example": "开箱 + 首次体验"},
            {"pillar": "场景", "angle": "真实使用场景", "example": "一天中的三个使用时刻"},
            {"pillar": "对比", "angle": "同类产品对比", "example": "和竞品的三个差别"},
        ],
        "creator_mix": [
            {"tier": "纳米", "count": 30, "budget": "$3,000"},
            {"tier": "微型", "count": 8, "budget": "$2,800"},
        ],
        "kpi": [
            {"metric": "CPM", "target": "≤ $10", "benchmark": "美区 $6-15"},
            {"metric": "CTR", "target": "≥ 1.2%", "benchmark": "美区 0.8-1.5%"},
            {"metric": "CPA", "target": "按客单价定", "benchmark": "硬件 $25-45"},
            {"metric": "ROAS", "target": "≥ 3.5", "benchmark": "DTC 3-8"},
        ],
        "pricing": [
            {"tier": "试水", "price": "$8k / 月", "scope": "达人 + 代运营"},
            {"tier": "标准", "price": "$18k / 月", "scope": "达人 + 内容 + 投放托管"},
            {"tier": "深度", "price": "$35k / 3 个月", "scope": "全案 + 数据看板"},
        ],
        "timeline": [
            {"week": "W1", "deliverable": "达人名单"},
            {"week": "W2", "deliverable": "首批素材"},
            {"week": "W3", "deliverable": "投放起量"},
            {"week": "W4", "deliverable": "首次复盘"},
        ],
    }


def delivery(customer: dict, proposal_result: dict) -> dict:
    curated = CURATED.get(customer["id"], {}).get("delivery")
    if curated:
        return curated
    return {
        "tasks": [
            {"owner": "达人 BD", "due": "W1", "deliverable": "30 位达人名单", "acceptance": "北美占比 ≥ 60%"},
            {"owner": "内容", "due": "W2", "deliverable": "10 条脚本 + 20 条素材", "acceptance": "3 秒完播预估 ≥ 35%"},
            {"owner": "投放", "due": "W3", "deliverable": "Spark Ads 起量", "acceptance": "日预算 $200，CPM ≤ $10"},
            {"owner": "数据", "due": "每周一", "deliverable": "周报", "acceptance": "覆盖全链路"},
        ],
        "scripts": [
            {"name": "脚本 A", "hook": "0-2s 产品首次出现", "body": "2-8s 核心功能演示", "cta": "12-15s 点击链接"},
            {"name": "脚本 B", "hook": "0-2s 痛点场景", "body": "2-8s 产品解决问题", "cta": "12-15s 点击链接"},
            {"name": "脚本 C", "hook": "0-2s 对比画面", "body": "2-8s 差异展示", "cta": "12-15s 点击链接"},
        ],
    }


def review(customer: dict, metrics: dict, kpi: list) -> dict:
    curated = CURATED.get(customer["id"], {}).get("review")
    if curated:
        return curated
    return {
        "bottleneck": "素材层",
        "diagnosis": f"当前 CTR {metrics['ctr']}%，CPA ${metrics['cpa']}，与目标仍有差距，主要卡在素材吸引力上。",
        "actions": ["重做前 2 秒钩子", "停投高 CPA 素材", "补充达人素材供给"],
        "ab_test": {"variable": "前 2 秒钩子", "hypothesis": "更强钩子可提升完播与点击", "metric": "3 秒完播率"},
    }
