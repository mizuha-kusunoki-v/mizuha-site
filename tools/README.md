# tools / ファンアートギャラリー更新ツール

## ファイル構成

```
tools/
├── update_fanart.py   ← 実行スクリプト
├── fanart_sample.csv  ← CSVの記載サンプル（参照用）
└── README.md          ← このファイル
fanart_list.csv        ← 実際のデータ（ルートに置く）
```

---

## CSV のフォーマット

| 列名 | 内容 | 省略 |
|---|---|---|
| `filename` | `docs/img/fanart/` に置く画像ファイル名 | 可（ダミー表示になる） |
| `author` | 作者名（様は自動付与） | 不可 |
| `x_handle` | X の ID（@ なし） | 不可 |
| `post_url` | 元ポストの URL | 不可 |

### 記載例

```csv
filename,author,x_handle,post_url
001.png,まおS,munouyaku_desu,https://x.com/munouyaku_desu/status/2053807330819805495
,ピリリたん,tottchiki2619,https://x.com/tottchiki2619/status/2021417657078018169
```

---

## 更新手順

```powershell
# 1. fanart_list.csv に作品情報を追記
# 2. 画像を docs/img/fanart/ に保存（省略可）
# 3. スクリプトを実行（venv を有効化してから）

.venv\Scripts\Activate.ps1
python tools\update_fanart.py

# 4. 確認 → 公開
git add .
git commit -m "ファンアート追加"
git push
```
