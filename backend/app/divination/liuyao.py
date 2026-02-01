from __future__ import annotations

import hashlib
import random
from typing import Dict, List


TRIGRAMS = {
    "111": "乾",
    "000": "坤",
    "001": "震",
    "010": "坎",
    "011": "艮",
    "100": "巽",
    "101": "离",
    "110": "兑",
}


def cast_liuyao(question: str, seed_key: str = "") -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    rng = random.Random(_seed(question, seed_key, "liuyao"))

    lines = []
    yang_count = 0
    for index in range(6):
        value = "yang" if rng.random() > 0.45 else "yin"
        if value == "yang":
            yang_count += 1
        lines.append({"line": index + 1, "value": value})

    lower_code = _line_code(lines[:3])
    upper_code = _line_code(lines[3:])
    lower = TRIGRAMS.get(lower_code, "未知")
    upper = TRIGRAMS.get(upper_code, "未知")

    verdict = _build_verdict(yang_count, upper, lower)
    advice = _build_advice(yang_count)

    symbols = {
        "upper": upper,
        "lower": lower,
        "lines": lines,
        "pattern": f"上{upper}下{lower}",
    }

    return {"symbols": symbols, "verdict": verdict, "advice": advice}


def _line_code(lines: List[Dict[str, str]]) -> str:
    return "".join("1" if line["value"] == "yang" else "0" for line in lines)


def _build_verdict(yang_count: int, upper: str, lower: str) -> str:
    if yang_count >= 4:
        return f"卦象为上{upper}下{lower}，行动力强，适合主动推进。"
    if yang_count == 3:
        return f"卦象为上{upper}下{lower}，局势平衡，适合稳步试探。"
    return f"卦象为上{upper}下{lower}，宜先守后动，等待时机明朗。"


def _build_advice(yang_count: int) -> List[str]:
    if yang_count >= 4:
        return ["设定明确节点并推进", "优先解决最关键的变量", "保持节奏，不要摇摆"]
    if yang_count == 3:
        return ["先小步验证，再扩大投入", "与关键人保持同步", "别急于一锤定音"]
    return ["先稳住基本面", "避免被外部噪音影响", "等待下一次明确机会"]


def _seed(question: str, seed_key: str, namespace: str) -> int:
    payload = f"{namespace}:{seed_key}:{question}".encode("utf-8")
    return int(hashlib.sha256(payload).hexdigest(), 16)
