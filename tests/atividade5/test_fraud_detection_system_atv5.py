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


def test_boundary_amount_equal(fds):
    """Teste do limite exato do valor: NÃO deve acionar fraude (mutantes: 74, 80)"""
    current = Transaction(
        amount=10000, timestamp=datetime(2025, 10, 1, 12, 0, 0), location="Brasil"
    )
    previous = []
    blacklist = []
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent is False
    assert result.verification_required is False
    assert result.risk_score == 0


def test_boundary_amount_above(fds):
    """Teste ligeiramente acima do limite: deve acionar fraude (mutantes: 74, 75, 80)"""
    current = Transaction(
        amount=10001, timestamp=datetime(2025, 10, 1, 12, 0, 0), location="Brasil"
    )
    previous = []
    blacklist = []
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent is True
    assert result.verification_required is True
    assert result.risk_score == 50


def test_boundary_transaction_count(fds):
    """Teste de exatamente 10 transações em 60 minutos: NÃO deve acionar bloqueio (mutantes: 83, 88, 90, 91, 94, 95)"""
    current = Transaction(
        amount=100, timestamp=datetime(2025, 10, 1, 12, 0, 0), location="Brasil"
    )
    previous = create_previous_transactions(
        10,
        datetime(2025, 10, 1, 12, 0, 0),
        interval_minutes=5,
        location="Brasil",
        amounts=[50] * 10,
    )
    blacklist = []
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_blocked is False
    assert result.risk_score == 0


def test_boundary_time_exact_30(fds):
    """Teste de diferença exata de 30 minutos: NÃO deve acionar fraude por localização (mutantes: 108, 110, 111)"""
    current = Transaction(
        amount=100,
        timestamp=datetime(2025, 10, 1, 12, 30, 0),
        location="Estados Unidos",
    )
    previous = [
        Transaction(
            amount=50, timestamp=datetime(2025, 10, 1, 12, 0, 0), location="Brasil"
        )
    ]
    blacklist = []
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_fraudulent is False
    assert result.verification_required is False
    assert result.risk_score == 0


def test_boundary_time_exact_60(fds):
    """Teste da janela exata de 60 minutos: NÃO deve acionar regra de transações excessivas (mutantes: 83, 88, 90, 91, 94, 95)"""
    current = Transaction(
        amount=100, timestamp=datetime(2025, 10, 1, 13, 0, 0), location="Brasil"
    )
    previous = create_previous_transactions(
        10,
        datetime(2025, 10, 1, 13, 0, 0),
        interval_minutes=6,
        location="Brasil",
        amounts=[50] * 10,
    )
    blacklist = []
    result = fds.check_for_fraud(current, previous, blacklist)
    assert result.is_blocked is False  # apenas 10 transações, limite é >10
    assert result.risk_score == 0


def test_time_diff_boundary_less_than_60(fds):
    """
    Mutantes #88 e #90: Detecta mudança de <=60 para <60 minutos
    """
    base_time = datetime(2025, 10, 1, 12, 0, 0)
    previous = [
        Transaction(
            amount=100, timestamp=base_time - timedelta(minutes=60), location="Brasil"
        )
        for _ in range(11)
    ]
    current = Transaction(amount=200, timestamp=base_time, location="Brasil")
    result = fds.check_for_fraud(current, previous, [])
    # Diferença de 60 minutos ainda deve contar (<= 60)
    assert result.is_blocked, "Exatamente 60 minutos devem estar incluídos na janela"


def test_time_diff_boundary_more_than_60(fds):
    """
    Mutante #91: Detecta mudança de <=60 para <=61 minutos
    """
    base_time = datetime(2025, 10, 1, 12, 0, 0)
    previous = [
        Transaction(
            amount=100, timestamp=base_time - timedelta(minutes=61), location="Brasil"
        )
        for _ in range(11)
    ]
    current = Transaction(amount=200, timestamp=base_time, location="Brasil")
    result = fds.check_for_fraud(current, previous, [])
    assert not result.is_blocked, "61 minutos devem estar fora da janela de 60 minutos"
