"""Leanest validation path — no server needed.

Usage:
    python run_cli.py "fitness"
"""
import sys
import json
from core.pipeline import scan


def main():
    niche = " ".join(sys.argv[1:]).strip() or input("Niche: ").strip()
    print(f"\nScanning '{niche}' ... (this can take 20-60s)\n")
    report = scan(niche, use_cache=False)

    if report.get("error"):
        print("ERROR:", report["error"])
        return

    print("=" * 50)
    print(f"NICHE: {report['niche']}")
    s = report.get("stats", {})
    print(f"Scanned {s.get('scanned')} conversations | "
          f"{s.get('topics')} topics | {s.get('communities')} communities")

    print("\n=== WHAT TO MAKE ===")
    for i, t in enumerate(report.get("topics", []), 1):
        print(f"{i}. [{t.get('demand')}/100] {t.get('title')}  ({t.get('format')})")
        q = (t.get("example_quote") or "").strip()
        if q:
            print(f"     e.g. {q[:140]}")

    print("\n=== WHERE TO POST ===")
    for c in report.get("communities", []):
        print(f" - {c['name']:<28} subs:{c['subscribers']:<10} mentions:{c['mentions']}")

    # Save full JSON next to you for sharing/validation
    with open("last_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\nFull JSON saved to last_report.json")


if __name__ == "__main__":
    main()
