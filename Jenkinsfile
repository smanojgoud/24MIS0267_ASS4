pipeline {
    agent any
    stages {
        stage('🛠️ Setup') {
            steps {
                echo 'Checking Python environment...'
                sh 'python3 --version'
            }
        }
        stage('🧪 Test 1: Normal Transaction') {
            steps {
                sh 'python3 -m unittest WalletSecurityQA.py -k test_normal_transaction'
            }
        }
        stage('🧪 Test 2: Insufficient Balance') {
            steps {
                sh 'python3 -m unittest WalletSecurityQA.py -k test_insufficient_balance'
            }
        }
        stage('🧪 Test 3: Daily Limit Breach') {
            steps {
                sh 'python3 -m unittest WalletSecurityQA.py -k test_daily_limit'
            }
        }
        stage('🛡️ Test 4: Fraud Detection') {
            steps {
                sh 'python3 -m unittest WalletSecurityQA.py -k test_suspicious_transaction'
            }
        }
        stage('🛑 Test 5: Negative Amounts') {
            steps {
                sh 'python3 -m unittest WalletSecurityQA.py -k test_negative_amount'
            }
        }
    }
}
