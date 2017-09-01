# import requests
from bs4 import BeautifulSoup
import re


urls = [
    u"taiken",
    u"tati",
    u"katate",
    u"souken",
    u"hanma",
    u"ransu",
    u"fue",      # 旋律がある
    u"gansu",    # 砲撃がある
    u"chaaku",   # ビンがある
    u"suraaku",  # ビンがある
    u"musikon",  # 虫の種類がある
    u"yumi",     # 溜めレベル、ビンがある
    u"raito",    # 玉、速射がある
    u"hebi",     # 玉、しゃがみがある
]

keyorder = [
    "level",
    "wepontype",
    "name",
    "buturi",
    "crit_p",
    "crit_m",
    "def",
    "fire",
    "water",
    "elec",
    "ice",
    "dragon",
    "para",
    "drowsy",
    "poison",
    "exp",
    "takumi_fuyou",
    "kireaji",
    "kireaji2",
    "slot",
    "biko"
]

kireaji_colors = ["赤", "橙", "黄", "緑", "青", "白", "紫"]

fue_colors = {
    "#00cc00": "緑",
    "#00eeee": "空",
    "#e0002a": "赤",
    "#eeee00": "黄",
    "#ef810f": "橙",
    "#f3f3f3": "白",
    "#ff00ff": "紫",
    "blue"   : "青"}

items = []
for url in urls:
    local_filename = url+".html"

    with open(local_filename) as fn:
        html = fn.read()

    soup = BeautifulSoup(html, "html.parser")

    for x in soup.select("table tbody > tr"):
        tds = x.find_all("td")

        item = {}

        # name and pyhsical power
        item["wepontype"] = url
        item["name"] = tds[0].span.a.string

        # wepon level
        pat = r"http://wiki.mhxg.org/images/weapon/w.*-(.*).gif"
        parser = re.compile(pat)
        item["level"] = parser.match(tds[0].img["src"]).group(1)

        # critical, defence, elemental
        if item["wepontype"] in ["raito", "hebi"]:
            item["seinou"] = "".join([x.strip() for x in tds[2].findAll(text=True)])
        else:
            item["buturi"] = tds[2].string
            item["seinou"] = "".join([x.strip() for x in tds[3].findAll(text=True)])

        pat = re.compile(r"""
        (
        攻撃：(?P<buturi>\d*)|
        会心(?P<crit_p>\d*)% |
        会心-(?P<crit_m>\d*)% |
        防御\+(?P<def>\d*) |
        火(?P<fire>\d*) |
        水(?P<water>\d*) |
        雷(?P<elec>\d*) |
        氷(?P<ice>\d*) |
        龍(?P<dragon>\d*) |
        麻痺(?P<para>\d*) |
        睡眠(?P<drowsy>\d*) |
        毒(?P<poison>\d*) |
        爆破(?P<exp>\d*)
        )*
        """, re.VERBOSE)
        mo = pat.match(item["seinou"])
        dict = mo.groupdict()
        upd = {k: dict[k] for k in dict if (k not in item)}
        item.update(upd)

        # kireaji
        if item["wepontype"] in ["taiken", "tati", "katate", "souken", "hanma", "ransu"]:
            biko = ""
            kireaji = tds[4].div
            item["slot"] = str(3 - tds[5].string.count("-"))
        elif item["wepontype"] in ["fue", "gansu", "chaaku", "suraaku", "musikon"]:
            biko = tds[4].string
            kireaji = tds[5].div
            item["slot"] = str(3 - tds[6].string.count("-"))

        kireaji_values = [len(s.string or "") for s in kireaji.find_all("span")]
        if kireaji_values[7] == 0:
            item["takumi_fuyou"] = "1"
        else:
            item["takumi_fuyou"] = "0"

        zip_ = zip(kireaji_colors, kireaji_values[8:15])
        list_ = ["{}{}".format(c, v*10) for c, v in zip_ if v != 0]
        item["kireaji"] = "".join(list_[-2:])

        zip_ = zip(kireaji_colors, kireaji_values[0:7])
        list_ = ["{}{}".format(c, v*10) for c, v in zip_ if v != 0]
        item["kireaji2"] = "".join(list_[-2:])

        # senritsu
        colorpat = re.compile(r"color:(.*);")
        if item["wepontype"] in ["fue"]:
            cl = [colorpat.match(s["style"]).group(1) for s in tds[4].div.find_all("span")]
            biko = "".join([fue_colors[c] for c in cl])

        item["biko"] = biko

        # append
        items.append(item)


