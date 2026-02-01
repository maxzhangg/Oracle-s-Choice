from __future__ import annotations

import hashlib
import random
from typing import Dict, List


MAJOR_ARCANA = [
    ("愚者", "开启新的旅程"),
    ("魔术师", "掌控与行动"),
    ("女祭司", "直觉与内省"),
    ("女皇", "滋养与成长"),
    ("皇帝", "结构与规则"),
    ("教皇", "传统与承诺"),
    ("恋人", "关系与选择"),
    ("战车", "推进与胜利"),
    ("力量", "温柔的坚定"),
    ("隐者", "独处与思考"),
    ("命运之轮", "变化与机遇"),
    ("正义", "公平与平衡"),
    ("倒吊人", "暂停与换角度"),
    ("死神", "结束与重启"),
    ("节制", "调和与耐心"),
    ("恶魔", "执念与束缚"),
    ("高塔", "突发与重构"),
    ("星星", "希望与指引"),
    ("月亮", "迷雾与情绪"),
    ("太阳", "清晰与喜悦"),
    ("审判", "觉醒与决定"),
    ("世界", "完成与收束"),
]

POSITIONS = ["过去", "现在", "未来"]


def draw_tarot(question: str, seed_key: str = "") -> Dict[str, List[Dict[str, str]]]:
    rng = random.Random(_seed(question, seed_key, "tarot"))
    cards = rng.sample(MAJOR_ARCANA, 3)

    symbols = []
    for index, (name, meaning) in enumerate(cards):
        orientation = "正位" if rng.random() > 0.3 else "逆位"
        symbols.append(
            {
                "name": name,
                "meaning": meaning,
                "position": POSITIONS[index],
                "orientation": orientation,
            }
        )

    positive = sum(1 for item in symbols if item["orientation"] == "正位")
    if positive >= 2:
        verdict = "整体走向偏积极，只要稳住节奏就能看到进展。"
    elif positive == 1:
        verdict = "局势有起伏，关键在于当下的取舍。"
    else:
        verdict = "阻力偏多，建议先整理情绪与边界。"

    advice = _build_advice(symbols)

    return {"symbols": symbols, "verdict": verdict, "advice": advice}


def _build_advice(symbols: List[Dict[str, str]]) -> List[str]:
    advice = []
    for item in symbols:
        if item["orientation"] == "逆位":
            advice.append(f"留意{item['name']}所示的失衡点")
        else:
            advice.append(f"抓住{item['name']}带来的推进力")

    advice.append("给自己留一个可调整的时间窗口")
    return advice[:3]


def _seed(question: str, seed_key: str, namespace: str) -> int:
    payload = f"{namespace}:{seed_key}:{question}".encode("utf-8")
    return int(hashlib.sha256(payload).hexdigest(), 16)
