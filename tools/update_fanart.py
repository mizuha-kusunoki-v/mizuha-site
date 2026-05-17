"""
ファンアートギャラリー更新スクリプト
======================================
使い方:
  1. fanart_list.csv に作品情報を追記する
  2. 画像を docs/img/fanart/ に保存する（省略可・省略時はダミー表示）
  3. python tools/update_fanart.py を実行する
  4. git add . && git commit && git push で公開

CSV のフォーマット:
  filename  : 画像ファイル名（例: 001.png）。未取得の場合は空欄でOK
              複数枚の場合は count を指定し 001_1.png / 001_2.png ... と命名する
  author    : 作者名（様 は自動付与）
  x_handle  : X の ID（@ なし）
  post_url  : 元ポストの URL
  count     : 画像の枚数（省略 or 1 = 1枚、2以上 = 複数枚）
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


def expand_filenames(filename: str, count: int) -> list[str]:
    """count に応じてファイル名リストを生成する。
    count=1 → ["001.png"]
    count=3 → ["001_1.png", "001_2.png", "001_3.png"]
    """
    if count <= 1:
        return [filename] if filename else [""]

    if filename:
        p = Path(filename)
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

    filenames = expand_filenames(filename, count)
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

    # --- 既存の登録済み URL を取得 ---
    md = MD_FILE.read_text(encoding="utf-8")

    if START_MARKER not in md or END_MARKER not in md:
        print(f"❌ {MD_FILE} にマーカーが見つかりません。")
        return

    start = md.index(START_MARKER) + len(START_MARKER)
    end   = md.index(END_MARKER)
    existing_block = md[start:end]

    registered_urls = {
        line.split('href="')[1].split('"')[0]
        for line in existing_block.splitlines()
        if 'href="https://x.com/' in line and 'status/' in line
    }

    # --- 新規エントリのみフィルタ ---
    new_entries  = []
    skip_entries = []
    for row in entries:
        url = row["post_url"].strip()
        if url in registered_urls:
            skip_entries.append(row)
        else:
            new_entries.append(row)

    if skip_entries:
        print(f"⏭️  {len(skip_entries)} 件はすでに登録済みのためスキップ:")
        for row in skip_entries:
            count = int(row.get("count", "1").strip() or "1")
            label = f"{count}枚" if count > 1 else "1枚"
            print(f"      {row['author']}様 [{label}] ({row['post_url']})")

    if not new_entries:
        print("ℹ️  追加する新規エントリはありませんでした。")
        return

    # --- 新規カードを既存ブロックの末尾に追記 ---
    all_cards = []
    for row in new_entries:
        all_cards.extend(generate_cards_for_entry(row))

    new_block  = "\n\n".join(all_cards)
    updated_block = existing_block.rstrip() + "\n\n" + new_block + "\n\n"
    new_md = md[:start] + updated_block + md[end:]
    MD_FILE.write_text(new_md, encoding="utf-8")

    total_cards = sum(int(r.get("count", "1").strip() or "1") for r in new_entries)
    print(f"✅ {len(new_entries)} 件（計 {total_cards} 枚）を新たに追加しました。")
    for i, row in enumerate(new_entries, 1):
        count  = int(row.get("count", "1").strip() or "1")
        has_img = row["filename"].strip()
        status = "🖼️ " if has_img else "⬜ (画像未設定)"
        label  = f"{count}枚" if count > 1 else "1枚"
        print(f"  {i:02d}. {status} {row['author']}様 [@{row['x_handle']}] {label}")


if __name__ == "__main__":
    main()
