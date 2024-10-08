from typing import Dict, Optional

import requests
from lcls_tools.common.controls.pyepics.utils import PV

from utils.sc_linac.linac_utils import SCLinacObject, DECARAD_BACKGROUND_READING


class DecaradHead(SCLinacObject):
    def __init__(self, number: int, decarad: "Decarad"):
        if number not in range(1, 11):
            raise AttributeError("Decarad Head number need to be between 1 and 10")

        self.decarad: Decarad = decarad
        self.number: int = number

        # Adds leading 0 to numbers with less than 2 digits
        self._pv_prefix = self.decarad.pv_addr("{:02d}:".format(self.number))

        self.dose_rate_pv: str = self.pv_addr("GAMMAAVE")
        self._dose_rate_pv_obj: Optional[PV] = None

        self.counter = 0

    @property
    def pv_prefix(self):
        return self._pv_prefix

    @property
    def dose_rate_pv_obj(self) -> PV:
        if not self._dose_rate_pv_obj:
            self._dose_rate_pv_obj = PV(self.dose_rate_pv)
        return self._dose_rate_pv_obj.get()

    @property
    def avg_dose(self) -> float:
        # try to do averaging of the last 60 points to account for signal noise
        try:
            return max(self.dose_rate_pv_obj.get() - DECARAD_BACKGROUND_READING, 0)

        # return the most recent value if we can't average for whatever reason
        except (AttributeError, requests.exceptions.ConnectionError):
            return self.normalized_dose

    @property
    def normalized_dose(self) -> float:
        return max(self.dose_rate_pv_obj.get() - DECARAD_BACKGROUND_READING, 0)


class Decarad(SCLinacObject):
    def __init__(self, number: int):
        if number not in [1, 2]:
            raise AttributeError("Decarad needs to be 1 or 2")
        self.number = number
        self._pv_prefix = "RADM:SYS0:{num}00:".format(num=self.number)
        self.power_control_pv = self.pv_addr("HVCTRL")
        self.power_status_pv = self.pv_addr("HVSTATUS")
        self.voltage_readback_pv = self.pv_addr("HVMON")

        self.heads: Dict[int, DecaradHead] = {
            head: DecaradHead(number=head, decarad=self) for head in range(1, 11)
        }

    @property
    def pv_prefix(self):
        return self._pv_prefix

    @property
    def max_avg_dose(self):
        return max([head.avg_dose for head in self.heads.values()])

    @property
    def max_dose(self):
        return max([head.dose_rate_pv_obj.value for head in self.heads.values()])
