from typing import List

import pyqtgraph as pg
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QDateTimeEdit, QLabel
from pydm import Display

from displays.cavity_display.backend.backend_cavity import BackendCavity
from displays.cavity_display.backend.backend_machine import BackendMachine
from displays.cavity_display.frontend.cavity_widget import DARK_GRAY_COLOR
from displays.cavity_display.utils import utils


class FaultCountForMachineDisplay(Display):
    def __init__(self, lazy_fault_pvs=True):
        super().__init__()
        self.setWindowTitle("Fault Count Total for the Machine")

        self.machine = BackendMachine(lazy_fault_pvs=lazy_fault_pvs)

        main_v_layout = QVBoxLayout()
        input_h_layout = QHBoxLayout()

        self.plot_window = pg.plot()
        self.plot_window.setBackground(DARK_GRAY_COLOR)

        main_v_layout.addLayout(input_h_layout)
        main_v_layout.addWidget(self.plot_window)
        self.setLayout(main_v_layout)

        self.fault_combo_box = QComboBox()
        self.number_of_bins_combo_box = QComboBox()

        end_date_time = QDateTime.currentDateTime()
        intermediate_time = QDateTime.addSecs(end_date_time, -30 * 60)  # 30 min
        min_date_time = QDateTime.addYears(end_date_time, -3)  # 3 years

        self.start_selector = QDateTimeEdit()
        self.start_selector.setCalendarPopup(True)

        self.end_selector = QDateTimeEdit()
        self.end_selector.setCalendarPopup(True)

        self.start_selector.setMinimumDateTime(min_date_time)
        self.start_selector.setDateTime(intermediate_time)
        self.end_selector.setDateTime(end_date_time)

        input_h_layout.addWidget(QLabel("Fault:"))
        input_h_layout.addWidget(self.fault_combo_box)
        input_h_layout.addWidget(QLabel("Number of time bins:"))
        input_h_layout.addWidget(self.number_of_bins_combo_box)
        input_h_layout.addStretch()
        input_h_layout.addWidget(QLabel("Start:"))
        input_h_layout.addWidget(self.start_selector)
        input_h_layout.addWidget(QLabel("End:"))
        input_h_layout.addWidget(self.end_selector)

        fault_list = []
        for fault_row_dict in utils.parse_csv():
            fault_list.append(fault_row_dict["Three Letter Code"])

        self.fault_combo_box.addItems(fault_list)
        self.number_of_bins_combo_box.addItems([""] + [str(i) for i in range(1, 11)])

        self.num_of_faults = []
        self.num_of_invalids = []

        self.fault_combo_box.currentIndexChanged.connect(self.update_plot)

    def get_data(self):
        self.num_of_faults = []
        self.num_of_invalids = []

        start = self.start_selector.dateTime().toPyDateTime()
        end = self.end_selector.dateTime().toPyDateTime()

        """
        Using this section to try and figure out how to run through all cavities + cryomodules
        """
        self.backend_cavities: List[BackendCavity] = list(self.machine.all_iterator)
        for backend_cavity_object in self.backend_cavities:
            for fault_tuple in backend_cavity_object.faults.items():
                fault_object = fault_tuple[1]
                if fault_object.tlc == self.fault_combo_box.currentText():
                    # print(backend_cavity_object, fault_object.tlc)
                    fault_counter_object = fault_object.get_fault_count_over_time_range(
                        start, end
                    )

    def update_plot(self):
        self.plot_window.clear()
        self.get_data()
