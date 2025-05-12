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

# # fbs app special
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
        
        # platform and stylesheet
        try:        
            styleFile = GUI_miscFeatures.CONFIGURATION_FILES[platform.system()]["styleSheet"]  
        except:
            print("StyleSheet: Your current OS is not supported.")
        # fbs app special
        self.setStyleSheet(open(styleFile, "r").read())
        # appctxt = ApplicationContext()
        # appctxt.app.setStyleSheet(open(appctxt.get_resource(styleFile)).read()) 
        
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
            elif (platform.system() == "Linux") or (platform.system() == "Darwin"):
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
        


#######################################
#class  ViewSources

class ViewSources(QWidget):
    """a widget to display editable URL sources for data downoad.
    """
    def __init__(self, pathHapDir):
        """constructor
        """
        super().__init__()
        self.pathHapDir = pathHapDir
        self.initUI()
        
    def initUI(self):
        """define the GUI
        """  
        self.sources_display()
        self.show()
        
    def sources_display(self):
        # platform and stylesheet  
        try:        
            styleFile = GUI_miscFeatures.CONFIGURATION_FILES[platform.system()]["styleSheet"]  
        except:
            print("StyleSheet: Your current OS is not supported.")
        # fbs app special
        self.setStyleSheet(open(styleFile, "r").read())
        # appctxt = ApplicationContext()
        # appctxt.app.setStyleSheet(open(appctxt.get_resource(styleFile)).read())          
       
        self.setMinimumSize(1000,300)
        layoutAll = QVBoxLayout() 
        sourceFrame = QFrame()             
        grid = QGridLayout()

        # GUIsrc working directory      
        self.dirParent = os.getcwd()
        self.pathURLconfig = str(os.path.join(self.pathHapDir, "prepareData", "url_config.txt"))  
       
        # Read URLconfig 
        if(os.path.isfile(self.pathURLconfig)):
            try:            
                # read parameters
                fi = open(self.pathURLconfig, 'r')
                for line in fi:
                    if not line.startswith('#'):                    
                        line = line.rstrip('\r\n')
                        splittedLine = line.split('=')
                        inputFileName = splittedLine[0]
                        inputURL = splittedLine[1]

                        if inputFileName == 'hla_nom_p.txt' :
                            urlForHlanomp = inputURL
                        elif inputFileName == 'hla_nom_g.txt' :
                            urlForHlanomg = inputURL
                        elif inputFileName == 'alpha.v3.zip' :
                            urlForAlpha = inputURL
                        elif inputFileName == 'hla_ambigs.xml.zip' :
                            urlForHlaambigs = inputURL
                        else:
                            qMessTxt = f"Unknown parameter in url_config.txt:\n{inputFileName}."
                            QMessageBox.about(self, 'Unknown parameter', qMessTxt)
                fi.close()
            except:
                QMessageBox.about(self, "Error", "Something went wrong reading from url_config.txt")
        else:
            QMessageBox.about(self,"Error", "No URL configuration file\n(url_config.txt) found!") 
        

        btnSaveSources =QPushButton('Save')
        btnCancelSources =QPushButton('Cancel')
        btnCancelSources.setStyleSheet(GUI_miscFeatures.button_style_cancel)
        self.labSource1 = QLabel('hla_nom_p.txt') 
        self.sourceEdit1 = QLineEdit(urlForHlanomp)
        self.labSource2 = QLabel('hla_nom_g.txt') 
        self.sourceEdit2 = QLineEdit(urlForHlanomg)
        self.labSource3 = QLabel('alpha.v3.zip') 
        self.sourceEdit3 = QLineEdit(urlForAlpha)
        self.labSource4 = QLabel('hla_ambigs.xml.zip') 
        self.sourceEdit4 = QLineEdit(urlForHlaambigs)

        grid.addWidget(self.labSource1, 0, 1)
        grid.addWidget(self.sourceEdit1, 0, 2)
        grid.addWidget(self.labSource2, 1, 1)
        grid.addWidget(self.sourceEdit2, 1, 2)
        grid.addWidget(self.labSource3, 2, 1)
        grid.addWidget(self.sourceEdit3, 2, 2)
        grid.addWidget(self.labSource4, 3, 1)
        grid.addWidget(self.sourceEdit4, 3, 2)
        grid.addWidget(btnCancelSources, 4,2)
        grid.addWidget(btnSaveSources, 4,2)

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(btnCancelSources)   
        hbox1.addWidget(btnSaveSources)   

        sourceFrame.setLayout(grid)
        layoutAll.addWidget(sourceFrame)
        layoutAll.addLayout(hbox1)
        self.setLayout(layoutAll)

        # button action
        btnSaveSources.clicked.connect(self.saveSources_test)  #save parameters  
        btnCancelSources.clicked.connect(self.close)
        
        self.show()

    # Functions
    def saveSources_test(self):
        """saves URLInformation to url_config.txt
        """
        reply = QMessageBox.question(self, 'Save changes', 'Are you sure you want to save changes to the URL configuration file?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            fi = open(self.pathURLconfig, 'w')
            txt = "{}={}\n".format(self.labSource1.text(), self.sourceEdit1.text())  
            fi.write(str(txt))    
            txt = "{}={}\n".format(self.labSource2.text(), self.sourceEdit2.text())   
            fi.write(str(txt)) 
            txt = "{}={}\n".format(self.labSource3.text(), self.sourceEdit3.text())   
            fi.write(str(txt)) 
            txt = "{}={}\n".format(self.labSource4.text(), self.sourceEdit4.text())     
            fi.write(str(txt))
            fi.close()
        self.close()





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
            painter.drawLine(0, -4, 0, -10)
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
        