import pytest
from datetime import datetime
from src.flight.FlightBookingSystem import FlightBookingSystem


@pytest.fixture
def fbs():
    return FlightBookingSystem()


def test_CT01_reserva_simples(fbs):
    booking_time = datetime(2025, 10, 1, 10, 0, 0)
    departure_time = datetime(2025, 10, 10, 14, 0, 0)
    result = fbs.book_flight(
        passengers=2,
        booking_time=booking_time,
        available_seats=50,
        current_price=500.0,
        previous_sales=25,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=0
    )
    print(result)
    assert result.confirmation == True
    assert result.total_price > 0
    assert result.refund_amount == 0.0
    assert result.points_used == False

def test_CT02_passageiros_excedem_assentos(fbs):
    booking_time = datetime(2025, 10, 1, 10, 0, 0)
    departure_time = datetime(2025, 10, 10, 14, 0, 0)
    result = fbs.book_flight(
        passengers=60,
        available_seats=50,
        booking_time=booking_time,
        current_price=1,
        previous_sales=1,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=0
    )
    assert result.confirmation == False
    assert result.total_price == 0.0
    assert result.refund_amount == 0.0
    assert result.points_used == False

def test_CT03_reserva_ultima_hora(fbs):
    booking_time = datetime(2025, 10, 1, 15, 0, 0)
    departure_time = datetime(2025, 10, 2, 10, 0, 0)
    result = fbs.book_flight(
        passengers=1,
        booking_time=booking_time,
        available_seats=30,
        current_price=300.0,
        previous_sales=50,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=0
    )
    assert result.confirmation == True
    assert result.total_price == 220.0
    assert result.refund_amount == 0.0
    assert result.points_used == False

def test_CT04_desconto_para_grupo(fbs):
    booking_time = datetime(2025, 9, 1, 10, 0, 0)
    departure_time = datetime(2025, 10, 15, 14, 0, 0)
    result = fbs.book_flight(
        passengers=5,
        booking_time=booking_time,
        available_seats=50,
        current_price=400.0,
        previous_sales=30,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=0
    )
    assert result.confirmation == True
    assert result.total_price == 456.0
    assert result.refund_amount == 0.0
    assert result.points_used == False

def test_CT05_uso_de_pontos_de_recompensa(fbs):
    booking_time = datetime(2025, 9, 20, 10, 0, 0)
    departure_time = datetime(2025, 10, 5, 14, 0, 0)
    result = fbs.book_flight(
        passengers=2,
        booking_time=booking_time,
        available_seats=40,
        current_price=600.0,
        previous_sales=40,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=5000
    )
    assert result.confirmation == True
    assert int(result.total_price) == 334
    assert result.refund_amount == 0.0
    assert result.points_used == True

def test_CT06_pontos_excessivos(fbs):
    booking_time = datetime(2025, 9, 25, 10, 0, 0)
    departure_time = datetime(2025, 10, 3, 14, 0, 0)
    result = fbs.book_flight(
        passengers=1,
        booking_time=booking_time,
        available_seats=50,
        current_price=200.0,
        previous_sales=10,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=10000
    )
    assert result.confirmation == True
    assert result.total_price == 0.0
    assert result.refund_amount == 0.0
    assert result.points_used == True


def test_CT07_cancelamento_com_reembolso_total(fbs):
    booking_time = datetime(2025, 9, 1, 10, 0, 0)
    departure_time = datetime(2025, 10, 10, 14, 0, 0)
    result = fbs.book_flight(
        passengers=3,
        booking_time=booking_time,
        available_seats=50,
        current_price=350.0,
        previous_sales=20,
        is_cancellation=True,
        departure_time=departure_time,
        reward_points_available=0
    )
    print(result)
    assert result.confirmation == False
    assert result.total_price == 0.0
    assert round(result.refund_amount, 1) == 168.0
    assert result.points_used == False

def test_CT08_cancelamento_com_reembolso_parcial(fbs):
    booking_time = datetime(2025, 10, 9, 15, 0, 0)
    departure_time = datetime(2025, 10, 11, 10, 0, 0)
    result = fbs.book_flight(
        passengers=2,
        booking_time=booking_time,
        available_seats=40,
        current_price=400.0,
        previous_sales=35,
        is_cancellation=True,
        departure_time=departure_time,
        reward_points_available=0
    )
    assert result.confirmation == False
    assert result.total_price == 0.0
    assert round(result.refund_amount, 1) == 112.0
    assert result.points_used == False

def test_CT09_ultimahora_grupo_pontos(fbs):
    booking_time = datetime(2025, 10, 9, 20, 0, 0)
    departure_time = datetime(2025, 10, 10, 14, 0, 0)
    result = fbs.book_flight(
        passengers=6,
        booking_time=booking_time,
        available_seats=50,
        current_price=500.0,
        previous_sales=45,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=3000
    )
    assert result.confirmation == True
    assert round(result.total_price, 1) == 1091.0
    assert result.refund_amount == 0.0
    assert result.points_used == True

def test_CT10_cancelamento_ultimahora(fbs):
    booking_time = datetime(2025, 10, 9, 20, 0, 0)
    departure_time = datetime(2025, 10, 10, 15, 0, 0)
    result = fbs.book_flight(
        passengers=1,
        booking_time=booking_time,
        available_seats=30,
        current_price=300.0,
        previous_sales=50,
        is_cancellation=True,
        departure_time=departure_time,
        reward_points_available=0
    )
    assert result.confirmation == False
    assert result.total_price == 0.0
    assert result.refund_amount == 110.0
    assert result.points_used == False