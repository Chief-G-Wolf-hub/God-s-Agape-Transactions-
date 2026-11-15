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

## Verify before deployment

1. Record each existing token's actual `contract_account`, chain, precision, issuer, maximum supply and current supply. Record chain explorers/transaction IDs as evidence.
2. Decide which asset, if any, needs a new contract or a code change. A ticker is not sufficient to identify a token; the chain and contract account matter.
3. On a controlled testnet account, check resources and authorities before deploying.
4. Compare deployed bytecode and ABI against a reviewed upstream version; run a separate security review before production.
5. Require human authorization for every chain-changing operation. No production deployment or wallet permission changes are implemented here.

**GitHub `main` is source control; XPR mainnet is a production blockchain.** Merging this repository cannot by itself create or change a token on XPR Network.

Official references: [Create a Token](https://docs.xprnetwork.org/guides/create-token.html) · [CLI commands](https://docs.xprnetwork.org/cli/usage) · [Standard token source](https://github.com/XPRNetwork/ts-smart-contracts/tree/main/external/xtokens)
