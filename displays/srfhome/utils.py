from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout
from pydm.widgets import PyDMByteIndicator, PyDMLabel, PyDMShellCommand


def make_watcher_groupbox(watcher_name: str, script_path: str) -> QGroupBox:
    groupbox = QGroupBox(watcher_name)
    vlayout = QVBoxLayout()
    groupbox.setLayout(vlayout)

    show_button = PyDMShellCommand()
    show_button.setText(f"Show {watcher_name} Output")
    xterm_prefix = f"xterm -T {watcher_name} -hold -e"
    show_button.commands = [f"{xterm_prefix} tmux_launcher open {watcher_name}"]

    # TODO change export to point to release
    xterm_prefix += (
        ' "export PYTHONPATH=/home/physics/zacarias/sc_linac_physics && export TMUX_SSH_USER=laci && '
        "exportMUX_SSH_SERVER=lcls-srv03"
    )

    start_button = PyDMShellCommand()
    start_button.setText(f"(Re)Start {watcher_name} Process")
    tmux_command = f"tmux_launcher restart 'python {script_path}' {watcher_name}\""
    start_button.commands = [f"{xterm_prefix} && {tmux_command}"]
    print(start_button.commands)

    stop_button = PyDMShellCommand()
    stop_button.setText(f"Stop {watcher_name} Process")
    tmux_command = f'tmux_launcher stop {script_path} {watcher_name}"'
    stop_button.commands = [f"{xterm_prefix} && {tmux_command}"]
    print(stop_button.commands)

    vlayout.addWidget(show_button)
    vlayout.addWidget(start_button)
    vlayout.addWidget(stop_button)

    readback_layout = QHBoxLayout()
    readback_layout.addStretch()
    watcher_pv = f"ALRM:SYS0:{watcher_name}:ALHBERR"
    indicator = PyDMByteIndicator(init_channel=watcher_pv)
    indicator.showLabels = False
    indicator.offColor = QColor(0, 255, 0)
    indicator.onColor = QColor(255, 0, 0)
    readback_label = PyDMLabel(init_channel=watcher_pv)
    readback_layout.addWidget(indicator)
    readback_layout.addWidget(readback_label)
    readback_layout.addStretch()
    vlayout.addLayout(readback_layout)
    return groupbox


def make_link_button(text: str, link: str) -> PyDMShellCommand:
    button = PyDMShellCommand(
        title=text,
        command=f"python -m webbrowser {link}",
    )
    button.setText(text)
    return button
