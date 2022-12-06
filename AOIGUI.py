import sys

from PyQt5.QtCore import Qt, QTimer, QObject, QThread, pyqtSignal, QMutex
from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit, QMainWindow, QApplication, QVBoxLayout, QWidget, QSpinBox
import random
import requests
import json
import Cryostat
#from Cryostation import Cryostat as cr
import time as tm

from time import sleep

CRYO_IP = 'test'#'http://128.46.220.204:47101'
mutex = QMutex() # not in use 

#tutorials used: https://realpython.com/python-pyqt-qthread/   https://www.pythonguis.com/tutorials/pyqt-basic-widgets/   https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QLabel.html

class Worker(QObject):
    finished = pyqtSignal()

    def run(self):
        sleep(5)
        self.finished.emit()

class Window(QMainWindow):
    def __init__(self, CRYO_IP, parent=None):
        super().__init__(parent)
        self.CRYO_IP = CRYO_IP
        self.c=Cryostat.Cryostat(CRYO_IP)
        self.target_temp = 150
        self.setupUi()
        
    
    def setupUi(self):
        self.setWindowTitle("Example GUI")
        self.resize(300, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.cooldownBtn = QPushButton("Cooldown", self)
        #self.cooldownBtn.move(64, 32)
        self.cooldownBtn.clicked.connect(self.cooldown)
        self.warmupBtn = QPushButton("Warm Up", self)
        #self.warmupBtn.move(64, 64)
        self.warmupBtn.clicked.connect(self.warmup)
        self.terminateBtn = QPushButton("Terminate", self)
        #self.terminateBtn.move(64, 96)
        self.terminateBtn.clicked.connect(self.terminate)
        self.pullVacuumBtn = QPushButton("Pull Vacuum", self)
        #self.pullVacuumBtn.move(64, 128)
        self.pullVacuumBtn.clicked.connect(self.pullVacuum)

        self.tempLabel = QLabel("Current Temperature: -- K")  #label for the adjustable widget
        self.tempLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.tempBox = QLineEdit(self)
        self.tempBox.resize(280,40)
        self.update_timer = QTimer()
        self.update_timer.start(100)
        self.update_timer.timeout.connect(self.getTemp)
                
        #self.enterline = QSpinBox() #widget for selecting a value
        #self.enterline.setMinimum(0)
        #self.enterline.setMaximum(30)
        #self.enterline.setSuffix(" mA")
        #self.enterline.setSingleStep(1)
        #self.valuelabel = QLabel("The chosen value is: ") #label for chosen value
        #self.chosenvalue = QLabel(self) #displaying the selected value 
        #self.enterline.valueChanged.connect(self.value_changed) #sending chosen value to function
        
        #layout

        layout2 = QVBoxLayout()
        layout2.addWidget(self.cooldownBtn)
        layout2.addWidget(self.warmupBtn)
        layout2.addWidget(self.terminateBtn)
        layout2.addWidget(self.pullVacuumBtn)
        layout2.addWidget(self.tempLabel)
        layout2.addWidget(self.tempBox)
        
        #layout.addWidget(self.enterline)
        #layout.addWidget(self.valuelabel)
        #layout.addWidget(self.chosenvalue)
        
        
        self.centralWidget.setLayout(layout2)

    def cooldown(self):
        target_temp = float(self.tempBox.text())
        if target_temp < 1 or target_temp > 293:
            print("Error: please enter a value between 1 and 293.")
        else:
            self.target_temp = target_temp
            self.c.setTargetTemp(self.target_temp)
            print(self.CRYO_IP, "cooldown() to", self.c.getTargetTemp())
            self.c.cooldown()

    def warmup(self):
        print(self.CRYO_IP, "warmup()")
        self.c.warmup()
        
    def terminate(self):
        print(self.CRYO_IP, "terminate()")
        self.c.terminate()
        
    def pullVacuum(self):
        print(self.CRYO_IP, "pullVacuum()")
        self.c.pullVacuum()
    
    def getTemp(self):
        temp = self.c.getTemp()
        #print(self.CRYO_IP, "getTemp() =", temp)
        self.tempLabel.setText("Current Temperature: " + str(round(temp, 3)) + "K")
        
   
app = QApplication(sys.argv)
win = Window(CRYO_IP)
win.show()
sys.exit(app.exec())

# cooldown button - parameter in a textbox from 1 to 293 K
# label - shows temperature in real time