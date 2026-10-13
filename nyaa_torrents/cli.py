import argparse
import json
import sys
from .scraper import search_nyaa


def main():
    parser = argparse.ArgumentParser(prog="nyaa", description="Search torrents on nyaa.si")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--r18", action="store_true", help="Search on sukebei (R18)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    raw = search_nyaa(args.query, sukebei=args.r18)

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

    for item in data:
        print(f"#{item['result_number']}")
        print(f"Name:    {item['name']}")
        print(f"Size:    {item['size']}")
        print(f"Date:    {item['date']}")
        print(f"Torrent: {item['torrent']}")
        print(f"Magnet:  {item['magnet']}")
        print()


if __name__ == "__main__":
    main()
