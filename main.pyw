from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

import builder

import os
import threading
import sys
import json
from time import sleep

from win32api import GetMonitorInfo, MonitorFromPoint

with open("settings.json", "r") as r:
        SETTINGS = json.loads(r.read())

# The builder is currently not recommended for use, Stay with the built-in Refresher.exe.
#
# if not os.path.isfile("./Refresher.exe"):
#     builder.buildScanner()



mainWifi = SETTINGS[0]["mainWifi"]
robotWifi = SETTINGS[0]["robotWifi"]

xOffset, yOffset = SETTINGS[0]["xOffset"],SETTINGS[0]["yOffset"]

class rippleButton(QPushButton):
    global buttonDown
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._radius = 0
        self.pressed.connect(self._start_animation)
        self.clickedPos = QPoint()

    def _start_animation(self):
        self.t = 0
        self._radius = 0
        self._animation = QVariantAnimation(startValue=0.0)
        self._animation.valueChanged.connect(self._handle_valueChanged)
        self._animation.finished.connect(self._handle_finished)
        self._animation.setDuration(300)
        self._animation.setEndValue(self.width() / 2.0)
        self._animation.start()

        mouse = QCursor().pos()
        self.clickedPos.setX(mouse.x() - self.parent().frameGeometry().x() - self.frameGeometry().x())  #GlobalMouseXY - AppXY - ButtonInAppXY = clickedXY
        self.clickedPos.setY(mouse.y() - self.parent().frameGeometry().y()  - self.frameGeometry().y() ) #Get the clicked button mouse position relative to the button coordinates

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

gray =  'QPushButton{\n color: #ffffff;\n background-color: #545454;\n  font-size: 12px;\n  border-radius: 5px;\n}'
red =   'QPushButton{\n color: #ffffff;\n background-color: #bd2038;\n  font-size: 12px;\n  border-radius: 5px;\n}'
green = 'QPushButton{\n color: #ffffff;\n background-color: #198754;\n  font-size: 12px;\n  border-radius: 5px;\n}'

class NetCheckerThread(QThread):
    def run(self):
        while 1:
            try:
                network_interfaces = str(os.popen('netsh wlan show interfaces').read())
                networks = str(os.popen('netsh wlan show networks | findstr SSID').read())

                mainWifi = SETTINGS[0]["mainWifi"]
                robotWiFi = SETTINGS[0]["robotWifi"]

                # whole lotta nonsense below but it works 😃👍

                if mainWifi in network_interfaces:
                    mainNet.setStyleSheet(green) # GREEN
                else:
                    mainNet.setStyleSheet(gray) # GRAY
                if robotWiFi in network_interfaces:
                    robotNet.setStyleSheet(green) # GREEN
                else:
                    robotNet.setStyleSheet(gray) # GRAY

                if mainWifi in networks:
                    mainNet.setStyleSheet(red) # RED
                    if mainWifi in network_interfaces:
                        mainNet.setStyleSheet(green) # GREEN
                else:
                    mainNet.setStyleSheet(gray) # GRAY

                if robotWiFi in networks:
                    robotNet.setStyleSheet(red) # RED
                    if robotWiFi in network_interfaces:
                        robotNet.setStyleSheet(green) # GREEN
                else:
                    robotNet.setStyleSheet(gray) # GRAY
            
            except Exception as err:
                pass

            #os.popen("Refresher.exe")
            sleep(1) # 1s refresh rate

def createMainConnection():
    os.popen(f'netsh wlan connect name="{SETTINGS[0]["mainWifi"]}"') # App may be marked as a virus because of this line (can't find another solution)
    os.popen(f'netsh wlan connect name="{SETTINGS[0]["mainWifi"]}"') # App may be marked as a virus because of this line (can't find another solution)

def createRobotConnection():
    os.popen(f'netsh wlan connect name="{SETTINGS[0]["robotWifi"]}"')

refreshing = False

