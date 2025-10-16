import pytest
from datetime import datetime
from src.energy.EnergyManagementSystem import EnergyManagementSystem
from src.energy.DeviceSchedule import DeviceSchedule
from src.energy.EnergyManagementResult import EnergyManagementResult

@pytest.fixture
def ems():
    return EnergyManagementSystem()


def test_CT01_operacao_normal(ems):
    initial_device_status = {"Light": False, "TV": False, "AC": False}
    current_time = datetime(2025, 10, 15, 14, 0, 0)
    device_priorities = {"Light": 2, "TV": 1, "AC": 3}
    
    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=False,
        temperature_regulation_active=False,
        current_price=0.15,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=50.0,
        scheduled_devices=[],
    )

    expected_status = {"Light": False, "TV": False, "AC": False}
    assert result.device_status == expected_status
    # CORREÇÃO: Removido o '_active'
    assert result.energy_saving_mode == False
    assert result.temperature_regulation_active == False
    assert result.total_energy_used == 50.0
    assert result.devices_were_on == False


def test_CT02_modo_economia_ativado(ems):
    initial_device_status = {"Light": False, "TV": False, "Heater": False}
    current_time = datetime(2025, 10, 15, 15, 0, 0)
    device_priorities = {"Light": 2, "TV": 1, "Heater": 3}
    
    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=True,
        temperature_regulation_active=False,
        current_price=0.15,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=30.0,
        scheduled_devices=[],
    )

    expected_status = {"Light": False, "TV": False, "Heater": False}
    assert result.device_status == expected_status
    # CORREÇÃO: Removido o '_active'
    assert result.energy_saving_mode == True


def test_CT03_dispositivos_prioritarios(ems):
    initial_device_status = {"Light": True, "Refrigerator": True, "TV": True}
    current_time = datetime(2025, 10, 15, 10, 0, 0)
    device_priorities = {"Light": 3, "Refrigerator": 2, "TV": 1}
    
    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=False,
        temperature_regulation_active=False,
        current_price=0.25,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=40.0,
        scheduled_devices=[],
    )
    
    expected_status = {"Light": False, "Refrigerator": False, "TV": True}
    assert result.device_status == expected_status


def test_CT04_horario_noturno(ems):
    initial_device_status = {"Washing Machine": True, "Dryer": True, "Security": False, "Refrigerator": True}
    current_time = datetime(2025, 10, 15, 23, 30, 0)
    device_priorities = {"Washing Machine": 2, "Dryer": 1, "Security": 1, "Refrigerator": 1}

    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=False,
        temperature_regulation_active=False,
        current_price=0.15,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=60.0,
        scheduled_devices=[],
    )

    expected_status = {"Washing Machine": False, "Dryer": False, "Security": False, "Refrigerator": True}
    assert result.device_status == expected_status


def test_CT05_regulacao_temperatura_aquecimento(ems):
    initial_device_status = {"Heating": False, "Light": False}
    current_time = datetime(2025, 10, 15, 8, 0, 0)
    device_priorities = {"Heating": 3, "Light": 2}

    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=False,
        temperature_regulation_active=True,
        current_price=0.15,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=18.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=20.0,
        scheduled_devices=[],
    )

    expected_status = {"Heating": True, "Light": False}
    assert result.device_status == expected_status
    assert result.temperature_regulation_active == True


def test_CT06_regulacao_temperatura_resfriamento(ems):
    initial_device_status = {"Cooling": False, "AC": False}
    current_time = datetime(2025, 10, 15, 14, 0, 0)
    device_priorities = {"Cooling": 3, "AC": 2}

    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=False,
        temperature_regulation_active=True,
        current_price=0.15,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=28.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=30.0,
        scheduled_devices=[],
    )
    
    expected_status = {"Cooling": True, "AC": False}
    assert result.device_status == expected_status
    assert result.temperature_regulation_active == True

