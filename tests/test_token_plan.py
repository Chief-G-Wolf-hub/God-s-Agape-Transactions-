import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from token_plan import build_plan, PlanError, format_amount

BASE = {
    "chain": "proton-test", "contract_account": "gwtesttoken",
    "issuer": "gwtesttoken", "initial_recipient": "gwtesttoken",
    "symbol": "GWTEST", "precision": 4, "maximum_supply": "1000000",
    "initial_issue": "100000", "ram_bytes": 200000,
}

class PlanTests(unittest.TestCase):
    def test_dry_run_has_no_executable_mutations(self):
        lines = build_plan(BASE)
        executable = [x for x in lines if not x.startswith("#")]
        self.assertTrue(any("proton chain:set proton-test" == x for x in executable))
        self.assertFalse(any(" contract:set " in x or " issue " in x or " create " in x for x in executable))
        self.assertTrue(any("1000000.0000 GWTEST" in x for x in lines))

    def test_reject_mainnet(self):
        cfg = dict(BASE, chain="proton")
        with self.assertRaises(PlanError): build_plan(cfg)

    def test_reject_fractional_oversupply(self):
        cfg = dict(BASE, initial_issue="1000000.0001")
        with self.assertRaises(PlanError): build_plan(cfg)

    def test_reject_long_symbol(self):
        cfg = dict(BASE, symbol="SAFEPASSAGE")
        with self.assertRaises(PlanError): build_plan(cfg)

    def test_reject_float_supply(self):
        cfg = dict(BASE, maximum_supply=1000000.1)
        with self.assertRaises(PlanError): build_plan(cfg)

    def test_reject_supply_over_int64(self):
        cfg = dict(BASE, precision=9, maximum_supply="999999999999")
        with self.assertRaises(PlanError): build_plan(cfg)

    def test_format_decimal(self):
        self.assertEqual(format_amount("2.5", 4), "2.5000")

    def test_reject_invalid_account(self):
        cfg = dict(BASE, contract_account="account0", issuer="account0")
        with self.assertRaises(PlanError): build_plan(cfg)

if __name__ == "__main__":
    unittest.main()
