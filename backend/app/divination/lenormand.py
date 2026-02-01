from __future__ import annotations

import hashlib
import random
from typing import Dict, List


LENORMAND_CARDS = [
    ("骑士", "消息与行动"),
    ("三叶草", "小确幸"),
    ("船", "旅程与变化"),
    ("房屋", "基础与安全"),
    ("树", "成长与健康"),
    ("云", "不确定"),
    ("蛇", "复杂与试探"),
    ("棺材", "结束与转化"),
    ("花束", "惊喜与友好"),
    ("镰刀", "快速切换"),
    ("鞭子", "压力与反复"),
    ("鸟", "沟通与焦虑"),
    ("孩子", "新开始"),
    ("狐狸", "策略与谨慎"),
    ("熊", "资源与掌控"),
    ("星星", "方向与愿景"),
    ("鹳", "改变与搬迁"),
    ("狗", "信任与伙伴"),
    ("塔", "边界与制度"),
    ("花园", "社交与公开"),
    ("山", "阻碍"),
    ("道路", "选择"),
    ("老鼠", "消耗"),
    ("心", "情感"),
    ("戒指", "承诺"),
    ("书", "隐情"),
    ("信", "信息"),
    ("男人", "男性能量"),
    ("女人", "女性能量"),
    ("百合", "和谐"),
    ("太阳", "成功"),
    ("月亮", "名誉与情绪"),
    ("钥匙", "答案"),
    ("鱼", "财富与流动"),
    ("锚", "稳定"),
    ("十字", "责任"),
]


def draw_lenormand(question: str, seed_key: str = "") -> Dict[str, List[Dict[str, str]]]:
    rng = random.Random(_seed(question, seed_key, "lenormand"))
    cards = rng.sample(LENORMAND_CARDS, 3)

    symbols = [
        {"name": name, "meaning": meaning, "position": position}
        for position, (name, meaning) in zip(["起因", "过程", "结果"], cards)
    ]

    verdict = _compose_verdict(cards)
    advice = [
        "聚焦最能带来结果的动作",
        "避免被情绪牵着走",
        "给出明确的选择与时间点",
    ]

    return {"symbols": symbols, "verdict": verdict, "advice": advice}


def _compose_verdict(cards: List[tuple]) -> str:
    keywords = "、".join(card[0] for card in cards)
    if any(card[0] in {"太阳", "钥匙", "鱼"} for card in cards):
        return f"牌面显示{keywords}，结果倾向打开局面。"
    if any(card[0] in {"山", "十字", "云"} for card in cards):
        return f"牌面显示{keywords}，需要面对现实阻力。"
    return f"牌面显示{keywords}，节奏取决于你的下一步行动。"


def _seed(question: str, seed_key: str, namespace: str) -> int:
    payload = f"{namespace}:{seed_key}:{question}".encode("utf-8")
    return int(hashlib.sha256(payload).hexdigest(), 16)
