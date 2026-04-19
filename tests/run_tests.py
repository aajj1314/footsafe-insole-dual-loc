# -*- coding: utf-8 -*-
"""
测试报告生成脚本
运行所有测试并生成报告
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"


def run_tests(test_path: str = None, verbose: bool = True) -> dict:
    """
    运行测试

    Args:
        test_path: 测试文件路径, None表示运行所有测试
        verbose: 是否详细输出

    Returns:
        测试结果字典
    """
    cmd = [
        sys.executable, "-m", "pytest",
        str(TESTS_DIR),
        "-v" if verbose else "",
        "--tb=short",
        "--color=yes",
    ]

    if test_path:
        cmd.append(test_path)

    # 移除空字符串
    cmd = [c for c in cmd if c]

    print(f"Running command: {' '.join(cmd)}")
    print("=" * 80)

    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def generate_report(test_results: dict) -> str:
    """
    生成测试报告

    Args:
        test_results: 测试结果字典

    Returns:
        报告字符串
    """
    report = []
    report.append("=" * 80)
    report.append("足安智能防走失系统 API接口测试报告")
    report.append("=" * 80)
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # 测试执行状态
    if test_results["returncode"] == 0:
        report.append("测试状态: 通过 (PASSED)")
    else:
        report.append("测试状态: 失败 (FAILED)")

    report.append("")
    report.append("-" * 80)
    report.append("测试输出")
    report.append("-" * 80)
    report.append(test_results["stdout"])

    if test_results["stderr"]:
        report.append("")
        report.append("错误输出:")
        report.append(test_results["stderr"])

    report.append("")
    report.append("=" * 80)
    report.append("报告结束")
    report.append("=" * 80)

    return "\n".join(report)


def main():
    """主函数"""
    print("开始运行足安智能防走失系统API接口测试...")
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"测试目录: {TESTS_DIR}")
    print("")

    # 运行所有测试
    results = run_tests()

    # 生成报告
    report = generate_report(results)

    # 输出报告
    print(report)

    # 保存报告到文件
    report_file = PROJECT_ROOT / "test_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n报告已保存到: {report_file}")

    return results["returncode"]


if __name__ == "__main__":
    sys.exit(main())
