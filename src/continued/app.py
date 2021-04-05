#!/usr/bin/env python3

from typing import Callable

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt


class ContinuEDApp(QtCore.QObject):

    __main_window: QtWidgets.QMainWindow

    closed = QtCore.Signal()
    update_clicked = QtCore.Signal()

    set_message: Callable[[str], None]
    set_cmdr: Callable[[str], None]
    set_ship: Callable[[str], None]
    set_system: Callable[[str], None]
    set_station: Callable[[str], None]

    class __MainWindow(QtWidgets.QMainWindow):

        closed = QtCore.Signal()

        def __init__(self) -> None:

            super().__init__(flags=Qt.WindowStaysOnTopHint)

        def closeEvent(self, event: QtGui.QCloseEvent) -> None:
            super().closeEvent(event)
            if event.isAccepted():
                self.closed.emit()

    def __init__(self, initial_message="") -> None:

        super().__init__(None)

        entry_cmdr = QtWidgets.QLabel()
        self.set_cmdr = entry_cmdr.setText

        entry_ship = QtWidgets.QLabel()
        entry_ship.setTextFormat(Qt.RichText)
        entry_ship.setOpenExternalLinks(True)
        self.set_ship = entry_ship.setText

        entry_system = QtWidgets.QLabel()
        entry_system.setTextFormat(Qt.RichText)
        entry_system.setOpenExternalLinks(True)
        self.set_system = entry_system.setText

        entry_station = QtWidgets.QLabel()
        entry_station.setTextFormat(Qt.RichText)
        entry_station.setOpenExternalLinks(True)
        self.set_station = entry_station.setText

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow('Cmdr:', entry_cmdr)
        form_layout.addRow('Ship:', entry_ship)
        form_layout.addRow('System:', entry_system)
        form_layout.addRow('Station:', entry_station)

        update_button = QtWidgets.QPushButton(text="Update")
        update_button.clicked.connect(self.update_clicked)

        status_bar = QtWidgets.QStatusBar()
        if initial_message:
            status_bar.showMessage(initial_message)
        self.set_message = status_bar.showMessage

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(update_button)
        layout.addWidget(status_bar)

        inner = QtWidgets.QWidget()
        inner.setLayout(layout)

        self.__main_window = self.__MainWindow()
        # self.__main_window.setWindowTitle("ContinuED")
        self.__main_window.setCentralWidget(inner)
        self.__main_window.closed.connect(self.closed)

    def show(self) -> None:

        self.__main_window.show()
