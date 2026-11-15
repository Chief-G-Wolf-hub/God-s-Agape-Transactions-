# XPR Network testnet runbook — human-reviewed commands

**STOP before anything that signs, broadcasts, mints, registers a token, changes a permission, buys RAM or spends funds.** The sample workflow below is documentation, not an unattended script.

## 1. Preflight

- Confirm `proton-test` is selected. The XPR CLI persists your chain selection, including after terminal restarts.
- Check the selected test account and each proposed contract name. Do not reuse a name without checking what already exists.
- Compare any existing on-chain token's `(chain, contract account, symbol, precision)` against `inventory.csv`.
- Confirm the planned supplies fit the signed 64-bit quantity limit and that the proposed issuance does not exceed maximum supply.
- Have an authorized signer review each action in the wallet or trusted signing environment. **Never put recovery phrases or private keys in source code, environment logs, or AI chats.**

## 2. Generate a *non-executing* review plan

```bash
python3 src/token_plan.py --config examples/gwtest.json
```

Sample values are intentionally hypothetical: no testnet account or token availability is asserted.

## 3. Official CLI examples, only for separately approved testnet operations

The [XPR official token guide](https://docs.xprnetwork.org/guides/create-token.html) documents these operations:

```bash
npm install -g @proton/cli
proton chain:set proton-test
proton chain:get
proton account YOUR_TESTNET_CONTRACT
# If new account explicitly approved:
# proton account:create YOUR_TESTNET_CONTRACT
# If resource expenditure approved:
# proton ram:buy YOUR_PAYER_ACCOUNT YOUR_TESTNET_CONTRACT 200000
# If audited contract deployment approved:
# proton contract:set YOUR_TESTNET_CONTRACT https://github.com/XPRNetwork/ts-smart-contracts/tree/main/external/xtokens
# If new token creation approved:
# proton action YOUR_TESTNET_CONTRACT create '{"issuer":"YOUR_TESTNET_CONTRACT","maximum_supply":"1000000.0000 GWTEST"}' YOUR_TESTNET_CONTRACT@active
# If issuance separately approved:
# proton action YOUR_TESTNET_CONTRACT issue '{"to":"YOUR_TESTNET_CONTRACT","quantity":"100000.0000 GWTEST","memo":"Testnet approved issuance"}' YOUR_TESTNET_CONTRACT@active
```

All commented commands are *examples* and must remain commented until a separate verified manual procedure. Replace placeholders with verified account information. This project intentionally does not automate these actions.

## 4. Read-only checks after an authorized transaction

For XPR CLI the signature is `proton table CONTRACT [TABLE] [SCOPE]`:

```bash
proton table YOUR_TESTNET_CONTRACT stat GWTEST
proton table YOUR_TESTNET_CONTRACT accounts YOUR_TESTNET_CONTRACT
```

Capture the on-chain transaction ID, network, authorization, stat row, current balance, and public code hash. Document any material difference from the approved plan.

## 5. Production release gate

- Complete independent code/security review, token issuer/reserve/rights analysis, and token-specific legal assessment.
- Obtain unambiguous authorization for production deployment, minting, token registry updates, wallet access, and any liquidity actions **separately**.
- Treat changes to contract ownership/permission as potentially irreversible. Do not copy blanket lockout instructions into this repository's runnable scripts.
- Use a dedicated production change request. Testnet success does not imply safety or correctness on mainnet.
