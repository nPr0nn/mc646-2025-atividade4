from datetime import datetime
from src.energy.DeviceSchedule import DeviceSchedule
from src.energy.EnergyManagementResult import EnergyManagementResult

class EnergyManagementSystem:
    """Um sistema para gerenciar inteligentemente o consumo de energia."""
    def manage_energy(
        self,
        # Parâmetros que foram adicionados para receber o estado inicial do teste
        initial_device_status: dict[str, bool],
        energy_saving_mode: bool,
        temperature_regulation_active: bool,
        
        # Parâmetros que já estavam corretos
        current_price: float,
        price_threshold: float,
        device_priorities: dict[str, int],
        current_time: datetime,
        current_temperature: float,
        desired_temperature_range: tuple[float, float],
        energy_usage_limit: float,
        total_energy_used_today: float,
        scheduled_devices: list[DeviceSchedule],
    ) -> EnergyManagementResult:

        # Usamos uma cópia para não modificar o dicionário original passado pelo teste
        device_status = initial_device_status.copy()
        
        # Variáveis para rastrear o estado atual, que pode ser modificado pela lógica
        current_energy_saving_mode = energy_saving_mode
        current_temp_regulation_active = temperature_regulation_active

        # 1. Ativa o modo de economia de energia se o preço exceder o limite
        if current_price > price_threshold:
            current_energy_saving_mode = True
        
        # Aplica as regras do modo de economia (seja forçado por parâmetro ou pelo preço)
        if current_energy_saving_mode:
            for device, priority in device_priorities.items():
                if priority > 1:
                    device_status[device] = False

        # 2. Modo noturno entre 23h e 6h (sobrepõe outras regras)
        if current_time.hour >= 23 or current_time.hour < 6:
            for device in device_priorities:
                if device not in ("Security", "Refrigerator"):
                    device_status[device] = False

        # 3. Regulação de temperatura (só se o modo estiver ativo)
        if temperature_regulation_active:
            if current_temperature < desired_temperature_range[0]:
                if "Heating" in device_status:
                    device_status["Heating"] = True
            elif current_temperature > desired_temperature_range[1]:
                if "Cooling" in device_status:
                    device_status["Cooling"] = True

        devices_were_on = any(initial_device_status.values())

        # 4. Limite de consumo de energia
        if total_energy_used_today >= energy_usage_limit:
            devices_were_on = False # Assume que algo será desligado
            # Desliga primeiro os de baixa prioridade (maior número)
            low_prio_devices = sorted([d for d, p in device_priorities.items() if p > 1], key=lambda d: device_priorities[d], reverse=True)
            for device in low_prio_devices:
                if device_status.get(device, False):
                    device_status[device] = False
            
            # Se ainda não for suficiente, desliga os de alta prioridade
            high_prio_devices = sorted([d for d, p in device_priorities.items() if p <= 1], key=lambda d: device_priorities[d], reverse=True)
            for device in high_prio_devices:
                 if device_status.get(device, False):
                    device_status[device] = False

        # 5. Lida com dispositivos agendados (sobrepõe tudo)
        for schedule in scheduled_devices:
            if schedule.scheduled_time.hour == current_time.hour and schedule.scheduled_time.minute == current_time.minute:
                device_status[schedule.device_name] = True

        # Retorno da função com todos os 5 parâmetros esperados
        return EnergyManagementResult(
            device_status,
            current_energy_saving_mode,
            current_temp_regulation_active,
            total_energy_used_today,
            devices_were_on
        )