from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import sys
from time import sleep

from win32api import GetMonitorInfo, MonitorFromPoint



mainWifi = "mainWifi"
robotWifi = "3065"

xOffset, yOffset = 0,0    #edit based on your screen



class rippleButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._radius = 0
        self.pressed.connect(self._start_animation)
        self.clickedPos = QPoint()

    def _start_animation(self,):
        self.t = 0
        self._radius = 0
        self._animation = QVariantAnimation(startValue=0.0)
        self._animation.valueChanged.connect(self._handle_valueChanged)
        self._animation.finished.connect(self._handle_finished)
        self._animation.setDuration(300)
        self._animation.setEndValue(self.width() / 2.0)
        self._animation.start()

        mouse = QCursor().pos()
        self.clickedPos.setX(mouse.x() - self.parent().frameGeometry().x() - self.frameGeometry().x())  #GlobalMouseXY - AppXY - ButtonInAppXY
        self.clickedPos.setY(mouse.y() - self.parent().frameGeometry().y()  - self.frameGeometry().y() ) #get the clicked button mouse position relative to the button coordinates

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
            qp.drawEllipse(self.clickedPos, self._radius, self._radius)
            qp.setOpacity(self._animation.currentValue() / 300)

class NetCheckerThread(QThread):
    def run(self):
        while 1:
            network_interfaces = str(os.popen('netsh wlan show interfaces').read())
            networks = str(os.popen('netsh wlan show networks').read())
            if mainWifi in networks:
                mainNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #bd2038;\n  font-size: 12px;\n  border-radius: 5px;\n}') #DISPLAY RED COLOR
                if mainWifi in network_interfaces:
                    mainNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #198754;\n  font-size: 12px;\n  border-radius: 5px;\n}') #DISPLAY GREEN COLOR
            else:
                mainNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #545454;\n  font-size: 12px;\n  border-radius: 5px;\n}') #DISPLAY GRAY COLOR

            if robotWifi in networks:
                robotNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #bd2038;\n  font-size: 12px;\n  border-radius: 5px;\n}') #DISPLAY RED COLOR
                if robotWifi in network_interfaces:
                    robotNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #198754;\n  font-size: 12px;\n  border-radius: 5px;\n}') #DISPLAY GREEN COLOR
            else:
                robotNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #545454;\n  font-size: 12px;\n  border-radius: 5px;\n}') #DISPLAY GRAY COLOR

            sleep(0.25) # 0.25s refresh rate

win = None

monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
monitor_area = monitor_info.get("Monitor")
work_area = monitor_info.get("Work")
screen_height = monitor_area[3]
screen_width = monitor_area[2]
taskbar_height = screen_height-work_area[3]

screen_height = 1080
screen_width = 1920 #I set it 1080,1920 to prevent issues

def __init__():
    global win
    global mainNet
    global robotNet
    app = QApplication(sys.argv)
    win = QDialog()
    height,width = 51,171 #app dimentions 

    win.setWindowFlag(QtCore.Qt.FramelessWindowHint)
    win.setAttribute(Qt.WA_TranslucentBackground,True)
    win.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
    win.setWindowFlag(QtCore.Qt.Tool) 

    win.setGeometry(screen_width - width + xOffset,screen_height - taskbar_height - height - yOffset, width, height) # auto position gui to screen

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

    mainNet.clicked.connect(createMainConnection)

    robotNet = rippleButton(robotWifi,win)
    robotNet.setGeometry(90,10,71,31)
    robotNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #545454;\n  font-size: 12px;\n  border-radius: 5px;\n}')

    robotNet.clicked.connect(createRobotConnection)

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

def createMainConnection():
    os.popen(f'netsh wlan connect name="{mainWifi}"') # app may be marked as a virus because of this line (can't find another solution)

def createRobotConnection():
    os.popen(f'netsh wlan connect name="{robotWifi}"')

__init__()

