"""Read an XPR testnet account and its token stat table without signing."""
import argparse
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from token_plan import SYMBOL_RE

RPC = "https://testnet.protonchain.com"
TESTNET_CHAIN_ID = "71ee83bcf52142d61019d95f9cc5427ba6a0d7ff8accd9e2088ae2abeaf3d3dd"
ACCOUNT_NAME = re.compile(r"[a-z1-5.]{1,12}\Z")


def rpc_read(method, payload):
    request = Request(
        f"{RPC}/v1/chain/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=10) as response:
        return json.load(response)


def lookup(contract, symbol):
    if not ACCOUNT_NAME.fullmatch(contract) or not contract.strip("."):
        raise ValueError("Enter a valid contract account name.")
    if not SYMBOL_RE.fullmatch(symbol):
        raise ValueError("Enter a token symbol of 1–7 uppercase letters.")
    info = rpc_read("get_info", {})
    if info.get("chain_id") != TESTNET_CHAIN_ID:
        raise ValueError("The RPC did not report the expected XPR testnet chain ID.")
    account = rpc_read("get_account", {"account_name": contract})
    if account.get("account_name") != contract:
        raise ValueError("The RPC did not confirm the requested contract account.")
    result = rpc_read("get_table_rows", {
        "json": True, "code": contract, "scope": symbol, "table": "stat", "limit": 1,
    })
    rows = result["rows"]
    if len(rows) > 1 or result.get("more"):
        raise ValueError("The stat lookup returned an ambiguous result.")
    stat = rows[0] if rows else None
    if stat is not None:
        pattern = re.compile(r"([0-9]+)(?:\.([0-9]+))? " + symbol + r"\Z")
        supply = pattern.fullmatch(stat.get("supply", ""))
        maximum = pattern.fullmatch(stat.get("max_supply", ""))
        issuer = stat.get("issuer", "")
        if not supply or not maximum or not ACCOUNT_NAME.fullmatch(issuer):
            raise ValueError("The stat row does not match the standard token format.")
        precision = len(supply[2] or "")
        if precision != len(maximum[2] or ""):
            raise ValueError("The stat row reports inconsistent precision.")
        stat = {"issuer": issuer, "supply": stat["supply"],
                "maximum_supply": stat["max_supply"], "precision": precision}
    return {
        "rpc": RPC, "chain_id": info["chain_id"], "head_block": info["head_block_num"],
        "contract_account": contract, "symbol": symbol,
        "status": "stat_found" if stat else "no_stat_row",
        "stat": stat,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract")
    parser.add_argument("symbol")
    args = parser.parse_args()
    try:
        print(json.dumps(lookup(args.contract, args.symbol), indent=2))
    except HTTPError as exc:
        parser.exit(1, f"Testnet RPC rejected the lookup (HTTP {exc.code}).\n")
    except (URLError, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        parser.exit(1, f"Testnet lookup could not be verified: {exc}\n")


if __name__ == "__main__":
    main()
