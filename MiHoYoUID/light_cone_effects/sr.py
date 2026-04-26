from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Tuple

EffectValues = Tuple[float, float, float, float, float]
EffectDef = Dict[str, Any]


def _step(start: float, step: float | None = None) -> EffectValues:
    if step is None:
        step = start / 4
    return tuple(start + step * idx for idx in range(5))  # type: ignore[return-value]


def _fmt_num(value: Any) -> str:
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(num - round(num)) < 0.01:
        return str(int(round(num)))
    return f"{num:.1f}".rstrip("0").rstrip(".")


def _norm_name(name: str) -> str:
    return re.sub(r"[\s·•・,，。.!！?？:：;；'‘’\"“”【】\[\]（）()《》<>「」-]", "", str(name or "")).lower()


def _pick(values: Iterable[Any], refine: int) -> Any:
    arr = list(values)
    if not arr:
        return ""
    idx = max(1, min(int(refine or 1), 5)) - 1
    return arr[min(idx, len(arr) - 1)]


def _render(template: str, values: Dict[str, Iterable[Any]], refine: int) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            return match.group(0)
        return _fmt_num(_pick(values[key], refine))

    return re.sub(r"\{([A-Za-z0-9_]+)\}", repl, template)


# 参考 miao-plugin resources/meta-sr/weapon/*/calc.js：以模板 + 叠影 1-5 数值表保存，便于后续继续补全。
# 数值以常见光锥效果为准；如果面板源本身提供 desc/effect，会优先使用面板源文本。
LIGHT_CONE_EFFECTS: Dict[str, EffectDef] = {
    # 虚无
    "行于流逝的岸": {
        "template": "暴击伤害提高{cdmg}%；使敌方陷入泡影后，装备者造成的伤害提高{dmg}%，终结技伤害额外提高{qDmg}%。",
        "values": {"cdmg": _step(36), "dmg": _step(24), "qDmg": _step(24)},
        "aliases": ("行于流逝", "流逝的岸", "黄泉专武"),
    },
    "无边曼舞": {
        "template": "暴击率提高{cpct}%；对处于防御降低或减速状态下的敌方目标，暴击伤害提高{cdmg}%。",
        "values": {"cpct": _step(8), "cdmg": _step(24)},
        "aliases": ("无边慢舞",),
    },
    "雨一直下": {
        "template": "效果命中提高{effPct}%；装备者对带有以太编码的目标造成的伤害提高{dmg}%。",
        "values": {"effPct": _step(24), "dmg": _step(12)},
        "aliases": ("银狼专武",),
    },
    "只需等待": {
        "template": "造成的伤害提高{dmg}%；释放攻击后速度提高，最多叠加3层。",
        "values": {"dmg": _step(24)},
        "aliases": ("卡芙卡专武",),
    },
    "决心如汗珠般闪耀": {
        "template": "命中敌方目标时有概率使其陷入攻陷状态，防御力降低{enemyDef}%。",
        "values": {"enemyDef": _step(12)},
        "aliases": ("决心", "汗珠"),
    },
    "晚安与睡颜": {
        "template": "敌方目标每承受1个负面状态，装备者对其造成的伤害提高{dmg}%，最多叠加3层。",
        "values": {"dmg": _step(12)},
        "aliases": ("晚安", "睡颜"),
    },
    "猎物的视线": {
        "template": "效果命中提高{effPct}%，造成的持续伤害提高{dotDmg}%。",
        "values": {"effPct": _step(20), "dotDmg": _step(24)},
        "aliases": ("猎物",),
    },

    # 同谐
    "夜色流光溢彩": {
        "template": "5层【歌咏】使装备者能量恢复效率提高{recharge}%；释放终结技后，装备者攻击力提高{atkPct}%，我方全体造成伤害提高{dmg}%。",
        "values": {"recharge": (15, 17.5, 20, 22.5, 25), "atkPct": _step(48), "dmg": _step(24)},
        "aliases": ("夜色流光", "流光溢彩", "知更鸟专武"),
    },
    "但战斗还未结束": {
        "template": "能量恢复效率提高{recharge}%；施放终结技后恢复战技点，战技后下一名我方目标造成伤害提高。",
        "values": {"recharge": _step(10)},
        "aliases": ("鸭鸭专武", "布洛妮娅专武"),
    },
    "镜中故我": {
        "template": "击破特攻提高{stance}%；施放终结技后我方全体造成伤害提高并恢复战技点。",
        "values": {"stance": _step(60)},
        "aliases": ("镜中顾我", "阮梅专武"),
    },
    "芳华待灼": {
        "template": "攻击力提高{atkPct}%；队伍中有两名及以上相同命途角色时，暴击伤害提高{cdmg}%。",
        "values": {"atkPct": _step(16), "cdmg": _step(16)},
        "aliases": (),
    },
    "回到大地的飞行": {
        "template": "能量恢复效率提高；施放终结技后，使我方目标造成伤害提高并恢复能量。",
        "values": {},
        "aliases": ("回到大地飞行", "回到大地", "星期日专武"),
    },
    "舞！舞！舞！": {
        "template": "装备者施放终结技后，我方全体行动提前。",
        "values": {},
        "aliases": ("舞舞舞",),
    },
    "过往未来": {
        "template": "施放战技后，下一名行动的我方目标造成的伤害提高{dmg}%。",
        "values": {"dmg": _step(16)},
        "aliases": (),
    },

    # 毁灭
    "比阳光更明亮的": {
        "template": "暴击率提高{cpct}%；获得2层【龙吟】后攻击力提高{atkPct}%，能量恢复效率提高{recharge}%。",
        "values": {"cpct": _step(18), "atkPct": (36, 42, 48, 54, 60), "recharge": (12, 14, 16, 18, 20)},
        "aliases": ("比阳光更明亮", "饮月专武"),
    },
    "此身为剑": {
        "template": "暴击伤害提高{cdmg}%；叠满月蚀后下一次攻击造成的伤害提高{dmg}%，并无视目标{ignore}%防御力。",
        "values": {"cdmg": _step(20), "dmg": (42, 49, 56, 63, 70), "ignore": _step(12)},
        "aliases": ("镜流专武",),
    },
    "无可取代的东西": {
        "template": "攻击力提高{atkPct}%；消灭敌方或受到攻击后回复生命，并使造成的伤害提高{dmg}%。",
        "values": {"atkPct": _step(24), "dmg": _step(24)},
        "aliases": ("无可取代东西", "克拉拉专武"),
    },
    "记一位星神的陨落": {
        "template": "攻击命中后攻击力提高，可叠加4层；击破敌方弱点后造成的伤害提高。",
        "values": {},
        "aliases": ("星神的陨落", "星神陨落"),
    },
    "秘密誓心": {
        "template": "造成的伤害提高{dmg}%；对生命百分比不低于自身的敌方目标额外提高{dmg2}%。",
        "values": {"dmg": _step(20), "dmg2": _step(20)},
        "aliases": ("秘密",),
    },
    "梦应归于何处": {
        "template": "击破特攻提高；造成击破伤害后使敌方陷入溃败，受到的击破伤害提高，速度降低。",
        "values": {},
        "aliases": ("流萤专武",),
    },
    "铭记于心的约定": {
        "template": "击破特攻提高{stance}%；施放终结技后暴击率提高{cpct}%。",
        "values": {"stance": _step(28), "cpct": _step(15)},
        "aliases": ("铭记于心",),
    },

    # 巡猎
    "于夜色中": {
        "template": "暴击率提高{cpct}%；速度超过100后，普攻/战技伤害与终结技暴击伤害随速度提高。",
        "values": {"cpct": _step(18)},
        "aliases": ("夜色中", "希儿专武"),
    },
    "星海巡航": {
        "template": "暴击率提高{cpct}%；对生命值低于50%的敌方目标暴击率额外提高，消灭目标后攻击力提高{atkPct}%。",
        "values": {"cpct": _step(8), "atkPct": _step(20)},
        "aliases": ("星海", "巡航"),
    },
    "纯粹思维的洗礼": {
        "template": "暴击伤害提高；敌方每有1个负面效果，装备者对其造成的暴击伤害额外提高；终结技后追加攻击无视防御。",
        "values": {},
        "aliases": ("纯粹思维", "真理医生专武"),
    },
    "烦恼着，幸福着": {
        "template": "暴击率提高{cpct}%；追加攻击伤害提高，并使目标陷入温驯状态，受到追加攻击暴击伤害提高。",
        "values": {"cpct": _step(18)},
        "aliases": ("烦恼着幸福着", "托帕专武"),
    },
    "驶向第二次生命": {
        "template": "击破特攻提高{stance}%；造成的击破伤害无视目标{breakIgnore}%防御力，击破特攻达标后速度提高。",
        "values": {"stance": _step(60), "breakIgnore": _step(20)},
        "aliases": ("驶向二次生命", "第二次生命", "波提欧专武"),
    },
    "论剑": {
        "template": "多次命中同一敌方目标时，每层使造成的伤害提高{dmg}%，最多叠加5层。",
        "values": {"dmg": _step(8)},
        "aliases": (),
    },
    "唯有沉默": {
        "template": "攻击力提高{atkPct}%；场上敌方目标小于等于2时，暴击率提高{cpct}%。",
        "values": {"atkPct": _step(16), "cpct": _step(12)},
        "aliases": (),
    },

    # 智识
    "拂晓之前": {
        "template": "暴击伤害提高{cdmg}%；战技和终结技伤害提高，施放战技或终结技后追加攻击伤害提高。",
        "values": {"cdmg": _step(36)},
        "aliases": ("景元专武",),
    },
    "偏偏希望无价": {
        "template": "暴击率提高{cpct}%；基于暴击伤害提高追加攻击伤害，终结技或追加攻击无视目标防御。",
        "values": {"cpct": _step(16)},
        "aliases": ("翡翠专武",),
    },
    "不息的演算": {
        "template": "攻击力提高{atkPct}%；攻击后每命中1个敌方目标额外提高攻击力，命中数达标时速度提高。",
        "values": {"atkPct": _step(8)},
        "aliases": (),
    },
    "生命当付之一炬": {
        "template": "装备者对目标造成的伤害提高{dmg}%，并使目标防御力降低{enemyDef}%。",
        "values": {"dmg": _step(12), "enemyDef": _step(6)},
        "aliases": ("生命付之一炬", "付之一炬", "那刻夏专武"),
    },
    "别让世界静下来": {
        "template": "进入战斗时恢复能量，终结技造成的伤害提高{qDmg}%。",
        "values": {"qDmg": _step(32)},
        "aliases": ("别让世界静下",),
    },

    # 存护
    "制胜的瞬间": {
        "template": "防御力提高{defPct}%，效果命中提高；受到攻击时防御力额外提高{defPct2}%。",
        "values": {"defPct": _step(24), "defPct2": _step(24)},
        "aliases": ("致胜的瞬间", "制胜", "杰帕德专武"),
    },
    "她已闭上双眼": {
        "template": "生命上限提高{hpPct}%，能量恢复效率提高；生命降低时，我方全体造成的伤害提高{dmg}%。",
        "values": {"hpPct": _step(24), "dmg": _step(9)},
        "aliases": ("闭上双眼", "符玄专武"),
    },
    "命运从未公平": {
        "template": "防御力提高；施加护盾后暴击伤害提高，并使受击目标受到的伤害提高。",
        "values": {},
        "aliases": ("命运公平", "砂金专武"),
    },
    "余生的第一天": {
        "template": "防御力提高{defPct}%；进入战斗后使我方全体伤害抗性提高。",
        "values": {"defPct": _step(16)},
        "aliases": ("余生",),
    },
    "两个人的演唱会": {
        "template": "防御力提高；场上每有一个持有护盾的角色，装备者造成的伤害提高。",
        "values": {},
        "aliases": ("两人的演唱会",),
    },
    "宇宙市场趋势": {
        "template": "防御力提高；受到攻击后有概率使敌方陷入灼烧状态。",
        "values": {},
        "aliases": ("市场趋势",),
    },

    # 丰饶
    "惊魂夜": {
        "template": "能量恢复效率提高{recharge}%；我方目标施放终结技时回复生命，治疗时提高目标攻击力。",
        "values": {"recharge": _step(12)},
        "aliases": ("藿藿专武",),
    },
    "棺的回响": {
        "template": "攻击力提高{atkPct}%；攻击不同敌方目标后恢复能量，施放终结技后我方全体速度提高{speed}点。",
        "values": {"atkPct": _step(24), "speed": _step(12)},
        "aliases": ("罗刹专武",),
    },
    "一场术后对话": {
        "template": "能量恢复效率提高{recharge}%；释放终结技时治疗量提高{qHeal}%。",
        "values": {"recharge": _step(8), "qHeal": _step(12)},
        "aliases": ("术后对话",),
    },
    "此时恰好": {
        "template": "效果抵抗提高{effDef}%；基于效果抵抗提高治疗量。",
        "values": {"effDef": _step(16)},
        "aliases": (),
    },
    "唯有香如故": {
        "template": "击破特攻提高；终结技攻击敌方目标后，使其受到的伤害提高。",
        "values": {},
        "aliases": ("灵砂专武",),
    },
    "同一种心情": {
        "template": "治疗量提高{heal}%；施放战技后为我方全体恢复能量。",
        "values": {"heal": _step(10)},
        "aliases": (),
    },

    # 记忆
    "将光阴织成黄金": {
        "template": "速度提高{speed}；获得6层【锦缎】后，暴击伤害提高{cdmg}%，普攻伤害提高{aDmg}%。",
        "values": {"speed": _step(12), "cdmg": (54, 63, 72, 81, 90), "aDmg": (54, 63, 72, 81, 90)},
        "aliases": ("光阴织成黄金", "阿格莱雅专武"),
    },
    "让告别，更美一些": {
        "template": "使装备者的生命上限提高{hpPct}%，装备者或装备者的忆灵在自身回合内损失生命值时，装备者获得【冥花】，【冥花】可以使装备者和装备者的忆灵造成伤害时，无视目标{ignore}%的防御力，持续2回合。当装备者的忆灵消失时，使装备者行动提前{advance}%。该效果最多触发1次，装备者每次施放终结技时重置触发次数。",
        "values": {"hpPct": _step(30), "ignore": _step(30), "advance": _step(12)},
        "aliases": ("让告别更美一些", "遐蝶专武"),
    },
    "多流汗，少流泪": {
        "template": "暴击率提高{cpct}%，造成的伤害提高{dmg}%。",
        "values": {"cpct": _step(12), "dmg": _step(24)},
        "aliases": ("多流汗少流泪",),
    },
    "天才们的问候": {
        "template": "攻击力提高{atkPct}%；普攻造成的伤害提高{aDmg}%。",
        "values": {"atkPct": _step(16), "aDmg": _step(24)},
        "aliases": (),
    },
    "胜利只在朝夕间": {
        "template": "暴击伤害提高{cdmg}%，造成的伤害提高{dmg}%。",
        "values": {"cdmg": _step(24), "dmg": _step(24)},
        "aliases": ("胜利只在朝夕",),
    },
}

_INDEX: Dict[str, str] = {}
for _name, _data in LIGHT_CONE_EFFECTS.items():
    _INDEX[_norm_name(_name)] = _name
    for _alias in _data.get("aliases", ()):
        _INDEX[_norm_name(str(_alias))] = _name


def get_light_cone_effect(name: str, refine: int = 1) -> str:
    """返回星铁光锥按叠影等级替换后的效果摘要。"""
    key = _INDEX.get(_norm_name(name))
    if not key:
        return ""
    data = LIGHT_CONE_EFFECTS[key]
    return _render(str(data.get("template") or ""), data.get("values") or {}, refine)
