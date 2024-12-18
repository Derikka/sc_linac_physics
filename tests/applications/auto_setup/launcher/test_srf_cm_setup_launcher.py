from random import randint, choice
from unittest.mock import MagicMock

import pytest
from lcls_tools.common.controls.pyepics.utils import make_mock_pv

from applications.auto_setup.backend.setup_cavity import SetupCavity
from applications.auto_setup.backend.setup_cryomodule import SetupCryomodule
from applications.auto_setup.backend.setup_utils import (
    STATUS_READY_VALUE,
    STATUS_ERROR_VALUE,
)
from applications.auto_setup.launcher.srf_cm_setup_launcher import setup_cavity
from utils.sc_linac.linac_utils import ALL_CRYOMODULES


@pytest.fixture
def cavity():
    cavity = SetupCavity(cavity_num=randint(1, 8), rack_object=MagicMock())
    cavity._status_msg_pv_obj = make_mock_pv()
    cavity._status_pv_obj = make_mock_pv()
    cavity._ssa_cal_requested_pv_obj = make_mock_pv()
    cavity._auto_tune_requested_pv_obj = make_mock_pv()
    cavity._cav_char_requested_pv_obj = make_mock_pv()
    cavity._rf_ramp_requested_pv_obj = make_mock_pv()
    cavity.trigger_setup = MagicMock()
    cavity.trigger_shutdown = MagicMock()
    cavity.cryomodule = SetupCryomodule(
        cryo_name=choice(ALL_CRYOMODULES), linac_object=MagicMock()
    )
    cm = cavity.cryomodule
    cm._ssa_cal_requested_pv_obj = make_mock_pv()
    cm._auto_tune_requested_pv_obj = make_mock_pv()
    cm._cav_char_requested_pv_obj = make_mock_pv()
    cm._rf_ramp_requested_pv_obj = make_mock_pv()
    yield cavity


def test_setup_cavity(cavity):
    args = MagicMock()
    args.shutdown = False
    cavity._status_pv_obj.get = MagicMock(
        return_value=choice([STATUS_READY_VALUE, STATUS_ERROR_VALUE])
    )
    setup_cavity(cavity, args)
    cavity.trigger_setup.assert_called()
    cryomodule = cavity.cryomodule
    cavity._ssa_cal_requested_pv_obj.put.assert_called()
    cryomodule._ssa_cal_requested_pv_obj.get.assert_called()

    cavity._auto_tune_requested_pv_obj.put.assert_called()
    cryomodule._auto_tune_requested_pv_obj.get.assert_called()

    cavity._cav_char_requested_pv_obj.put.assert_called()
    cryomodule._cav_char_requested_pv_obj.get.assert_called()

    cavity._rf_ramp_requested_pv_obj.put.assert_called()
    cryomodule._rf_ramp_requested_pv_obj.get.assert_called()
