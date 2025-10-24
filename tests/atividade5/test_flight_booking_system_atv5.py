import pytest
from datetime import datetime
from src.flight.FlightBookingSystem import FlightBookingSystem

@pytest.fixture
def fbs():
    return FlightBookingSystem()

def test_CT11_fronteira_assentos_iguais_reserva(fbs):
    """
    Objetivo: matar o mutante (>) -> (>=) na verificação de assentos.
    Cenário de fronteira: passengers == available_seats deve permitir reservar.
    """

    booking_time    = datetime(2025, 10, 1, 10, 0, 0)
    departure_time  = datetime(2025, 10, 10, 10, 0, 0)
    passengers      = 3
    available_seats = 3
    current_price   = 100.0
    previous_sales  = 10 
    is_cancellation = False
    reward_points   = 0

    result = fbs.book_flight(
        passengers=passengers,
        available_seats=available_seats,
        booking_time=booking_time,
        current_price=current_price,
        previous_sales=previous_sales,
        is_cancellation=is_cancellation,
        departure_time=departure_time,
        reward_points_available=reward_points
    )

    assert result.confirmation is True, "Reserva deveria ser confirmada na igualdade (==)."
    assert round(result.total_price,1) == 24.0, "Preço total calculado incorretamente."
    assert result.refund_amount == 0.0, "Cancelamento não solicitado; reembolso deve ser 0.0."
    assert result.points_used is False, "Sem pontos; points_used deve ser False."


def test_CT12_limite_24h_sem_taxa_ultima_hora(fbs):
    """
    Objetivo: matar o mutante (divisor 3600 -> 3601) na fronteira de 24h.
    No original, exatamente 24h NÃO aplica taxa de última hora; no mutante, aplica.
    """

    booking_time    = datetime(2025, 10, 1, 10, 0, 0)
    departure_time  = datetime(2025, 10, 2, 10, 0, 0)
    passengers      = 1
    available_seats = 10
    current_price   = 100.0
    previous_sales  = 50
    is_cancellation = False
    reward_points   = 0

    result = fbs.book_flight(
        passengers=passengers,
        available_seats=available_seats,
        booking_time=booking_time,
        current_price=current_price,
        previous_sales=previous_sales,
        is_cancellation=is_cancellation,
        departure_time=departure_time,
        reward_points_available=reward_points
    )

    assert result.confirmation is True
    assert result.total_price == 40.0
    assert result.refund_amount == 0.0
    assert result.points_used is False


def test_CT13_limite_48h_reembolso_total(fbs):
    """
    Objetivo: matar o mutante (divisor 3600 -> 3601) na fronteira de 48h (cancelamento).
    No original, exatamente 48h garante reembolso integral; no mutante, vira parcial (50%).
    """

    booking_time    = datetime(2025, 10, 1, 10, 0, 0)
    departure_time  = datetime(2025, 10, 3, 10, 0, 0)
    passengers      = 2
    available_seats = 10
    current_price   = 250.0
    previous_sales  = 40
    is_cancellation = True
    reward_points   = 0

    result = fbs.book_flight(
        passengers=passengers,
        available_seats=available_seats,
        booking_time=booking_time,
        current_price=current_price,
        previous_sales=previous_sales,
        is_cancellation=is_cancellation,
        departure_time=departure_time,
        reward_points_available=reward_points
    )

    assert result.confirmation is False
    assert result.total_price == 0.0
    assert round(result.refund_amount,1) == 160.0
    assert result.points_used is False

def test_CT14_quatro_passageiros_sem_desconto(fbs):
    """
    Objetivo: matar o mutante que altera a fronteira do desconto de grupo
    de (>4) para (>=4). No original, exatamente 4 passageiros NÃO recebem
    5% de desconto; no mutante, receberiam.
    """
    booking_time    = datetime(2025, 10, 1, 10, 0, 0)
    departure_time  = datetime(2025, 10, 10, 10, 0, 0)
    passengers      = 4
    available_seats = 50
    current_price   = 200.0
    previous_sales  = 50
    is_cancellation = False
    reward_points   = 0

    result = fbs.book_flight(
        passengers=passengers,
        available_seats=available_seats,
        booking_time=booking_time,
        current_price=current_price,
        previous_sales=previous_sales,
        is_cancellation=is_cancellation,
        departure_time=departure_time,
        reward_points_available=reward_points
    )

    assert result.confirmation is True, "Reserva deveria ser confirmada."
    assert result.total_price == 320.0, "No mutante (>=4) aplicaria 5% e daria 304.0."
    assert result.refund_amount == 0.0, "Sem cancelamento; reembolso deve ser 0.0."
    assert result.points_used is False, "Sem pontos; points_used deve ser False."

def test_CT15_um_ponto_reserva_aplica_desconto(fbs):
    """
    Objetivo: matar o mutante que altera o limiar do resgate de pontos de (>0) para (>1).
    No original, 1 ponto já aplica desconto de 0.01 e marca points_used=True;
    no mutante, não aplica desconto e points_used=False.
    """

    booking_time    = datetime(2025, 10, 1, 10, 0, 0)
    departure_time  = datetime(2025, 10, 2, 16, 0, 0)
    passengers      = 1
    available_seats = 10
    current_price   = 100.0
    previous_sales  = 50
    is_cancellation = False
    reward_points   = 1

    result = fbs.book_flight(
        passengers=passengers,
        available_seats=available_seats,
        booking_time=booking_time,
        current_price=current_price,
        previous_sales=previous_sales,
        is_cancellation=is_cancellation,
        departure_time=departure_time,
        reward_points_available=reward_points
    )

    assert result.confirmation is True
    assert round(result.total_price, 2) == 39.99
    assert result.refund_amount == 0.0
    assert result.points_used is True

def test_CT16_preco_entre_0e1_sem_clamp(fbs):
    """
    Objetivo: matar o mutante que altera o clamp de (final_price < 0) para (final_price < 1).
    Cenário de reserva com final_price ∈ (0,1): no original mantém-se >0; no mutante zera (0).
    """

    booking_time    = datetime(2025, 10, 1, 10, 0, 0)
    departure_time  = datetime(2025, 10, 2, 16, 0, 0)
    passengers      = 1
    available_seats = 10
    current_price   = 100.0
    previous_sales  = 50
    is_cancellation = False
    reward_points   = 3999

    result = fbs.book_flight(
        passengers=passengers,
        available_seats=available_seats,
        booking_time=booking_time,
        current_price=current_price,
        previous_sales=previous_sales,
        is_cancellation=is_cancellation,
        departure_time=departure_time,
        reward_points_available=reward_points
    )

    assert result.confirmation is True
    assert round(result.total_price, 2) == 0.01
    assert result.refund_amount == 0.0
    assert result.points_used is True
