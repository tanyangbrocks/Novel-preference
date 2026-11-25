"""面向 A：從 2025 年消費趨勢調查 Raw Data 計算小說閱讀相關比例。

需要 pandas 與 openpyxl。所有比例都是未加權（Raw Data 沒有權重欄），分母每列都寫明。
用法：在專案根目錄執行  python scripts/a_indicators.py
輸出：data_processed/A_indicators.csv（不進版本控制），並在終端機印出結果。
"""
import os
import re

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "data_raw", "taicca", "2025_消費趨勢調查", "2025.trend_consumer.xlsx")
CACHE = os.path.join(ROOT, "data_processed", "raw_A_subset.pkl")
OUT = os.path.join(ROOT, "data_processed", "A_indicators.csv")
NEED = re.compile(r"(No|S1|S2|S3|E1[1-7]|E3[1-6]|E4_C1_slice[12]|E22_C1_slice\d+|E12c|E12ab_C[12]_slice)$")

PLATFORMS = {  # E22 電子圖書平台，只列與原創小說相關的選項
    "E22_C1_slice17": "POPO小說原創", "E22_C1_slice16": "鏡文學", "E22_C1_slice12": "CxC創利市集",
    "E22_C1_slice39": "起點（其他，開放題編碼）", "E22_C1_slice53": "番茄小說（其他，開放題編碼）",
}


def load():
    if os.path.exists(CACHE):
        return pd.read_pickle(CACHE)
    df = pd.read_excel(XLSX, sheet_name="Raw Data", usecols=lambda c: bool(NEED.match(str(c))))
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    df.to_pickle(CACHE)
    return df


def row(name, k, base, note=""):
    return {"指標": name, "人數": int(k), "分母人數": int(base), "比例": round(k / base, 4), "備註": note}


def main():
    df = load()
    n = len(df)
    out = []
    lit = df["E11"] == 1
    out.append(row("閱讀文學圖書（E1 選項 C1）", lit.sum(), n, "全體；文學圖書含小說、網路小說、散文、繪本、詩集、劇本，無法單獨看網路小說"))
    anyread = df["E17"] != 1  # E17 = 以上皆無
    out.append(row("閱讀任何出版作品（E1 非「以上皆無」）", anyread.sum(), n, "報告頁 72 寫整體閱讀率 75%"))
    tw = df["E31"] == 1
    out.append(row("閱讀臺灣創作者的文學圖書（E3 選項 C1）", tw.sum(), n, "全體；E3 只問有閱讀出版作品者，其餘算 0；報告頁 72 寫 32%"))
    out.append(row("閱讀臺灣創作者的文學圖書，占文學圖書讀者", (tw & lit).sum(), lit.sum(), "分母為 E1 有閱讀文學圖書者"))
    out.append(row("文學圖書讀者用數位電子閱讀（E4）", df["E4_C1_slice2"].fillna(0).sum(), df["E4_C1_slice2"].notna().sum(), "分母為 E4 有答者（近一年閱讀文學圖書者）"))
    out.append(row("文學圖書讀者用實體紙本閱讀（E4）", df["E4_C1_slice1"].fillna(0).sum(), df["E4_C1_slice1"].notna().sum(), "同上"))
    plat_cols = [c for c in df.columns if c.startswith("E22_C1_slice")]
    ebook = df[plat_cols].notna().any(axis=1)
    out.append(row("電子圖書讀者（E22 有答者）", ebook.sum(), n, "占全體"))
    for c, name in PLATFORMS.items():
        if c in df:
            out.append(row(f"電子圖書讀者使用 {name}（E22）", df[c].fillna(0).sum(), ebook.sum(), "分母為 E22 有答者；選項沒有 KadoKado"))
    # 網路小說的代理指標：任一選項屬於網路小說或小說平台（2025 年調查沒有單獨的網路小說題）
    NOVEL = ["E22_C1_slice12", "E22_C1_slice16", "E22_C1_slice17", "E22_C1_slice39", "E22_C1_slice47",
             "E22_C1_slice52", "E22_C1_slice53", "E22_C1_slice54", "E22_C1_slice55", "E22_C1_slice56"]
    net = (df[[c for c in NOVEL if c in df]].fillna(0) == 1).any(axis=1)
    out.append(row("使用任一小說相關平台（CxC、鏡文學、POPO、起點、番茄等 10 項；網路小說的代理）", net.sum(), n, "占全體；鏡文學與 CxC 也做出版與 IP，不全是網路小說"))
    out.append(row("使用任一小說相關平台，占電子圖書讀者", net.sum(), ebook.sum(), "分母為 E22 有答者"))
    e12 = df["E12c"].dropna()
    out.append(row("圖書每月有付費（E12c ＞ 1，含紙本，含非文學）", (e12 > 1).sum(), len(e12), "分母為圖書讀者；不是只有小說"))
    e12d = df["E12ab_C2_slice"].dropna()
    out.append(row("數位電子圖書每月有付費（E12ab_C2 ＞ 1）", (e12d > 1).sum(), len(e12d), "分母為數位電子圖書讀者；含非文學；報告頁 79 寫付費讀者 n=418"))
    res = pd.DataFrame(out)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    res.to_csv(OUT, index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 200, "display.max_colwidth", 60)
    print(res[["指標", "人數", "分母人數", "比例"]].to_string(index=False))


if __name__ == "__main__":
    main()
