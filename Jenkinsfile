pipeline {
    agent any
    stages {
        stage('🛠️ Setup') {
            steps {
                echo 'Checking Python environment installation paths...'
                // Try executing with Python fallback routes safely
                sh 'python3 --version || python --version || echo "Python command fallback activated"'
            }
        }
        stage('🧪 Test 1: Normal Transaction') {
            steps {
                // Tries python3 first, falls back to python if needed
                sh 'python3 -m unittest WalletSecurityQA.py -k test_normal_transaction || python -m unittest WalletSecurityQA.py -k test_normal_transaction'
            }
        }
        stage('🧪 Test 2: Insufficient Balance') {
            steps {
                sh 'python3 -m unittest WalletSecurityQA.py -k test_insufficient_balance || python -m unittest WalletSecurityQA.py -k test_insufficient_balance'
            }
        }
        stage('🧪 Test 3: Daily Limit Breach') {
            steps {
                sh 'python3 -m unittest WalletSecurityQA.py -k test_daily_limit || python -m unittest WalletSecurityQA.py -k test_daily_limit'
            }
        }
        stage('🛡️ Test 4: Fraud Detection') {
            steps {
                sh 'python3 -m unittest WalletSecurityQA.py -k test_suspicious_transaction || python -m unittest WalletSecurityQA.py -k test_suspicious_transaction'
            }
        }
        stage('🛑 Test 5: Negative Amounts') {
            steps {
                sh 'python3 -m unittest WalletSecurityQA.py -k test_negative_amount || python -m unittest WalletSecurityQA.py -k test_negative_amount'
            }
        }
    }
}
