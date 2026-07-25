#!/usr/bin/env python3
"""Patch InStock crawlers: push2 -> push2delay + paginate (max 100/page)."""
from pathlib import Path
import re

CRAWL = Path("/data/InStock/instock/core/crawling")


def patch_hist():
    path = CRAWL / "stock_hist_em.py"
    text = path.read_text()
    old = '''def stock_zh_a_spot_em() -> pd.DataFrame:
    """
    东方财富网-沪深京 A 股-实时行情
    https://quote.eastmoney.com/center/gridlist.html#hs_a_board
    :return: 实时行情
    :rtype: pandas.DataFrame
    """
    url = "https://push2delay.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "50000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
        "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f14,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25,f26,f37,f38,f39,f40,f41,f45,f46,f48,f49,f57,f61,f100,f112,f113,f114,f115,f221",
        "_": "1623833739532",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if not data_json["data"]["diff"]:
        return pd.DataFrame()
    temp_df = pd.DataFrame(data_json["data"]["diff"])'''
    new = '''def stock_zh_a_spot_em() -> pd.DataFrame:
    """
    东方财富网-沪深京 A 股-实时行情
    https://quote.eastmoney.com/center/gridlist.html#hs_a_board
    :return: 实时行情
    :rtype: pandas.DataFrame
    """
    import math, time, random
    url = "https://push2delay.eastmoney.com/api/qt/clist/get"
    page_size = 100
    page_current = 1
    params = {
        "pn": page_current,
        "pz": page_size,
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
        "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f14,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25,f26,f37,f38,f39,f40,f41,f45,f46,f48,f49,f57,f61,f100,f112,f113,f114,f115,f221",
        "_": "1623833739532",
    }
    r = requests.get(url, params=params, timeout=30)
    data_json = r.json()
    if not data_json["data"]["diff"]:
        return pd.DataFrame()
    data = data_json["data"]["diff"]
    data_count = data_json["data"]["total"]
    page_count = math.ceil(data_count / page_size)
    while page_count > 1:
        time.sleep(random.uniform(0.2, 0.5))
        page_current += 1
        params["pn"] = page_current
        r = requests.get(url, params=params, timeout=30)
        data_json = r.json()
        data.extend(data_json["data"]["diff"])
        page_count -= 1
    temp_df = pd.DataFrame(data)'''
    if old not in text:
        raise SystemExit("stock_zh_a_spot_em pattern not found")
    path.write_text(text.replace(old, new, 1))
    print("OK stock_hist_em")


def patch_etf():
    path = CRAWL / "fund_etf_em.py"
    text = path.read_text()
    old = '''    url = "https://push2delay.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "2000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "wbp2u": "|0|0|0|web",
        "fid": "f3",
        "fs": "b:MK0021,b:MK0022,b:MK0023,b:MK0024",
        "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
        "_": "1672806290972",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["data"]["diff"])'''
    new = '''    import math, time, random
    url = "https://push2delay.eastmoney.com/api/qt/clist/get"
    page_size = 100
    page_current = 1
    params = {
        "pn": page_current,
        "pz": page_size,
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "wbp2u": "|0|0|0|web",
        "fid": "f3",
        "fs": "b:MK0021,b:MK0022,b:MK0023,b:MK0024",
        "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
        "_": "1672806290972",
    }
    r = requests.get(url, params=params, timeout=30)
    data_json = r.json()
    data = data_json["data"]["diff"]
    data_count = data_json["data"]["total"]
    page_count = math.ceil(data_count / page_size)
    while page_count > 1:
        time.sleep(random.uniform(0.2, 0.5))
        page_current += 1
        params["pn"] = page_current
        r = requests.get(url, params=params, timeout=30)
        data_json = r.json()
        data.extend(data_json["data"]["diff"])
        page_count -= 1
    temp_df = pd.DataFrame(data)'''
    if old not in text:
        raise SystemExit("fund_etf_spot_em pattern not found")
    path.write_text(text.replace(old, new, 1))
    print("OK fund_etf_em")


PAGINATE_HELPER = '''
def _fetch_clist_paginated(url, params, page_size=100):
    import math, time, random
    import requests
    params = dict(params)
    params["pz"] = page_size
    params["pn"] = 1
    r = requests.get(url, params=params, timeout=30)
    data_json = r.json()
    data = data_json["data"]["diff"]
    data_count = data_json["data"]["total"]
    page_count = math.ceil(data_count / page_size)
    page_current = 1
    while page_count > 1:
        time.sleep(random.uniform(0.2, 0.5))
        page_current += 1
        params["pn"] = page_current
        r = requests.get(url, params=params, timeout=30)
        data_json = r.json()
        data.extend(data_json["data"]["diff"])
        page_count -= 1
    return data
'''


def patch_fund():
    path = CRAWL / "stock_fund_em.py"
    text = path.read_text()
    if "_fetch_clist_paginated" not in text:
        # insert helper after imports
        text = text.replace(
            "import requests\n",
            "import requests\n" + PAGINATE_HELPER + "\n",
            1,
        )

    # Replace single-shot get+DataFrame patterns for push2delay clist
    pattern = re.compile(
        r'url = "https://push2delay\.eastmoney\.com/api/qt/clist/get"\n'
        r'(?P<body>(?:.*\n)*?)'
        r'    r = requests\.get\(url, params=params\)\n'
        r'    data_json = r\.json\(\)\n'
        r'    temp_df = pd\.DataFrame\(data_json\["data"\]\["diff"\]\)',
        re.M,
    )

    def repl(m):
        body = m.group("body")
        # normalize large pz to page_size via helper
        body = re.sub(r'"pz":\s*"\d+"', '"pz": "100"', body)
        return (
            'url = "https://push2delay.eastmoney.com/api/qt/clist/get"\n'
            f"{body}"
            '    temp_df = pd.DataFrame(_fetch_clist_paginated(url, params))\n'
        )

    new_text, n = pattern.subn(repl, text)
    if n < 1:
        raise SystemExit("stock_fund_em clist patterns not found")
    path.write_text(new_text)
    print(f"OK stock_fund_em patched {n} clist fetch(es)")


if __name__ == "__main__":
    patch_hist()
    patch_etf()
    patch_fund()
    print("all patches applied")
