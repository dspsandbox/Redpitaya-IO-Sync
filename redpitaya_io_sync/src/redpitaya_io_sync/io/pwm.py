from .base import BaseIo

class PwmCmd:
    DUTY_CYCLE = 0x0

class Pwm(BaseIo): 
    def __init__(self, addr):
        super().__init__(addr)

    def duty_cycle(self, t: int, val: float):
        DUTY_CYCLE_MIN = 0.0
        DUTY_CYCLE_MAX = 1.0
        if (val < DUTY_CYCLE_MIN) or (val > DUTY_CYCLE_MAX):
            raise Exception(f"Duty cycle value {val} is out of range [{DUTY_CYCLE_MIN}, {DUTY_CYCLE_MAX}].")
        data = int(val * ((1 << 8) - 1))
        self.add_instruction(t=t, cmd=PwmCmd.DUTY_CYCLE, data=data)