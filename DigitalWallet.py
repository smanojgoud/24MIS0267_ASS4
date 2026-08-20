import time
from datetime import datetime, timedelta

class Account:
    def __init__(self, account_id, pin, initial_balance=0.0):
        self.account_id = account_id
        self.pin = pin
        self.balance = float(initial_balance)
        self.failed_pin_attempts = 0
        self.is_locked = False
        self.history = []  # List of dicts: {'timestamp': float, 'type': str, 'amount': float, 'flagged': bool}

    def get_daily_total(self):
        """Calculates total money moved out of the account in the last 24 hours."""
        now = time.time()
        one_day_ago = now - 86400
        total = 0.0
        for tx in self.history:
            if tx['timestamp'] >= one_day_ago and tx['type'] in ['withdraw', 'transfer_out'] and not tx['flagged']:
                total += tx['amount']
        return total

    def get_average_transaction(self):
        """Calculates the average amount of past valid transactions."""
        valid_txs = [tx['amount'] for tx in self.history if not tx['flagged']]
        if not valid_txs:
            return 0.0
        return sum(valid_txs) / len(valid_txs)


class DigitalWalletSystem:
    def __init__(self):
        self.accounts = {}

    def create_account(self, account_id, pin, initial_balance=0.0):
        """Creates a new user account."""
        if initial_balance < 0:
            return "Error: Initial balance cannot be negative"
        if account_id in self.accounts:
            return "Error: Account already exists"
        self.accounts[account_id] = Account(account_id, pin, initial_balance)
        return "Success: Account created"

    def verify_balance(self, account_id, pin):
        """Checks balance securely after verification."""
        acc = self.accounts.get(account_id)
        if not acc:
            return "Error: Account not found"
        
        if acc.is_locked:
            return "Error: Account is locked due to multiple failed PIN attempts"

        if acc.pin != pin:
            acc.failed_pin_attempts += 1
            if acc.failed_pin_attempts >= 3:
                acc.is_locked = True
                return "Error: Account is locked due to multiple failed PIN attempts"
            return "Error: Invalid PIN"

        acc.failed_pin_attempts = 0  # Reset on successful login
        return acc.balance

    def check_fraud(self, acc, amount, recipient_id=None):
        """Runs basic fraud detection rules. Returns True if suspicious."""
        now = time.time()

        # 1. Velocity Check: More than 5 transactions in last 10 minutes
        ten_minutes_ago = now - 600
        recent_tx_count = sum(1 for tx in acc.history if tx['timestamp'] >= ten_minutes_ago)
        if recent_tx_count >= 5:
            return "Suspicious: High frequency transaction limit exceeded"

        # 2. Large Transaction Rule: Amount over $10,000
        if amount > 10000:
            return "Suspicious: Large transaction amount flagged"

        # 3. Unusual Transaction Amount: Exceeds 5x the account average (if history exists)
        avg_tx = acc.get_average_transaction()
        if avg_tx > 0 and amount > (avg_tx * 5):
            return "Suspicious: Unusual transaction amount compared to history"

        # 4. Duplicate Transaction: Exact same amount and recipient within last 2 seconds
        for tx in acc.history:
            if now - tx['timestamp'] <= 2:
                if tx['amount'] == amount and tx.get('recipient') == recipient_id:
                    return "Suspicious: Duplicate transaction detected"

        return None

    def deposit(self, account_id, amount):
        """Deposits funds into an account."""
        if amount <= 0:
            return "Error: Amount must be positive"
        acc = self.accounts.get(account_id)
        if not acc:
            return "Error: Account not found"

        acc.balance += amount
        acc.history.append({'timestamp': time.time(), 'type': 'deposit', 'amount': amount, 'flagged': False})
        return "Success"

    def withdraw(self, account_id, pin, amount):
        """Withdraws funds following verification and limits."""
        if amount <= 0:
            return "Error: Amount must be positive"
        
        acc = self.accounts.get(account_id)
        if not acc:
            return "Error: Account not found"

        # Security check: Failed PIN status
        if acc.is_locked:
            return "Error: Account locked"
        if acc.pin != pin:
            acc.failed_pin_attempts += 1
            if acc.failed_pin_attempts >= 3:
                acc.is_locked = True
            return "Error: Invalid PIN"

        # Financial check: Insufficient balance
        if amount > acc.balance:
            return "Error: Insufficient balance"

        # Limit check: Daily limit breach (e.g., $5,000 max withdrawal/transfer per day)
        if acc.get_daily_total() + amount > 5000:
            return "Error: Daily transaction limit exceeded"

        # Fraud rules check
        fraud_reason = self.check_fraud(acc, amount)
        if fraud_reason:
            acc.history.append({'timestamp': time.time(), 'type': 'withdraw', 'amount': amount, 'flagged': True})
            return fraud_reason

        # Execute transaction
        acc.balance -= amount
        acc.history.append({'timestamp': time.time(), 'type': 'withdraw', 'amount': amount, 'flagged': False})
        acc.failed_pin_attempts = 0
        return "Success"

    def transfer(self, sender_id, pin, receiver_id, amount):
        """Transfers money from sender to receiver safely."""
        if amount <= 0:
            return "Error: Amount must be positive"
        if sender_id == receiver_id:
            return "Error: Cannot transfer to self"

        sender = self.accounts.get(sender_id)
        receiver = self.accounts.get(receiver_id)
        if not sender or not receiver:
            return "Error: One or both accounts not found"

        if sender.is_locked:
            return "Error: Account locked"
        if sender.pin != pin:
            sender.failed_pin_attempts += 1
            if sender.failed_pin_attempts >= 3:
                sender.is_locked = True
            return "Error: Invalid PIN"

        if amount > sender.balance:
            return "Error: Insufficient balance"

        if sender.get_daily_total() + amount > 5000:
            return "Error: Daily transaction limit exceeded"

        # Fraud Check
        fraud_reason = self.check_fraud(sender, amount, receiver_id)
        if fraud_reason:
            sender.history.append({'timestamp': time.time(), 'type': 'transfer_out', 'amount': amount, 'recipient': receiver_id, 'flagged': True})
            return fraud_reason

        # Execute Transfer
        sender.balance -= amount
        receiver.balance += amount
        
        sender.history.append({'timestamp': time.time(), 'type': 'transfer_out', 'amount': amount, 'recipient': receiver_id, 'flagged': False})
        receiver.history.append({'timestamp': time.time(), 'type': 'transfer_in', 'amount': amount, 'sender': sender_id, 'flagged': False})
        
        sender.failed_pin_attempts = 0
        return "Success"
