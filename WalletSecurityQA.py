import unittest
import time
import threading
from DigitalWallet import DigitalWalletSystem

class TestWalletSecurityQA(unittest.TestCase):

    def setUp(self):
        """Runs automatically before every single test case."""
        self.sys = DigitalWalletSystem()
        self.sys.create_account("ACC123", "1111", initial_balance=2000.0)
        self.sys.create_account("ACC456", "2222", initial_balance=500.0)

    def test_normal_transaction(self):
        """1. Tests standard safe deposit and withdrawal actions."""
        dep_res = self.sys.deposit("ACC123", 500.0)
        self.assertEqual(dep_res, "Success")
        
        with_res = self.sys.withdraw("ACC123", "1111", 300.0)
        self.assertEqual(with_res, "Success")
        self.assertEqual(self.sys.verify_balance("ACC123", "1111"), 2200.0)

    def test_insufficient_balance(self):
        """2. Tests that accounts cannot overdraft past zero."""
        result = self.sys.withdraw("ACC123", "1111", 2500.0)
        self.assertEqual(result, "Error: Insufficient balance")

    def test_daily_limit(self):
        """3. Tests that transactions blocking occurs when daily caps are broken."""
        # Top up account to have plenty of cash
        self.sys.deposit("ACC123", 10000.0)
        
        # Withdraw $4500 (Allowed)
        self.sys.withdraw("ACC123", "1111", 4500.0)
        
        # Attempting another $1000 breaches the $5000 daily limit rule
        result = self.sys.withdraw("ACC123", "1111", 1000.0)
        self.assertEqual(result, "Error: Daily transaction limit exceeded")

    def test_multiple_failed_pins(self):
        """4. Tests security locks kicking in after multiple bad entries."""
        self.sys.verify_balance("ACC123", "9999") # Fail 1
        self.sys.verify_balance("ACC123", "8888") # Fail 2
        result = self.sys.verify_balance("ACC123", "7777") # Fail 3 -> Locks Account
        
        self.assertIn("locked", result.lower())
        
        # Ensure even a correct attempt is blocked now
        blocked_res = self.sys.withdraw("ACC123", "1111", 100.0)
        self.assertEqual(blocked_res, "Error: Account locked")

    def test_suspicious_transaction(self):
        """5. Tests that an over-the-top large value triggers fraud flags."""
        self.sys.create_account("WHALE", "1234", initial_balance=50000.0)
        result = self.sys.withdraw("WHALE", "1234", 15000.0) # > $10,000 threshold
        self.assertIn("Suspicious", result)

    def test_duplicate_transaction(self):
        """6. Tests rapid repetitive inputs to block duplicate accidents."""
        # First transaction
        res1 = self.sys.transfer("ACC123", "1111", "ACC456", 50.0)
        self.assertEqual(res1, "Success")
        
        # Instant second transaction with identical properties should be flagged
        res2 = self.sys.transfer("ACC123", "1111", "ACC456", 50.0)
        self.assertIn("Duplicate transaction detected", res2)

    def test_negative_amount(self):
        """7. Tests that negative numerical inputs are rejected immediately."""
        res_dep = self.sys.deposit("ACC123", -100.0)
        res_wit = self.sys.withdraw("ACC123", "1111", -50.0)
        
        self.assertEqual(res_dep, "Error: Amount must be positive")
        self.assertEqual(res_wit, "Error: Amount must be positive")

    def test_concurrent_transactions(self):
        """8. Tests processing multi-threaded transaction safety using Python threads."""
        results = []

        def worker():
            res = self.sys.withdraw("ACC123", "1111", 1500.0)
            results.append(res)

        # Thread 1 and Thread 2 will fire simultaneously to withdraw $1500 each.
        # Only one should succeed since balance is only $2000!
        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # One should succeed, one must fail because $1500 + $1500 > $2000 balance
        self.assertTrue("Success" in results)
        self.assertTrue("Error: Insufficient balance" in results or "Suspicious: High frequency transaction limit exceeded" in results)

if __name__ == '__main__':
    unittest.main()