def refreshNetworks():
    global refreshing
    if refreshing == False:
        refreshing = True

        refreshBtn.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #545454;\n  font-size: 18px;\n  border-radius: 5px;\n}')
        refreshBtn.setEnabled(False)

        refreshing_text.setGeometry(15,14,71,16)
        refreshing_text.setStyleSheet("color:white")
        refreshing_text.show()
        result = str(os.popen('Refresher.exe').read()) # .read() is to make the function stop until it recieves a result (1)
        refreshing_text.hide()

        refreshBtn.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #4D68F9;\n  font-size: 18px;\n  border-radius: 5px;\n}')
        refreshBtn.setEnabled(True)

        refreshing = False

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
    global mainNet, robotNet
    global settings
    global height,width
    global refreshing_text, refreshBtn
    app = QApplication(sys.argv)

    settings = loadUi("settings.ui")
    settings.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint,False)
    settings.Apply.clicked.connect(applySettings)
    settings.Cancel.clicked.connect(settings.hide)
    settings.setWindowIcon(settings.style().standardIcon(QtWidgets.QStyle.SP_VistaShield))
    settings.setWindowFlag(QtCore.Qt.FramelessWindowHint)
    settings.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
    settings.setWindowFlag(QtCore.Qt.Tool) 
    settings.setAttribute(Qt.WA_TranslucentBackground,True)

    win = QMainWindow()
    height,width = 81,171 #app dimensions 

    win.setWindowFlag(QtCore.Qt.FramelessWindowHint)
    win.setAttribute(Qt.WA_TranslucentBackground,True)
    win.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
    win.setWindowFlag(QtCore.Qt.Tool) 

    win.setGeometry(screen_width - width + xOffset,screen_height - taskbar_height - height - yOffset, width, height) # auto position gui to screen

    win.tray_icon = QtWidgets.QSystemTrayIcon(win)
    win.tray_icon.setIcon(win.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))
    win.tray_icon.setToolTip("Quick Net Switcher\n-  Made by 3065  -")

    refreshing_text = QtWidgets.QLabel("Refreshing...", win)
    refreshing_text.hide()

    show_action = QtWidgets.QAction("Show", win)
    hide_action = QtWidgets.QAction("Hide", win)
    quit_action = QtWidgets.QAction("Exit", win)
    settings_action = QtWidgets.QAction("Settings", win)
    show_action.triggered.connect(win.show)
    hide_action.triggered.connect(win.hide)
    quit_action.triggered.connect(app.quit)
    settings_action.triggered.connect(showSettings)

    mainNet = rippleButton(mainWifi,win)
    mainNet.setGeometry(10,10 + 30,71,31)
    mainNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #545454;\n  font-size: 12px;\n  border-radius: 5px;\n}')

    mainNet.clicked.connect(createMainConnection)

    robotNet = rippleButton(robotWifi,win)
    robotNet.setGeometry(90,10 +  30,71,31)
    robotNet.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #545454;\n  font-size: 12px;\n  border-radius: 5px;\n}')



    settings.setStyleSheet('''QDialog{
background-color: rgb(25,25,25);
border-radius: 5px;
}''')

    robotNet.clicked.connect(createRobotConnection)

    refreshBtn = rippleButton("↻",win)
    refreshBtn.setGeometry(130,2,30,30)
    refreshBtn.setStyleSheet('QPushButton{\n color: #ffffff;\n background-color: #4D68F9;\n  font-size: 18px;\n  border-radius: 5px;\n}')
    refreshBtn.setToolTip("Refresh")

    refreshBtn.clicked.connect(lambda: threading.Thread(target=refreshNetworks).start())

    NTC = NetCheckerThread()
    NTC.start()

    tray_menu = QMenu()
    tray_menu.addAction(settings_action)
    tray_menu.addAction(show_action)
    tray_menu.addAction(hide_action)
    tray_menu.addAction(quit_action)
    win.tray_icon.setContextMenu(tray_menu)
    win.tray_icon.show()
    
    win.show()

    sys.exit(app.exec_())

def showSettings():
    settings.mainWifi.setText(SETTINGS[0]["mainWifi"])
    settings.robotWifi.setText(SETTINGS[0]["robotWifi"])

    settings.xOffset.setValue(SETTINGS[0]["xOffset"])
    settings.yOffset.setValue(SETTINGS[0]["yOffset"])

    settings.show()

def applySettings():
    SETTINGS[0]["mainWifi"] = settings.mainWifi.text()
    SETTINGS[0]["robotWifi"] = settings.robotWifi.text()
    SETTINGS[0]["xOffset"] = settings.xOffset.value()
    SETTINGS[0]["yOffset"] = settings.yOffset.value()

    mainWifi = settings.mainWifi.text()
    robotWifi = settings.robotWifi.text()
    
    mainNet.setText(settings.mainWifi.text())
    robotNet.setText(settings.robotWifi.text())
    win.setGeometry(screen_width - width + settings.xOffset.value(),screen_height - taskbar_height - height - settings.yOffset.value(), width, height)

    with open("settings.json", "w+") as r:
        r.write(json.dumps(SETTINGS,indent=4))

__init__()
