"""從文策院 2025 年消費趨勢調查 Excel 的 Codebook 工作表，抽出面向 A 會用到的變數清單。

只用標準函式庫（不需要 openpyxl）。輸出放在 data_processed/，該資料夾不進版本控制，需要時重跑本程式即可。
用法：在專案根目錄執行  python scripts/extract_codebook.py
"""
import csv
import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "data_raw", "taicca", "2025_消費趨勢調查", "2025.trend_consumer.xlsx")
OUT = os.path.join(ROOT, "data_processed", "A_candidate_variables.csv")
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def shared_strings(z):
    out = []
    for _, el in ET.iterparse(z.open("xl/sharedStrings.xml")):
        if el.tag == M + "si":
            out.append("".join(t.text or "" for t in el.iter(M + "t")))
            el.clear()
    return out


def sheet_path(z, name):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    for s in wb.find(M + "sheets"):
        if s.get("name") == name:
            return "xl/" + rels[s.get(R + "id")].lstrip("/").replace("xl/", "")
    raise KeyError(name)


def rows(z, path, ss):
    for _, el in ET.iterparse(z.open(path)):
        if el.tag == M + "row":
            r = {}
            for c in el.findall(M + "c"):
                v = c.find(M + "v")
                if v is None:
                    continue
                r[re.match(r"[A-Z]+", c.get("r")).group()] = ss[int(v.text)] if c.get("t") == "s" else v.text
            yield r
            el.clear()


def main():
    if not os.path.exists(XLSX):
        sys.exit("找不到 " + XLSX + "，請先把 2025.trend_consumer.xlsx 放到 data_raw/taicca/2025_消費趨勢調查/")
    z = zipfile.ZipFile(XLSX)
    ss = shared_strings(z)
    rs = list(rows(z, sheet_path(z, "Codebook"), ss))[2:]
    variables = []
    for r in rs:
        if r.get("A"):
            first = [f'{r["C"]}={r.get("D", "")}'] if r.get("C") not in (None, "") else []
            variables.append({"code": r["A"], "text": re.sub(r"\s+", " ", r.get("B", "")), "labels": first})
        elif variables and r.get("C") not in (None, ""):
            variables[-1]["labels"].append(f'{r["C"]}={r.get("D", "")}')
    keep = [v for v in variables if v["code"].startswith("E") or v["code"].startswith("S") or v["code"] == "QArea"]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["變數代碼", "題目與選項說明", "值標籤"])
        for v in keep:
            w.writerow([v["code"], v["text"], "；".join(v["labels"][:30])])
    print(f"Codebook 共 {len(variables)} 個變數；輸出 {len(keep)} 個（E 開頭的出版題、S 開頭的受訪者資料、QArea）到 {OUT}")


if __name__ == "__main__":
    main()
