#!/usr/bin/env python3
"""Create a reviewable XPR Network TESTNET deployment plan; never execute transactions.

Usage: python3 src/token_plan.py --config examples/gwtest.json
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
from decimal import Decimal, InvalidOperation
from pathlib import Path

TOKEN_CONTRACT_SOURCE = (
    "https://github.com/XPRNetwork/ts-smart-contracts/tree/main/external/xtokens"
)
ACCOUNT_RE = re.compile(r"[a-z1-5]{4,12}\Z")
SYMBOL_RE = re.compile(r"[A-Z]{1,7}\Z")
INT64_MAX = 2**63 - 1


class PlanError(ValueError):
    """A configuration error that must be corrected before any deployment."""


def format_amount(value: object, precision: int) -> str:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise PlanError("Supply must be given as a decimal string or integer, not a float.")
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise PlanError(f"Invalid supply: {value!r}") from exc
    unit = Decimal(1).scaleb(-precision)
    if not amount.is_finite() or amount <= 0 or amount != amount.quantize(unit):
        raise PlanError(f"Supply must be positive with at most {precision} decimal places.")
    raw = amount * (10**precision)
    if raw > INT64_MAX:
        raise PlanError("Supply in smallest units exceeds the contract's signed 64-bit limit.")
    return f"{amount:.{precision}f}"


def command(*args: str) -> str:
    return " ".join(shlex.quote(x) for x in args)


def build_plan(config: dict) -> list[str]:
    if config.get("chain") != "proton-test":
        raise PlanError("Only proton-test is allowed in this training project. No mainnet output.")

    account = config.get("contract_account")
    issuer = config.get("issuer")
    recipient = config.get("initial_recipient")
    symbol = config.get("symbol")
    precision = config.get("precision")
    ram = config.get("ram_bytes", 200000)

    if not isinstance(account, str) or not ACCOUNT_RE.fullmatch(account):
        raise PlanError("contract_account must contain 4-12 lower-case letters or digits 1-5.")
    if issuer != account:
        raise PlanError("This starter requires issuer = contract_account.")
    if not isinstance(recipient, str) or not ACCOUNT_RE.fullmatch(recipient):
        raise PlanError("initial_recipient must be a valid existing XPR account name.")
    if not isinstance(symbol, str) or not SYMBOL_RE.fullmatch(symbol):
        raise PlanError("symbol must contain 1-7 uppercase letters.")
    if isinstance(precision, bool) or not isinstance(precision, int) or not (0 <= precision <= 18):
        raise PlanError("precision must be an integer between 0 and 18.")
    if isinstance(ram, bool) or not isinstance(ram, int) or ram <= 0:
        raise PlanError("ram_bytes must be a positive integer.")

    max_supply_text = format_amount(config.get("maximum_supply"), precision)
    issue_text = format_amount(config.get("initial_issue"), precision)
    if Decimal(issue_text) > Decimal(max_supply_text):
        raise PlanError("initial_issue cannot exceed maximum_supply.")

    creation = json.dumps({"issuer": issuer, "maximum_supply": f"{max_supply_text} {symbol}"}, separators=(",", ":"))
    issuance = json.dumps({"to": recipient, "quantity": f"{issue_text} {symbol}", "memo": "Testnet initial issuance"}, separators=(",", ":"))
    auth = f"{issuer}@active"
    return [
        "# XPR Network TESTNET only — REVIEW COMMANDS, never auto-run",
        "# BEFORE starting: confirm testnet account availability and authorization; make no live-chain changes.",
        "# Account creation and RAM purchases may incur resource costs even on a test network.",
        "# " + command("proton", "chain:set", "proton-test"),
        "# " + command("proton", "chain:get"),
        "# Check whether the account already exists before deciding to create it.",
        "# " + command("proton", "account", account),
        "# ONLY if the testnet account does not already exist:",
        "# " + command("proton", "account:create", account),
        "# ONLY after account creation, resource assessment, and approval:",
        "# " + command("proton", "ram:buy", account, account, str(ram)),
        "# ONLY after verifying official contract source and reviewing the bytecode:",
        "# " + command("proton", "contract:set", account, TOKEN_CONTRACT_SOURCE),
        "# TOKEN CREATE (review and sign; do not run if token symbol already exists under contract):",
        "# " + command("proton", "action", account, "create", creation, auth),
        "# TOKEN ISSUE (review and sign; do not repeat unless intended):",
        "# " + command("proton", "action", account, "issue", issuance, auth),
        "# Read-only verification after approval and execution (CLI: table CONTRACT TABLE SCOPE):",
        "# " + command("proton", "table", account, "stat", symbol),
        "# " + command("proton", "table", account, "accounts", recipient),
        "# Never paste private keys, seed phrases, or wallet recovery words into AI chats or repos.",
        "# Production mainnet, wallet registration, liquidity pools, and irreversible permission changes are deliberately excluded.",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        for line in build_plan(config):
            print(line)
    except (PlanError, json.JSONDecodeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
