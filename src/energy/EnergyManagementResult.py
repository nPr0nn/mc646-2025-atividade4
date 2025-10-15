class EnergyManagementResult:
    """Armazena os resultados da lógica de gerenciamento de energia."""
    def __init__(
        self,
        device_status: dict[str, bool],
        energy_saving_mode: bool,
        temperature_regulation_active: bool,
        total_energy_used: float,
        devices_were_on: bool,  # Parâmetro que estava faltando
    ):
        self.device_status = device_status
        self.energy_saving_mode = energy_saving_mode
        self.temperature_regulation_active = temperature_regulation_active
        self.total_energy_used = total_energy_used
        self.devices_were_on = devices_were_on  # Atribuição do novo parâmetro

    def __repr__(self) -> str:
        """Retorna uma representação legível do objeto."""
        return (f"EnergyManagementResult(device_status={self.device_status}, "
                f"energy_saving_mode={self.energy_saving_mode}, "
                f"temperature_regulation_active={self.temperature_regulation_active}, "
                f"total_energy_used={self.total_energy_used}, "
                f"devices_were_on={self.devices_were_on})") # Adicionado na representação