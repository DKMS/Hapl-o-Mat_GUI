#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Hapl-o-Mat: A software for haplotype frequency estimation

Copyright (C) 2020, DKMS gGmbH 

Ute Solloch / Dr. Juergen Sauter
Kressbach 1
72072 Tuebingen, Germany

T +49 7071 943-2061
F +49 7071 943-2090
solloch(at)dkms.de

This file is part of Hapl-o-Mat

Hapl-o-Mat is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by 
the Free Software Foundation; either version 3, or (at your option) any later version.

Hapl-o-Mat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Hapl-o-Mat;
see the file COPYING. If not, see <http://www.gnu.org/licenses/>.

Hapl-o-Mat software makes use of several libraries that are separately licensed.
These are listed in 'licenses.txt'.
numpy; Copyright (c) 2005-2020, NumPy Developers.
pyqtgraph: Copyright (c) 2011-2020, Pyqtgraph Developers.

Created on 06.05.2020

GUI_BuilData.py
Widget for IPD-IMGT/HLA data update

@author: Ute Solloch
'''

# fbs app special
# from fbs_runtime.application_context.PyQt5 import ApplicationContext

# import modules:
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QTableWidget, QRadioButton, QPushButton, QTextEdit, QLabel, QTabWidget, QTextEdit,QPlainTextEdit,
        QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QSizePolicy, QLineEdit,
        QCheckBox, QGroupBox, QComboBox, QFrame, QMainWindow, QMessageBox, QFileDialog, QToolTip)   
from PyQt5.QtCore import Qt, QDate, QTime, QDateTime
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen
from functools import partial
from pathlib import Path
import sys, os, time, platform
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import shutil

# import own modules
import GUI_miscFeatures


class CreateDataFrame(QGroupBox):
    """Window showing the process of IPD-IMGT/HLA data update
    """
    stateBD = pyqtSignal(str)
    stateNoBD = pyqtSignal(str)
        
    def __init__(self, pathHapDir):
        """constructor
        """
        super().__init__()
        
        self.pathHapDir = pathHapDir        
        
        self.initUI()
        
    def initUI(self):
        """define the GUI
        """        
        
        # stylesheet and platform
        # # fbs app special
        # appctxt = ApplicationContext()
        if platform.system() == "Windows":
            # # fbs app special            
            # stylesheet = appctxt.get_resource('styleWin.qss')
            # appctxt.app.setStyleSheet(open(stylesheet).read()) 
            self.setStyleSheet(open("styleWin.qss", "r").read())
        elif platform.system() == "Linux":
            # # fbs app special            
            # stylesheet = appctxt.get_resource('styleLinux.qss')
            # appctxt.app.setStyleSheet(open(stylesheet).read())
            self.setStyleSheet(open("styleLinux.qss", "r").read())
        
        self.setWindowFlags(Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        global dirParent        
        
        # GUIsrc working directory
        dirParent = os.getcwd()
        
        self.setMinimumSize(400,100)
        self.LayoutBuildData = QGridLayout()
        self.labBDInfo = QLabel('Data update may take a few minutes.')
        self.labOutputBD = QtWidgets.QTextBrowser()
        self.labOutputBD.setStyleSheet("color: white; background-color: black;")
        self.labOutputBD.verticalScrollBar().setStyleSheet('background: grey')
        self.buzyLines = WaitLines()
        self.btnKillProcess =QPushButton("Abort")
        self.btnKillProcess.setStyleSheet(GUI_miscFeatures.button_style_cancel)
       
        self.LayoutBuildData.addWidget(self.labBDInfo, 0,0,1,3)
        self.LayoutBuildData.addWidget(self.labOutputBD, 1, 0, 3,3)
        self.LayoutBuildData.addWidget(self.btnKillProcess, 4, 2, 1, 1)
        self.LayoutBuildData.addWidget(self.buzyLines, 4, 0)
        self.setLayout(self.LayoutBuildData)
        self.show()
        self.create_data_run()

    
####################################        
# Functions



    def create_data_run(self):
        """starts IPD-IMGT/HLA data update process
        """
        
        self.labOutputBD.append('Starting download ...')
        self.currDir_US = os.getcwd()
        try: dirParent
        except NameError:        
            QMessageBox.about(self, "Error: No directory.", "Please set working directory!")
        else:
            if platform.system() == "Windows":  # Windows-Version: change of directory necessary and Start of binary instead of python package
                self.pathBD = os.path.join(self.pathHapDir,"prepareData")     
                self.fileBD = os.path.join(self.pathBD, "BuildData.exe")
                my_path = Path(self.fileBD)            
                if my_path.is_file():
                    self.process = QtCore.QProcess()
                    os.chdir(self.pathBD)   #Win special [15.10.2020]
                    self.process.readyReadStandardOutput.connect(lambda: self.labOutputBD.append(str(self.process.readAllStandardOutput().data().decode('UTF-8')))) 
                    self.process.readyReadStandardError.connect(self.handle_stderr) 
                    QtCore.QTimer.singleShot(100, partial(self.process.start, "BuildData.exe"))
                    self.process.waitForStarted()          
                    self.btnKillProcess.clicked.connect(self.process.kill)
                    self.btnKillProcess.clicked.connect(self.buzy_Close)
                    self.btnKillProcess.clicked.connect(self.close)
                    self.process.finished.connect(self.status_CreateData1)
                else:
                    self.btnKillProcess.clicked.connect(self.close)
                    self.btnKillProcess.clicked.connect(self.buzy_Close)
                    self.status_NoBuild()
            elif platform.system() == "Linux":
                self.pathBD = os.path.join(self.pathHapDir,"prepareData")
                self.fileBD = os.path.join(self.pathBD, "BuildData.py")
                my_path = Path(self.fileBD)
                if my_path.is_file():
                    self.process = QtCore.QProcess()
                    self.process.setWorkingDirectory(self.pathBD)
                    self.process.readyReadStandardOutput.connect(lambda: self.labOutputBD.append(str(self.process.readAllStandardOutput().data().decode('UTF-8')))) 
                    self.process.readyReadStandardError.connect(self.handle_stderr)
                    QtCore.QTimer.singleShot(100, partial(self.process.start, 'python BuildData.py'))
                    self.process.waitForStarted()
                    
                    self.btnKillProcess.clicked.connect(self.process.kill)
                    self.btnKillProcess.clicked.connect(self.buzy_Close)
                    self.btnKillProcess.clicked.connect(self.close)                    
                    self.process.finished.connect(self.status_CreateData1)
                else:
                    self.btnKillProcess.clicked.connect(self.close)
                    self.btnKillProcess.clicked.connect(self.buzy_Close)
                    self.status_NoBuild()

    def status_CreateData1(self, exitCode, exitStatus):
        """processes status output of IPD-IMGT/HLA data update process
        and triggers sinal emission
        """
        if platform.system() == "Windows":
            os.chdir(self.currDir_US)   #Win special [15.10.2020]
        # self.buzy_Close()
        self.labOutputBD.clear()
        self.labOutputBD.append('exitStatus:' + str(exitStatus))
        if exitStatus == 0:         # Status 0: regular finished
            datetime = QDateTime.currentDateTime()
            self.labOutputBD.clear()
            self.labOutputBD.append('All data files updated.\n'+ datetime.toString())
            stringState = 'tick'
        elif exitStatus == 1:       # Status 1: process killed  
            self.labOutputBD.append('Data download cancelled.')
            stringState = 'error'
        self.stateBD.emit(stringState)
        self.close()
    
    def handle_stderr(self):
        """handling of StandardErrors
        """
        errorTxt = self.process.readAllStandardError().data().decode('UTF-8')
        errorArray = errorTxt.split('\n')
        if (len(errorArray) >= 2):
            stderr = errorArray[-2]
        else:
            stderr = ""
        messTxt = str(stderr + "\nPlease read tutorial for option of manual data update.")
        QMessageBox.about(self, "Error: Update not successful.", messTxt)
        stringState = 'error'
        self.stateBD.emit(stringState)

    def status_NoBuild(self):
        """used when IPD-IMGT/HLA data update not possible
        and triggers sinal emission
        """        
        if platform.system() == "Windows":
            os.chdir(self.currDir_US)   #Win special [15.10.2020]
        stringState = 'noBuild'
        self.stateNoBD.emit(stringState)
        self.buzy_Close()
        self.close()

    def buzy_Close(self):
        """ends execution of WaitLines()
        """
        self.buzyLines.close()
        


##################################
# Class WaitLines 

trs = (
    ( 0.0, 0.15, 0.30, 0.5, 0.65, 0.80, 0.9, 1.0 ),
    ( 1.0, 0.0,  0.15, 0.30, 0.5, 0.65, 0.8, 0.9 ),
    ( 0.9, 1.0,  0.0,  0.15, 0.3, 0.5, 0.65, 0.8 ),
    ( 0.8, 0.9,  1.0,  0.0,  0.15, 0.3, 0.5, 0.65 ),
    ( 0.65, 0.8, 0.9,  1.0,  0.0,  0.15, 0.3, 0.5 ),
    ( 0.5, 0.65, 0.8, 0.9, 1.0,  0.0,  0.15, 0.3 ),
    ( 0.3, 0.5, 0.65, 0.8, 0.9, 1.0,  0.0,  0.15 ),
    ( 0.15, 0.3, 0.5, 0.65, 0.8, 0.9, 1.0,  0.0, )
)

class WaitLines(QFrame):
    """executes busy indicator 'waitlines' (after J. Bodnar, ZetCode Advanced PyQt5 tutorial, August 2017)
    """    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        
        self.setFrameShape(QFrame.StyledPanel)    
        self.count = 0
        self.timerId = self.startTimer(105)        
        self.setGeometry(300, 300, 50, 50)

    def paintEvent(self, event):
    
        painter = QPainter()        
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.drawLines(painter)
        painter.end()
        
    def drawLines(self, painter):

        pen = QPen()
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        w = self.width()
        h = self.height()       
        painter.translate(w/2, h/2)
        painter.setPen(pen)

        for i in range(8):      
            painter.setOpacity(trs[self.count%8][i])
            painter.drawLine(0.0, -4.0, 0.0, -10.0)
            painter.rotate(45)

    def timerEvent(self, event):
        
        self.count = self.count + 1
        self.repaint()        


###################################################################
# main

if __name__ == '__main__':

    import sys
    app = QApplication([])
    window = CreateDataFrame()
    window.show()
    sys.exit(app.exec_())
        