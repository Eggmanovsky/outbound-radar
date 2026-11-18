# -*- coding: utf-8 -*-
"""无浏览器冒烟测试：用 Streamlit 官方 AppTest 真跑一遍五个步骤。

覆盖：初始渲染、每一步的生成按钮、切换客户后的离线兜底路径。
运行：python smoke_test.py
"""
from __future__ import annotations

import pathlib
import sys

from streamlit.testing.v1 import AppTest

APP = str(pathlib.Path(__file__).with_name("app.py"))


def check(at: AppTest, where: str) -> None:
    if at.exception:
        for e in at.exception:
            print(f"[FAIL] {where}: {e.message}")
            print(e.stack_trace)
        sys.exit(1)
    print(f"[ok] {where}")


def main() -> None:
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    check(at, "初始渲染")

    at.button(key="btn_analysis").click().run()
    check(at, "步骤1 生成判断")
    assert "analysis:c01" in at.session_state["results"], "分析结果未写入"

    for idx, (key, label) in enumerate(
        [("btn_outreach", "步骤2"), ("btn_proposal", "步骤3"), ("btn_delivery", "步骤4"), ("btn_review", "步骤5")],
        start=1,
    ):
        at.session_state["step_idx"] = idx
        at.run()
        check(at, f"{label} 渲染")
        at.button(key=key).click().run()
        check(at, f"{label} 生成")

    # 切到一个红牌客户，验证通用兜底路径
    at.session_state["cid"] = "c08"
    for idx in range(5):
        at.session_state["step_idx"] = idx
        at.run()
        check(at, f"红牌客户步骤{idx + 1} 渲染")

    at.session_state["cid"] = "c03"
    at.session_state["step_idx"] = 0
    at.run()
    check(at, "切回高风险客户渲染")

    print("\n全部通过")


if __name__ == "__main__":
    main()