def printAll():
    for item in items:
        print(",".join([item[k] or "" for k in keyorder]))


def getExpectedValue(item,
                     b_add=0, c_add=0,
                     tyou=False, tuukon=False, kyougeki=False):
    gofu = 5
    tume = 10
    crit_p_gain = 1.25 if not tyou else 1.4
    crit_m_gain = 0.75 if not tuukon else 1.0625

    # indicated value
    indicated = int(item["buturi"]) + gofu + tume + b_add

    # critical ration

    if kyougeki:
        c_add += 30

    if "or" in item["name"]:
        crit_m_hit = int(item["crit_m"] or "0")
        crit_p_hit = min(int(item["crit_p"] or "0") + c_add,
                         100 - crit_m_hit)
        if kyougeki:
            crit_p_hit += crit_m_hit
            crit_m_hit = 0
    else:
        crit_p_hit = min(int(item["crit_p"] or "0") + c_add,
                         100)
        crit_m_hit = int(item["crit_m"] or "0")

    normal_hit = 100 - crit_p_hit - crit_m_hit
    crit_gain = (normal_hit
                 + crit_p_hit * crit_p_gain
                 + crit_m_hit * crit_m_gain) / 100.0

    # print("+ {} * {} / -{} * {}  -- {}".format(crit_p_hit, crit_p_gain, crit_m_hit, crit_m_gain, normal_hit))

    # kireaji
    if u"紫" in item["kireaji"]:
        kireaji_gain = 1.39
    elif u"白"in item["kireaji"]:
        kireaji_gain = 1.32
    elif u"青"in item["kireaji"]:
        kireaji_gain = 1.2
    elif u"緑"in item["kireaji"]:
        kireaji_gain = 1.05
    else:
        kireaji_gain = 1.0

    # print(kireaji_gain)

    # 期待値
    return indicated * crit_gain * kireaji_gain


def printExpected():
    for item in items:
        print("{} {}".format(item["name"],
                             getExpectedValue(item, 40)))


def printNephilium():
    for item in items:
        if "or" in item["name"]:
            print("{} {} {} {} {} {}"
                  .format(item["name"],
                          getExpectedValue(item, tyou=True),
                          getExpectedValue(item, tuukon=True),
                          getExpectedValue(item, tyou=True, tuukon=True),
                          getExpectedValue(item, kyougeki=True),
                          getExpectedValue(item, tyou=True, kyougeki=True)
                  )
            )


def parseSkills(skills):
    arg = {
        "c_add": 0,
        "b_add": 0,
        "tyou": False,
        "tuukon": False,
        "kyougeki": False,
    }

    if u"見切り1" in skills:
        arg["c_add"] = 10
    if u"見切り2" in skills:
        arg["c_add"] = 20
    if u"見切り3" in skills:
        arg["c_add"] = 30

    if u"連撃" in skills:
        arg["c_add"] += 30
    if u"弱特" in skills:
        arg["c_add"] += 50

    if u"超会心" in skills:
        arg["tyou"] = True
    if u"痛恨" in skills:
        arg["tuukon"] = True

    if u"狂" in skills:
        arg["kyougeki"] = True
    if u"挑戦者2" in skills:
        arg["b_add"] += 20
        arg["c_add"] += 15
    elif u"本気2" in skills:
        arg["c_add"] += 50

    return arg


def printVariousSkills():
    skills = [
        "見切り1連撃超会心",
        "見切り2連撃超会心",
        "挑戦者2超会心",
        "挑戦者2連撃",
        "見切り2連撃弱特",
        "狂超会心",
    ]
    print(" ".join(["名前"] + skills))

    args = [parseSkills(s) for s in skills]
    for item in items:
        values = [str(getExpectedValue(item, **arg)) for arg in args]
        print(" ".join([item["name"]] + values))


# printAll()
# printExpected()

printVariousSkills()
