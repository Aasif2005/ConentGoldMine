"""CLI: scan a niche from the terminal and save the report to last_report.json.

Usage (from the backend/ folder):
    python run_cli.py calisthenics
"""
import json
import sys
from app.controllers.scan_controller import ScanController


def main():
    niche = " ".join(sys.argv[1:]).strip() or input("Niche to scan: ").strip()
    report = ScanController().scan(niche, use_cache=False)

    with open("last_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    if report.get("error"):
        print("Error:", report["error"])
        return

    print(f"\n=== {report['niche']} ===")
    print("stats:", report["stats"])
    print("\nWhat to make:")
    for i, t in enumerate(report["topics"], 1):
        print(f"  {i}. [{t['demand']}] {t['title']} ({t.get('format', '')})")
    print("\nTop videos:")
    for v in report["videos"][:5]:
        print(f"  - {v['title']} | {v['views']} views, {v['likes']} likes")
    print("\nSaved -> last_report.json")


if __name__ == "__main__":
    main()
