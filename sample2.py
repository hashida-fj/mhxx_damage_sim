# import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from urllib.parse import urlparse, urlsplit, parse_qs, urljoin
from tqdm import tqdm

from parse import *

import os.path
import time


urls = [
    u"taiken.html",
    u"tati.html",
    u"katate.html",
    u"souken.html",
    u"hanma.html",
    u"ransu.html",

    u"fue.html",

    u"gansu.html",

    u"chaaku.html",
    u"suraaku.html",

    u"musikon.html",

    #u"raito.html",
    #u"hebi.html",
    #
    #u"yumi.html",

]

import re


def parseSeinou(str):
    seinou = {}

for url in urls:
    download_urls = []

    # baseurl = urljoin(url, ")}/")
    # tmpfn = parse_qs(urlparse(url).query)['view'][0]

    # (local_filename, headers) = urlretrieve(url, tmpfn)
    local_filename = url

    with open(local_filename) as fn:
        html = fn.read()

    soup = BeautifulSoup(html, "html.parser")

    items = []
    for x in soup.select("table tbody tr"):
        tds = x.find_all("td")

        item = {}

        # name and pyhsical power
        item["name"] = tds[0].span.a.string
        item["buturi"] = tds[2].string

        # wepon level
        pat = r"http://wiki.mhxg.org/images/weapon/w.*-(.*).gif"
        parser = re.compile(pat)
        item["level"] = parser.match(tds[0].img["src"]).group(1)

        # critical, defence, elemental
        item["seinou"] = "".join([x.strip() for x in tds[3].findAll(text=True)])
        pat = re.compile(r"""
        (
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
        m = pat.match(item["seinou"])
        if m is not None:
            dict = m.groupdict()

            for k in dict:
                if dict[k] is None:
                    item[k] = 0
                else:
                    item[k] = dict[k]
        # kireaji

        # print(u" {} {} {} {} {}".format(url, item["name"], item["buturi"], item["level"], item["crit_p"]))
        print(item)
        items.append(item)

