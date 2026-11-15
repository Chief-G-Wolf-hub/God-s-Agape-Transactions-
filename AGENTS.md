# Coding agent instructions — XPR token project

Objective: Consolidate owner's existing XPR Network token inventory and develop an auditable token-management system. Use tests, pull requests, and peer review before deploying.

1. Never assume an existing token is undeployed. Verify contract account, symbol, circulating supply, maximum supply, precision, and issuer rights from chain data before suggesting any create/issue/retire actions.
2. Do not create new chains, bridge assets, change wallet permissions, publish secrets, push transactions, or transfer assets without distinct human authorization.
3. All generated plans target `proton-test` only. Keep mainnet deployment out of scripts until separate approval and independent contract audit.
4. Keep ledger records for code version, approval, signer, transaction ID, resource costs, and asset-specific permissions.
5. No invented values for reserves, backing, liquidity, redemption rights, or asset ownership. Separate a liquidity-pair quote from real asset backing.
6. Protect private keys and seed phrases: never log or commit them. Use wallet signing or secure signing mechanisms.
7. Run `python3 -m unittest discover -s tests -v` after changes. Keep the README and the inventory current.
8. Match implementation to documented XPR Network CLI and contracts, checking upstream changes before deployment.
9. Do not merge to GitHub main automatically. Produce a reviewable pull request after tests and owner approval.
