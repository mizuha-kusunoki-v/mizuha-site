"""
ファンアートギャラリー更新スクリプト
======================================
使い方:
  1. fanart_list.csv に作品情報を追記する
  2. 画像を docs/img/fanart/ に保存する（省略可・省略時はダミー表示）
  3. python tools/update_fanart.py を実行する
  4. git add . && git commit && git push で公開

CSV のフォーマット:
  filename  : ファイルのベース名（例: 001）または拡張子付き（例: 001.png）
              未取得の場合は空欄でOK
              複数枚の場合は count を指定し 001_1 / 001_2 ... と自動展開される
  author    : 作者名（様 は自動付与）
  x_handle  : X の ID（@ なし）
  post_url  : 元ポストの URL
  count     : 画像の枚数（省略 or 1 = 1枚、2以上 = 複数枚）
  ext       : 画像フォーマット（png / jpg / webp など、省略時は png）
              filename に拡張子が含まれている場合はそちらが優先される
"""

import csv
import sys
from pathlib import Path

# Windows コンソールの文字化け対策
sys.stdout.reconfigure(encoding="utf-8")

ROOT     = Path(__file__).parent.parent
CSV_FILE = ROOT / "fanart_list.csv"
MD_FILE  = ROOT / "docs" / "fanart_gallery.md"

START_MARKER = "<!-- FANART_START -->"
END_MARKER   = "<!-- FANART_END -->"


def resolve_filename(filename: str, ext: str) -> str:
    """filename と ext を組み合わせて完全なファイル名を返す。
    - filename に拡張子あり → そのまま使用（ext は無視）
    - filename に拡張子なし → filename.ext に結合
    - filename が空 → 空文字を返す
    """
    if not filename:
        return ""
    p = Path(filename)
    if p.suffix:          # 拡張子が既にある場合はそのまま
        return filename
    return f"{filename}.{ext.lstrip('.')}"


def expand_filenames(filename: str, ext: str, count: int) -> list[str]:
    """count に応じてファイル名リストを生成する。
    count=1 → ["001.png"]
    count=3 → ["001_1.png", "001_2.png", "001_3.png"]
    """
    full = resolve_filename(filename, ext)

    if count <= 1:
        return [full] if full else [""]

    if full:
        p = Path(full)
        return [f"{p.stem}_{i}{p.suffix}" for i in range(1, count + 1)]
    else:
        return [""] * count


def generate_card(filename: str, author: str, x_handle: str,
                  post_url: str, index: int = 0, total: int = 1) -> str:
    """1枚分のカード HTML を生成する。
    index / total は複数枚時のラベル用（0 なら非表示）。
    """
    if filename:
        img_src = f"img/fanart/{filename}"
    else:
        color   = "5BB8D4"
        label   = f"{author}様" + (f" ({index}/{total})" if total > 1 else "")
        img_src = f"https://placehold.co/400x400/{color}/ffffff?text={label}"

    label_html = f'<span class="fanart-index">{index}/{total}</span>' if total > 1 else ""

    return f"""\
<div class="fanart-card">
  <a href="{post_url}" target="_blank" rel="noopener">
    <img src="{img_src}" alt="{author}様のファンアート">
  </a>
  <div class="fanart-meta">
    {label_html}<a href="https://x.com/{x_handle}" target="_blank" rel="noopener">@{x_handle}</a>
  </div>
</div>"""


def generate_cards_for_entry(row: dict) -> list[str]:
    """1エントリ（1ポスト）分のカードリストを返す。"""
    filename = row["filename"].strip()
    author   = row["author"].strip()
    x_handle = row["x_handle"].strip()
    post_url = row["post_url"].strip()
    count    = int(row.get("count", "1").strip() or "1")
    ext      = row.get("ext", "png").strip() or "png"

    filenames = expand_filenames(filename, ext, count)
    return [
        generate_card(fn, author, x_handle, post_url,
                      index=i + 1 if count > 1 else 0,
                      total=count if count > 1 else 1)
        for i, fn in enumerate(filenames)
    ]


def main() -> None:
    # --- CSV 読み込み ---
    if not CSV_FILE.exists():
        print(f"❌ {CSV_FILE} が見つかりません。")
        return

    entries = []
    with open(CSV_FILE, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            entries.append(row)

    if not entries:
        print("⚠️  CSV にデータがありません。")
        return

    # --- CSV 内の重複 URL を除外（先勝ち） ---
    seen_urls    = set()
    unique_entries  = []
    dup_entries  = []
    for row in entries:
        url = row["post_url"].strip()
        if url in seen_urls:
            dup_entries.append(row)
        else:
            seen_urls.add(url)
            unique_entries.append(row)

    if dup_entries:
        print(f"⏭️  CSV 内に重複 URL が {len(dup_entries)} 件あったためスキップ:")
        for row in dup_entries:
            print(f"      {row['author']}様 ({row['post_url']})")

    # --- CSV 全件からギャラリーブロックを再生成 ---
    md = MD_FILE.read_text(encoding="utf-8")

    if START_MARKER not in md or END_MARKER not in md:
        print(f"❌ {MD_FILE} にマーカーが見つかりません。")
        return

    start = md.index(START_MARKER) + len(START_MARKER)
    end   = md.index(END_MARKER)

    all_cards = []
    for row in unique_entries:
        all_cards.extend(generate_cards_for_entry(row))

    new_block = "\n\n".join(all_cards)
    new_md = md[:start] + "\n\n" + new_block + "\n\n" + md[end:]
    MD_FILE.write_text(new_md, encoding="utf-8")

    total_cards = sum(
        len(generate_cards_for_entry(r)) for r in unique_entries
    )
    print(f"✅ {len(unique_entries)} 件（計 {total_cards} 枚）でギャラリーを更新しました。")
    for i, row in enumerate(unique_entries, 1):
        count   = int(row.get("count", "1").strip() or "1")
        has_img = row["filename"].strip()
        status  = "🖼️ " if has_img else "⬜ (画像未設定)"
        label   = f"{count}枚" if count > 1 else "1枚"
        print(f"  {i:02d}. {status} {row['author']}様 [@{row['x_handle']}] {label}")


if __name__ == "__main__":
    main()
