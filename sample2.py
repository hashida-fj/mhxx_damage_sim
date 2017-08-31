# import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from urllib.parse import urlparse, urlsplit, parse_qs, urljoin
from tqdm import tqdm

from parse import *

import os.path
import time
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
]

for url in urls:
    download_urls = []

    # baseurl = urljoin(url, ")}/")
    # tmpfn = parse_qs(urlparse(url).query)['view'][0]

    # (local_filename, headers) = urlretrieve(url, tmpfn)
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

        # output
        print(",".join([item[k] or "" for k in keyorder]))
        items.append(item)
