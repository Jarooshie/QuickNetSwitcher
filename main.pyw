from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QImage
from keyboard import is_pressed
from time import sleep
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os

import subprocess


mainWifi = "TotalWifi"
robotWifi = "3065"



class rippleButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._radius = 0
        self.pressed.connect(self._start_animation)

    def _start_animation(self):
        self.t = 0
        self._radius = 0
        self._animation = QVariantAnimation(startValue=0.0)
        self._animation.valueChanged.connect(self._handle_valueChanged)
        self._animation.finished.connect(self._handle_finished)
        self._animation.setDuration(300)
        self._animation.setEndValue(self.width() / 2.0)
        self._animation.start()

    def _handle_valueChanged(self, value):
        self._radius = value*2
        self.update()

    def _handle_finished(self):
        self._radius = 0
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._radius:
            self.t = self.t + 5
            qp = QPainter(self)
            qp.setBrush(QColor(0, 0, 0, 100-self.t))
            qp.setPen(Qt.NoPen)
            qp.drawEllipse(self.rect().center(), self._radius, self._radius)
            qp.setOpacity(self._animation.currentValue() / 300)


class NetCheckerThread(QThread):
    def run(self):
        while 1:
            network_interfaces = str(subprocess.check_output("netsh wlan show interfaces"))
            if mainWifi in network_interfaces:
                mainNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #198754;\n  font-size: 12px;\n  border-radius: 5px;\n}')
                pass
            elif robotWifi in network_interfaces:
                robotNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #198754;\n  font-size: 12px;\n  border-radius: 5px;\n}')
                pass
            else:
                print("no connection found.")

            sleep(0.25)

win = None
networks = []

def __init__():
    global win
    global mainNet
    global robotNet
    app = QApplication(sys.argv)
    win = loadUi("main.ui")

    win.setWindowFlag(QtCore.Qt.FramelessWindowHint)
    win.setAttribute(Qt.WA_TranslucentBackground,True)
    win.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
    win.setWindowFlag(QtCore.Qt.Tool) 

    win.tray_icon = QtWidgets.QSystemTrayIcon(win)
    win.tray_icon.setIcon(win.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))
    win.tray_icon.setToolTip("Quick Net Switcher\n-  Made by 3065  -")

    show_action = QtWidgets.QAction("Show", win)
    quit_action = QtWidgets.QAction("Exit", win)
    hide_action = QtWidgets.QAction("Hide", win)
    show_action.triggered.connect(win.show)
    hide_action.triggered.connect(win.hide)
    quit_action.triggered.connect(app.quit)

    mainNet = rippleButton(mainWifi,win)
    mainNet.setGeometry(10,10,71,31)
    mainNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #545454;\n  font-size: 12px;\n  border-radius: 5px;\n}')

    networks.append(mainNet)

    robotNet = rippleButton(robotWifi,win)
    robotNet.setGeometry(90,10,71,31)
    robotNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #545454;\n  font-size: 12px;\n  border-radius: 5px;\n}')

    networks.append(robotNet)

    NTC = NetCheckerThread()
    NTC.start()


    tray_menu = QMenu()
    tray_menu.addAction(show_action)
    tray_menu.addAction(hide_action)
    tray_menu.addAction(quit_action)
    win.tray_icon.setContextMenu(tray_menu)
    win.tray_icon.show()
    
    win.show()

    sys.exit(app.exec_())

    

def createConnection(netName):
    pass

__init__()

