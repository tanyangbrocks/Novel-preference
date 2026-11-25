# data_raw：原始資料

放從外部取得的原始檔，不修改、不覆蓋。這個資料夾的內容不進 git（見 `.gitignore`），只有本說明與 `manifest.csv` 會進。

- `manifest.csv`：每個檔案的來源網址、取得日期、大小與 SHA256，用來確認檔案沒被改過、也讓別人知道去哪裡重新取得。
- 命名：`data_raw/<提供者>/<年度_資料名稱>/<原檔名>`，保留原檔名。
- 新增檔案時，同步補 `manifest.csv` 與 `sources/source_register.csv`。

## 還沒取得、需要手動下載的檔案
文策院研究資料庫的 PDF 有 Cloudflare 驗證，我沒辦法自動下載，請用瀏覽器下載後放到下列位置：

| 檔案 | 下載連結 | 放到 |
|---|---|---|
| 2025 年文化內容消費趨勢調查報告（PDF） | https://research.taicca.tw/pdf/6cb49a4c-22dc-3f6d-bb2f-79f49d8010d5 | `data_raw/taicca/2025_消費趨勢調查/` |
| 跨域文化內容閱聽調查報告（上）（PDF） | https://research.taicca.tw/pdf/735225b4-ec9d-34aa-a764-295719dea446 | `data_raw/taicca/跨域閱聽調查/` |

存檔後把檔名、大小補進 `manifest.csv`。
