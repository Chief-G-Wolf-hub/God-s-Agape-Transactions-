# God's Agape Transactions — XPR Token Engineering

This repository is the version-controlled engineering workspace for XPR Network token planning, verification, and later reviewed smart-contract development. It is **not** evidence that a token already exists or that a wallet, reserve, backing asset, liquidity pool, or exchange integration has been validated.

## Current deliverable

The first release supplies a **testnet-only, no-execution plan generator**. It generates annotated commands; it does not create blockchain accounts, deploy contracts, mint tokens, spend resources, manage keys, or access wallets. The demonstration token **GWTEST** is fictitious and must not be confused with any existing asset.

- `inventory.csv` — unverified inventory; **do not** mint any listed existing token without checking on-chain issuer, precision, supply and authorities.
- `examples/gwtest.json` — illustrative TESTNET token configuration; its `contract_account` is a placeholder and is **not verified available**.
- `src/token_plan.py` — validates example economics and prints commented review steps.
- `tests/test_token_plan.py` — automated safety/format tests.
- `docs/TESTNET_WORKFLOW.md` — detailed review and deployment workflow.
- `AGENTS.md` — coding-agent operating controls.

## Run line by line

```bash
python3 src/token_plan.py --config examples/gwtest.json
python3 -m unittest discover -s tests -v
```

No Python dependencies are needed beyond the standard library.

## Warehouse and factory integration

Run `python3 src/token_inventory.py` to export the warehouse inventory as a JSON array. Each entry has `symbol`, `contract_account`, `precision`, `maximum_supply`, `on_chain_status` and `notes`. Blank fields become JSON `null`. Precision is an integer and maximum supply is a decimal string so apps can preserve every digit. The status comes from the CSV and still requires on-chain verification.

The factory can call `src.token_plan.build_plan(config)` using the fields in `examples/gwtest.json`. Render the returned lines as review text. Every command, including the CLI network selection, is commented out.

## Verify before deployment

1. Record each existing token's actual `contract_account`, chain, precision, issuer, maximum supply and current supply. Record chain explorers/transaction IDs as evidence.
2. Decide which asset, if any, needs a new contract or a code change. A ticker is not sufficient to identify a token; the chain and contract account matter.
3. On a controlled testnet account, check resources and authorities before deploying.
4. Compare deployed bytecode and ABI against a reviewed upstream version; run a separate security review before production.
5. Require human authorization for every chain-changing operation. No production deployment or wallet permission changes are implemented here.

**GitHub `main` is source control; XPR mainnet is a production blockchain.** Merging this repository cannot by itself create or change a token on XPR Network.

Official references: [Create a Token](https://docs.xprnetwork.org/guides/create-token.html) · [CLI commands](https://docs.xprnetwork.org/cli/usage) · [Standard token source](https://github.com/XPRNetwork/ts-smart-contracts/tree/main/external/xtokens)

## Run the app

From the repository root, run `python3 src/app.py` and open
[http://127.0.0.1:8000](http://127.0.0.1:8000). Use `--port` to choose another
local port. The warehouse displays and filters the CSV inventory. The factory
accepts a testnet configuration, flags symbols already recorded in the warehouse,
and lets you download a text review plan. Verify chain, contract and issuer
identity before any creation or issuance, including for symbols with no local match.

## Read-only testnet preflight

Run `python3 src/token_preflight.py CONTRACT SYMBOL` to check a known contract
account on the XPR testnet RPC. The JSON output reports the observed chain ID,
head block, and any standard token stat row, including issuer, precision, supply
and maximum supply. `no_stat_row` means the lookup returned no row for that
contract and symbol. Confirm the contract uses the expected token table and
verify signer authority separately before creating or issuing. Treat any failed
RPC lookup as unknown. The reported supply is issued supply from the stat table.

## WebAuth Wallet target

Start with **XPR Network Testnet** in WebAuth Wallet. The factory currently
produces review plans and reads the testnet RPC. A future wallet handoff must
verify the XPR testnet chain ID and selected signer before presenting separate
create and issue approvals, and record each confirmed transaction ID.

The wallet's Metal Testnet, Metal L2 Testnet, Sepolia ETH, Sepolia OP and
XRP Ledger Testnet entries are separate integration targets. Each needs its own
transaction preparation, signing and confirmation tests. Wallet network
visibility alone does not establish app signing compatibility.
