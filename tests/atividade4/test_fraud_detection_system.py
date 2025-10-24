import pytest
from datetime import datetime, timedelta
from src.fraud.FraudDetectionSystem import FraudDetectionSystem
from src.fraud.Transaction import Transaction
from src.fraud.FraudCheckResult import FraudCheckResult


def create_previous_transactions(
    count, start_time, interval_minutes, location, amounts
):
    transactions = []
    for i in range(count):
        timestamp = start_time - timedelta(minutes=i * interval_minutes)
        amount = amounts[i % len(amounts)]
        transactions.append(
            Transaction(amount=amount, timestamp=timestamp, location=location)
        )
    return list(reversed(transactions))


@pytest.fixture
def fds():
    return FraudDetectionSystem()


def test_CT01_transacao_normal(fds):
    current = Transaction(
        amount=5000, timestamp=datetime(2025, 10, 1, 12, 0, 0), location="Brasil"
    )
    previous = create_previous_transactions(
        5,
        datetime(2025, 10, 1, 12, 0, 0),
        interval_minutes=600,
        location="Brasil",
        amounts=[100, 200, 300, 400, 500],
    )
    blacklist = ["País de Alto Risco", "Irã", "Coreia do Norte"]
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent == False
    assert result.is_blocked == False
    assert result.verification_required == False
    assert result.risk_score == 0


def test_CT02_valor_elevado(fds):
    current = Transaction(
        amount=15000, timestamp=datetime(2025, 10, 1, 14, 0, 0), location="Brasil"
    )
    previous = []
    blacklist = ["País de Alto Risco"]
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent == True
    assert result.is_blocked == False
    assert result.verification_required == True
    assert result.risk_score == 50


def test_CT03_excesso_transacoes(fds):
    current = Transaction(
        amount=200, timestamp=datetime(2025, 10, 1, 13, 0, 0), location="Brasil"
    )
    previous = create_previous_transactions(
        12,
        datetime(2025, 10, 1, 13, 0, 0),
        interval_minutes=5,
        location="Brasil",
        amounts=[50, 100, 150, 200, 250, 300],
    )
    blacklist = ["País de Alto Risco"]
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent == False
    assert result.is_blocked == True
    assert result.verification_required == False
    assert result.risk_score == 30


def test_CT04_mudanca_localizacao_rapida(fds):
    current = Transaction(
        amount=800,
        timestamp=datetime(2025, 10, 1, 12, 25, 0),
        location="Estados Unidos",
    )
    previous = [
        Transaction(
            amount=300, timestamp=datetime(2025, 10, 1, 12, 0, 0), location="Brasil"
        )
    ]
    blacklist = ["País de Alto Risco"]
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent == True
    assert result.is_blocked == False
    assert result.verification_required == True
    assert result.risk_score == 20


def test_CT05_localizacao_blacklist(fds):
    current = Transaction(
        amount=150,
        timestamp=datetime(2025, 10, 1, 10, 0, 0),
        location="País de Alto Risco",
    )
    previous = []
    blacklist = ["País de Alto Risco", "Irã"]
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent == False
    assert result.is_blocked == True
    assert result.verification_required == False
    assert result.risk_score == 100


def test_CT06_valor_alto_mudanca_localizacao(fds):
    current = Transaction(
        amount=12000, timestamp=datetime(2025, 10, 1, 14, 20, 0), location="França"
    )
    previous = [
        Transaction(
            amount=500, timestamp=datetime(2025, 10, 1, 14, 0, 0), location="Brasil"
        )
    ]
    blacklist = ["País de Alto Risco"]
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent == True
    assert result.is_blocked == False
    assert result.verification_required == True
    assert result.risk_score == 70


def test_CT07_valor_alto_excesso_transacoes(fds):
    current = Transaction(
        amount=11500, timestamp=datetime(2025, 10, 1, 15, 0, 0), location="Brasil"
    )
    previous = create_previous_transactions(
        11,
        datetime(2025, 10, 1, 15, 0, 0),
        interval_minutes=5,
        location="Brasil",
        amounts=[100] * 11,
    )
    blacklist = ["País de Alto Risco"]
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent == True
    assert result.is_blocked == True
    assert result.verification_required == True
    assert result.risk_score == 80


def test_CT08_mudanca_local_lenta(fds):
    current = Transaction(
        amount=600, timestamp=datetime(2025, 10, 1, 13, 0, 0), location="Portugal"
    )
    previous = [
        Transaction(
            amount=200, timestamp=datetime(2025, 10, 1, 12, 0, 0), location="Brasil"
        )
    ]
    blacklist = ["País de Alto Risco"]
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent == False
    assert result.is_blocked == False
    assert result.verification_required == False
    assert result.risk_score == 0


def test_CT09_transacao_recente_mesma_localizacao(fds):
    current = Transaction(
        amount=400, timestamp=datetime(2025, 10, 1, 12, 15, 0), location="Brasil"
    )
    previous = [
        Transaction(
            amount=250, timestamp=datetime(2025, 10, 1, 12, 0, 0), location="Brasil"
        )
    ]
    blacklist = ["País de Alto Risco"]
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent == False
    assert result.is_blocked == False
    assert result.verification_required == False
    assert result.risk_score == 0


def test_repr_methods():
    t = Transaction(100, datetime.now(), "Brasil")
    f = FraudCheckResult(False, False, False, 0)

    assert repr(t) is not None
    assert repr(f) is not None
