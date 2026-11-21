#!/usr/bin/env python3
"""Export warehouse inventory as JSON for the app."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

DEFAULT_INVENTORY = Path(__file__).resolve().parents[1] / "inventory.csv"
FIELDS = (
    "symbol", "contract_account", "precision", "maximum_supply",
    "on_chain_status", "notes",
)


def load_inventory(path: Path = DEFAULT_INVENTORY) -> list[dict[str, str | int | None]]:
    """Read recorded values without inferring missing token identities or supplies."""
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        if reader.fieldnames is None or set(reader.fieldnames) != set(FIELDS) or len(reader.fieldnames) != len(FIELDS):
            raise ValueError("Inventory CSV must contain the documented columns.")

        tokens = []
        for row in reader:
            if None in row or any(row[field] is None for field in FIELDS):
                raise ValueError(f"Inventory row {reader.line_num} has the wrong number of fields.")
            token = {field: row[field].strip() or None for field in FIELDS}
            if not token["symbol"] or not token["on_chain_status"]:
                raise ValueError(f"Inventory row {reader.line_num} needs a symbol and status.")
            precision = token["precision"]
            if precision is not None:
                if not precision.isascii() or not precision.isdecimal() or len(precision) > 2 or int(precision) > 18:
                    raise ValueError(f"Inventory row {reader.line_num} has invalid precision.")
                token["precision"] = int(precision)
            tokens.append(token)
        return tokens


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    args = parser.parse_args()
    try:
        print(json.dumps(load_inventory(args.inventory), indent=2))
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
