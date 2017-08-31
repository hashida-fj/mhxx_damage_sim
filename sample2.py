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

for url in urls:
    local_filename = url+".html"

    with open(local_filename) as fn:
        html = fn.read()

    soup = BeautifulSoup(html, "html.parser")

    items = []
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

        aa = [len(s.string or "") for s in kireaji.find_all("span")]
        if aa[7] == 0:
            item["takumi_fuyou"] = "1"
        else:
            item["takumi_fuyou"] = "0"

        zip_ = zip(kireaji_colors, [i for i in aa[8:15]])
        list_ = ["{}{}".format(c, v*10) for c, v in zip_ if v != 0]
        item["kireaji"] = "".join(list_[-2:])

        zip_ = zip(kireaji_colors, [i for i in aa[0:7]])
        list_ = ["{}{}".format(c, v*10) for c, v in zip_ if v != 0]
        item["kireaji2"] = "".join(list_[-2:])

        # senritsu
        colorpat = re.compile(r"color:(.*);")
        if item["wepontype"] in ["fue"]:
            cl = [colorpat.match(s["style"]).group(1) for s in tds[4].div.find_all("span")]
            biko = "".join([fue_colors[c] for c in cl])

        item["biko"] = biko

        # output
        print(",".join([item[k] or "" for k in keyorder]))
        items.append(item)
