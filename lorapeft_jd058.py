"""lorapeft_jd058 —— 用规则在LoRA 与参数高效微调研究员·投机解码的命中率里定位可疑位置。

用一组明示的正则规则扫描输入，报告LoRA 与参数高效微调研究员·投机解码的命中率相关的命中行与片段

定位：
  规则表公开可读，每条命中都能对应到一条明示的规则

岗位对应：
  目标岗位　华为 · 初级LoRA 与参数高效微调研究员
  技能主线　大模型微调、PyTorch、预训练
  领域标签　大模型训练

设计约束：
  1. **只报告能定位到具体位置的结论**，不做语义猜测。
  2. **规则表公开**，每条命中都能对应到岗位要求的一条明示规则。
  3. **输入为空或格式不对时明确报错**，不静默返回空结果。

仅依赖 Python 标准库。

用法:
    python lorapeft_jd058.py --help
    python lorapeft_jd058.py --file input.txt
    python lorapeft_jd058.py --text "示例内容"
    python lorapeft_jd058.py --file input.txt --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# 岗位规则表：每条规则独立可核查，命中即报，不做推断。
# 规则由岗位 JD 的技能线与领域标签派生——每条都能对回岗位要求。
# 目标岗位：华为 · 初级LoRA 与参数高效微调研究员
RULES: list[dict] = [
    {
        "name": "LoRA 与参数高效微调研究员·投机解码的命中率·缺失",
        "why": "岗位要求「大模型微调」在输入里找不到对应内容",
        "severity": "high",
        "keywords": ['missing', 'absent', '缺少', '没有', '未提供', '大模型微调'],
    },
    {
        "name": "LoRA 与参数高效微调研究员·投机解码的命中率·冲突",
        "why": "两处关于「PyTorch」的描述互相矛盾",
        "severity": "high",
        "keywords": ['conflict', 'contradict', '矛盾', '不一致', '相反', 'PyTorch'],
    },
    {
        "name": "LoRA 与参数高效微调研究员·投机解码的命中率·越界",
        "why": "「预训练」的取值超出岗位场景的常规范围",
        "severity": "medium",
        "keywords": ['out of range', 'outlier', '越界', '超限', '超过', '预训练'],
    },
    {
        "name": "LoRA 与参数高效微调研究员·投机解码的命中率·退化",
        "why": "「大模型训练」相关的信息量不足以支撑判断",
        "severity": "medium",
        "keywords": ['degrade', 'insufficient', '不足', '太少', '无法', '大模型训练'],
    },
    {
        "name": "LoRA 与参数高效微调研究员·投机解码的命中率·泄漏",
        "why": "「LoRA 与参数高效微调研究员」相关的内容被意外暴露",
        "severity": "high",
        "keywords": ['leak', 'expose', '泄漏', '暴露', '明文', 'LoRA 与参数高效微调研究员'],
    },
    {
        "name": "LoRA 与参数高效微调研究员·投机解码的命中率·重复#2",
        "why": "同一处「大模型微调」信息被反复传递",
        "severity": "low",
        "keywords": ['duplicate', 'repeat', '重复', 'again', '大模型微调'],
    },
    {
        "name": "LoRA 与参数高效微调研究员·投机解码的命中率·陈旧#2",
        "why": "「PyTorch」的时效性已过期",
        "severity": "medium",
        "keywords": ['stale', 'expired', '过期', '陈旧', '旧版', 'PyTorch'],
    },
    {
        "name": "LoRA 与参数高效微调研究员·投机解码的命中率·不可核#2",
        "why": "关于「预训练」的说法无法追溯到具体证据",
        "severity": "high",
        "keywords": ['unverifiable', 'no evidence', '无法追溯', '没有来源', '预训练'],
    },
]

# 定位规则：(名称, 正则, 说明)
LOCATOR_RULES: list[tuple[str, str, str]] = [('LoRA 与参数高效微调研究员·投机解码的命中率·标注缺失', '\\b(todo|tbd|fixme|xxx)\\b', '占位符未替换'), ('LoRA 与参数高效微调研究员·投机解码的命中率·硬编码', '(password|secret|api[_-]?key)\\s*[=:]\\s*[\\"\'][^\\"\']+', '疑似硬编码密钥'), ('LoRA 与参数高效微调研究员·投机解码的命中率·调试残留', '(print\\(|console\\.log|breakpoint\\(\\))', '调试残留'), ('LoRA 与参数高效微调研究员·投机解码的命中率·注释占位', '#\\s*(TODO|FIXME|待补|待定)\\b', '注释里留了待办')]



# 定位规则：(名称, 已编译正则, 说明)
# 正则在这里就编译好——如果留成字符串，每次分析都要重新 compile，
# 而 analyze 里直接调 rx.finditer 就会 AttributeError。
LOCATOR_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    (name, re.compile(pat, re.I), why) for name, pat, why in LOCATOR_RULES
]


def lorapeft_jd058_locate(text: str) -> list[dict]:
    """定位所有规则命中。"""
    out: list[dict] = []
    for name, rx, _ in LOCATOR_PATTERNS:
        for m in rx.finditer(text):
            out.append({
                "rule": name,
                "start": m.start(),
                "end": m.end(),
                "snippet": m.group(0)[:100],
            })
    out.sort(key=lambda d: d["start"])
    return out


def lorapeft_jd058_analyze(text: str) -> dict:
    """主分析：违规位置与行号。"""
    hits = lorapeft_jd058_locate(text)
    lines = text.splitlines()
    for h in hits:
        h["line"] = text.count("\n", 0, h["start"]) + 1
        h["line_text"] = lines[h["line"] - 1].strip()[:120] if h["line"] <= len(lines) else ""
    by_rule: dict[str, int] = {}
    for h in hits:
        by_rule[h["rule"]] = by_rule.get(h["rule"], 0) + 1
    return {
        "line_count": len(lines),
        "hits": hits,
        "hit_count": len(hits),
        "by_rule": by_rule,
        "clean": not hits,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def render(result: dict) -> str:
    """把结果渲染成人读的文本。每个工具的版式不同。"""
    out: list[str] = []
    if not result.get("ok", True):
        out.append(f"无法分析：{{result.get('error', '未知原因')}}")
        return "\n".join(out)
    out.append(f"行数：{result['line_count']}  命中：{result['hit_count']}")
    out.append("")
    for h in result["hits"]:
        out.append(f"  第 {h['line']} 行  [{h['rule']}]  {h['snippet']!r}")
    if result["clean"]:
        out.append("没有命中任何规则。")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="lorapeft_jd058",
        description="用一组明示的正则规则扫描输入，报告LoRA 与参数高效微调研究员·投机解码的命中率相关的命中行与片段（仅依赖标准库）",
        epilog=(
            "示例:\n"
            "  python lorapeft_jd058.py --file input.txt\n"
            "  python lorapeft_jd058.py --text '示例内容'\n"
            "  python lorapeft_jd058.py --file input.txt --json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="输入文件路径")
    src.add_argument("--text", help="直接给出输入内容")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"读不了文件：{{e}}", file=sys.stderr)
            return 2
    else:
        content = args.text

    if not content.strip():
        print("输入是空的。", file=sys.stderr)
        return 2

    result = lorapeft_jd058_analyze(content)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(render(result))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
