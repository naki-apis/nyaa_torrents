import argparse
import json
import os
import sys
import requests
from .scraper import search_nyaa


def download_torrent(url, dest_dir, filename):
    if not url:
        return False
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
    except requests.RequestException:
        return False
    os.makedirs(dest_dir, exist_ok=True)
    safe = "".join(c for c in filename if c not in '<>:"/\\|?*').strip() or "torrent"
    path = os.path.join(dest_dir, safe + ".torrent")
    with open(path, "wb") as f:
        f.write(r.content)
    return True


def parse_hide(value):
    if value is None:
        return set()
    valid = {"size", "date", "torrent", "magnet"}
    parts = [p.strip().lower() for p in value.split(",") if p.strip()]
    for p in parts:
        if p not in valid:
            raise argparse.ArgumentTypeError(f"invalid --hide value: {p} (valid: size,date,torrent,magnet)")
    return set(parts)


def main():
    parser = argparse.ArgumentParser(prog="nyaa", description="Search torrents on nyaa.si")
    parser.add_argument("query", nargs="+", help="Search query")
    parser.add_argument("--r18", action="store_true", help="Search on sukebei (R18)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--limit", type=int, default=None, help="Only fetch the N most recent pages (default: all)")
    parser.add_argument("--sort", choices=["date", "name", "reverse"], default=None, help="Sort results")
    parser.add_argument("--save", metavar="DIR", default=None, help="Save .torrent files to DIR")
    parser.add_argument("--hide", type=parse_hide, default=None, metavar="FIELDS", help="Hide fields: size,date,torrent,magnet (comma-separated)")
    args = parser.parse_args()

    query = " ".join(args.query)
    raw = search_nyaa(query, sukebei=args.r18, limit=args.limit, sort=args.sort)

    if args.json:
        print(raw)
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("Error: invalid response", file=sys.stderr)
        sys.exit(1)

    if not data:
        print("No results found.")
        return

    hidden = args.hide or set()

    for item in data:
        print(f"#{item['result_number']}")
        print(f"Name:    {item['name']}")
        if "size" not in hidden:
            print(f"Size:    {item['size']}")
        if "date" not in hidden:
            print(f"Date:    {item['date']}")
        if "torrent" not in hidden:
            print(f"Torrent: {item['torrent']}")
        if "magnet" not in hidden:
            print(f"Magnet:  {item['magnet']}")
        print()

        if args.save:
            ok = download_torrent(item['torrent'], args.save, item['name'])
            if ok:
                print(f"Saved to {args.save}/{item['name']}.torrent")
            else:
                print(f"Failed to save {item['name']}")


if __name__ == "__main__":
    main()