def test_CT07_limite_energia_excedido(ems):
    initial_device_status = {"TV": True, "Gaming Console": True, "Stereo": True}
    current_time = datetime(2025, 10, 15, 16, 0, 0)
    device_priorities = {"TV": 2, "Gaming Console": 1, "Stereo": 1}

    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=False,
        temperature_regulation_active=False,
        current_price=0.15,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=110.0,
        scheduled_devices=[],
    )
    
    expected_status = {'TV': False, 'Gaming Console': False, 'Stereo': False}
    assert result.device_status == expected_status

def test_CT08_agendamento_dispositivos(ems):
    initial_device_status = {"Dishwasher": False, "Washing Machine": False}
    schedule_time = datetime(2025, 10, 15, 2, 0, 0)
    device_priorities = {"Dishwasher": 1, "Washing Machine": 1}
    scheduled_devices = [DeviceSchedule("Dishwasher", schedule_time)]

    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=False,
        temperature_regulation_active=False,
        current_price=0.30,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=schedule_time,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=40.0,
        scheduled_devices=scheduled_devices,
    )

    expected_status = {"Dishwasher": True, "Washing Machine": False}
    assert result.device_status == expected_status

def test_CT09_preco_acima_threshold(ems):
    initial_device_status = {"Water Heater": True, "Dryer": True}
    current_time = datetime(2025, 10, 15, 18, 0, 0)
    device_priorities = {"Water Heater": 2, "Dryer": 1}

    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=False,
        temperature_regulation_active=False,
        current_price=0.25,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=50.0,
        scheduled_devices=[],
    )

    expected_status = {"Water Heater": False, "Dryer": True}
    assert result.device_status == expected_status

def test_CT10_combinacao_multipla(ems):
    initial_device_status = {"Heating": False, "Light": True, "TV": True, "Security": False, "Refrigerator": True}
    current_time = datetime(2025, 10, 15, 23, 0, 0)
    device_priorities = {"Heating": 3, "Light": 2, "TV": 1, "Security": 1, "Refrigerator": 1}
    
    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=True,
        temperature_regulation_active=True,
        current_price=0.18,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=17.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=95.0,
        scheduled_devices=[],
    )

    expected_status = {'Heating': True, 'Light': False, 'TV': False, 'Security': False, 'Refrigerator': True}
    assert result.device_status == expected_status

def test_CT11_temperatura_na_faixa(ems):
    initial_device_status = {"Heating": False, "Cooling": False}
    current_time = datetime(2025, 10, 15, 12, 0, 0)
    device_priorities = {"Heating": 3, "Cooling": 3}
    
    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=False,
        temperature_regulation_active=True,
        current_price=0.15,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=100.0,
        total_energy_used_today=40.0,
        scheduled_devices=[],
    )

    expected_status = {"Heating": False, "Cooling": False}
    assert result.device_status == expected_status

def test_CT12_loop_desligamento_parcial(ems):
    initial_device_status = {"Dev1": True, "Dev2": True, "Dev3": True}
    current_time = datetime(2025, 10, 15, 10, 0, 0)
    device_priorities = {"Dev1": 3, "Dev2": 1, "Dev3": 1}
    
    result = ems.manage_energy(
        initial_device_status=initial_device_status,
        energy_saving_mode=False,
        temperature_regulation_active=False,
        current_price=0.15,
        price_threshold=0.20,
        device_priorities=device_priorities,
        current_time=current_time,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 25.0),
        energy_usage_limit=50.0,
        total_energy_used_today=90.0,
        scheduled_devices=[],
    )

    expected_status = {'Dev1': False, 'Dev2': False, 'Dev3': False}
    assert result.device_status == expected_status

def test_repr_methods():
    schedule = DeviceSchedule("Forno", datetime.now())
    result = EnergyManagementResult({}, False, False, 0.0, True)
    assert repr(schedule) is not None
    assert repr(result) is not None