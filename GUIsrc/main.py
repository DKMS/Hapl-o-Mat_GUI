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

main.py
Main window

@author: Ute Solloch
'''

# fbs app special
# from fbs_runtime.application_context.PyQt5 import ApplicationContext
# # import pkg_resources.py2_warn

# import modules:
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QRadioButton, QPushButton, QLabel,  
        QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter, QLineEdit,
        QCheckBox, QGroupBox, QFrame, QMainWindow, QMessageBox, QFileDialog, QToolTip)   
from PyQt5.QtCore import Qt, QDateTime, QTimer, pyqtSlot
from PyQt5.QtGui import QPixmap, QPainter, QColor
from functools import partial
from pathlib import Path
import sys, os, time, platform
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

# import own modules
import GUI_BuildData, GUI_SetParameters, GUI_miscFeatures

# # fbs app special
# class AppContext(ApplicationContext):
    # def run(self):
        # window = MainW()
        # window.show()
        # return self.app.exec_() 
        

class MainW(QMainWindow):
    """Main software window
    """
    def __init__(self):
        
        super().__init__()
        self.initUI()
 
        # platform and stylesheet       
        try:        
            styleFile = GUI_miscFeatures.CONFIGURATION_FILES[platform.system()]["styleSheet"]  
        except:
            print("StyleSheet: Your current OS is not supported.")
        # fbs app special
        self.setStyleSheet(open(styleFile, "r").read())
        # appctxt.app.setStyleSheet(open(appctxt.get_resource(styleFile)).read())            
        
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit Application', 'Are you sure you want to exit the application?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # # fbs special
            # print("Press Ctrl+C to return to prompt.")
            for widget in QApplication.topLevelWidgets():
                widget.close()
            event.accept()
        else:
            event.ignore()
        
    def initUI(self):
        """GUI definition
        """               
        
        self.setWindowTitle('Hapl-o-Mat')               
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.grid = QGridLayout()
        self.statusBar().showMessage('Ready')

        central_widget.setLayout(self.grid)
        
        QToolTip.setFont(QtGui.QFont('SansSerif', 10))        
        self.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12pt } ")        
        self.htfnr = 0
        self.dirHap = ''
        
        # Pixmaps
        global pixmap_TT
        global pixmap_Tick
        global pixmap_Icon
        global pixmap_Error
        global pixmap_None
        global pixmap_Wait
        global pixmap_Caution

        #fbs app special
        # pixmap_Tick = QPixmap(appctxt.get_resource("tick.png")).scaledToWidth(20)
        # pixmap_Icon = QPixmap(appctxt.get_resource("logo.png")).scaledToWidth(150)
        # pixmap_Error = QPixmap(appctxt.get_resource("error.png")).scaledToWidth(30)
        # pixmap_None = QPixmap(appctxt.get_resource("none.png")).scaledToWidth(30)
        # pixmap_Wait = QPixmap(appctxt.get_resource("progress3.png")).scaledToWidth(30)
        # pixmap_Caution = QPixmap(appctxt.get_resource("caution.png")).scaledToWidth(30)
        pixmap_Tick = QPixmap(os.path.join("Icons", "tick.png")).scaledToWidth(20)
        pixmap_Icon = QPixmap(os.path.join("Icons", "logo.png")).scaledToWidth(150)
        pixmap_Error = QPixmap(os.path.join("Icons", "error.png")).scaledToWidth(30)
        pixmap_None = QPixmap(os.path.join("Icons", "none.png")).scaledToWidth(30)
        pixmap_Wait = QPixmap(os.path.join("Icons", "progress3.png")).scaledToWidth(30)
        pixmap_Caution = QPixmap(os.path.join("Icons", "caution.png")).scaledToWidth(30)
        
        global dirParent
        self.isDataBD = 0
        self.inpForm = None
        self.signalBusy = 0     #states: 0-no Process yet, 1-process busy, 2-process finished
        self.switchLoadSet = 0        
                        
        # create Frames
        self.create_HeaderFrame()        
        self.create_SetParametersFrame()
        self.create_BuildDataFrame()
        self.create_ResultsFrame()
        self.create_RunFrame()
        
        # Set layout MainWindow     
        central_widget.setLayout(self.grid)
        
        # GUIsrc working directory      
        dirParent = os.getcwd()
        
        # create default parameter file
        self.pathParaDefault = str(os.path.join(dirParent, "parametersDefault"))
        self.createParamFile_default()
        
        # create haplomat path file and initiate pathFrame
        self.pathHapPath = str(os.path.join(dirParent, "pathHaplomat"))
        my_path = Path(self.pathHapPath)    
        if my_path.is_file():
            with open(self.pathHapPath) as f:
                first_line = f.readline()
                self.dirHap = first_line.rstrip('\r\n')
        self.create_PathFrame()
        
        self.showMaximized()
        
    #HeaderFrame
    def create_HeaderFrame(self):
        """defines the header frame of the Main Window
        """
        headerFrame = QFrame(self)
        headerFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)  
        headerFrame.setStyleSheet("background-color: #ddd9d8;") 
        layoutHeader = QHBoxLayout()
        labLogo = QLabel(self)
        labLogo.setPixmap(pixmap_Icon)
        labHeader = QLabel(self)
        labHeader.setTextFormat(Qt.RichText)
        labHeader.setText("<font size='5'> <b>Hapl-o-Mat - A software tool for haplotype frequency estimation</b></font>")
        btnTutorial = QPushButton("Manual", self)
        btnTutorial.setObjectName("tutorial")
        btnTutorial.setStyleSheet(GUI_miscFeatures.button_style_info)
        btnInfo = QPushButton("About", self)
        btnInfo.setObjectName("information")
        btnInfo.setStyleSheet(GUI_miscFeatures.button_style_info)
        
        layoutHeader.addWidget(labLogo)
        layoutHeader.addStretch(5)
        layoutHeader.addWidget(labHeader)
        layoutHeader.addStretch(5)
        layoutHeader.addWidget(btnTutorial)
        layoutHeader.addWidget(btnInfo)
        headerFrame.setLayout(layoutHeader)
        
        self.grid.addWidget(headerFrame, 0, 0,1,11)
        
        # Button Actions
        btnTutorial.clicked.connect(self.display_dialog)
        btnInfo.clicked.connect(self.display_dialog)
        
    #PathFrame
    def create_PathFrame(self):
        """defines the frame for indication of path to Hapl-o-Mat files
        """
        pathFrame = QGroupBox("Set path to 'haplomat' folder")
        layoutPHVert = QVBoxLayout()
        layoutPHHori = QHBoxLayout()
        labPathHap = QLabel()
        labPathHap.setText("Please set path\nto Hapl-o-Mat folder.")
        btnPathHap = QPushButton("...", self)
        self.labTickPath = QLabel()
        self.labTickPath.setLineWidth(1)
        btnPathHap.setToolTip("""Please set the path to the folder containing the executable 'haplomat'.""")
        self.labHapPath = QtWidgets.QLabel() 
        self.labHapPath.setStyleSheet(GUI_miscFeatures.label_style_info)
        self.labHapPath.setWordWrap(True)
        
        layoutPHHori.addWidget(self.labTickPath)
        layoutPHHori.addStretch(1)
        layoutPHHori.addWidget(btnPathHap)
        layoutPHVert.addLayout(layoutPHHori)
        layoutPHVert.addWidget(self.labHapPath)
        pathFrame.setLayout(layoutPHVert)
        
        if self.dirHap != '':
            self.labHapPath.setText(self.dirHap)
            self.pathHapDir = os.path.relpath(self.dirHap, start=os.curdir)
            self.labTickPath.setPixmap(pixmap_Tick)
            self.checkForData()
                
        self.grid.addWidget(pathFrame, 1, 0, 1, 4)
        
        # Button Actions
        btnPathHap.clicked.connect(self.browse_folder_Hap)
    
    #Frame BuildData
    def create_BuildDataFrame(self):
        """defines the frame for IPD-IMGT/HLA-data retrieval
        """
        buildDataFrame = QGroupBox("Update IPD-IMGT/HLA data")
        LayoutBuildData = QVBoxLayout()
        LayoutBDLine = QHBoxLayout()
          
        self.labOutputBuildData = QtWidgets.QLabel()
        self.labOLociBuildData = QtWidgets.QLabel()
        self.labOLociBuildData.setTextFormat(Qt.RichText)
        self.labOLociBuildData.setWordWrap(True)
        btnBuildData = QPushButton("Update", self)
        btnDataSource = QPushButton("Sources", self)

        btnBuildData.setToolTip("""Hapl-o-Mat relies on information about the HLA nomenclature provided by external files. 
        After the first download of Hapl-o-Mat the initial data update is mandatory. 
        As the HLA nomenclature is constantly evolving, e.g. by inclusion of new alleles or new multiple allele codes, it
        is important to update this data regularly.""")
        btnDataSource.setToolTip("""Lists the current URL sources of the data downloading process. URLs can be edited manually.""")
        btnDataSource.setStyleSheet(GUI_miscFeatures.button_style_info)
        self.labTickBD = QLabel()
        self.labTickBD.setLineWidth(1)
        
        LayoutBDLine.addWidget(self.labTickBD)
        LayoutBDLine.addWidget(self.labOutputBuildData)
        LayoutBDLine.addStretch(1)
        LayoutBDLine.addWidget(btnDataSource)
        LayoutBDLine.addWidget(btnBuildData)
        LayoutBuildData.addLayout(LayoutBDLine)
        LayoutBuildData.addWidget(self.labOLociBuildData)    
        buildDataFrame.setLayout(LayoutBuildData)
        self.grid.addWidget(buildDataFrame, 2,0,1,4)
                
        # Button Actions
        btnBuildData.clicked.connect(self.create_data_prep)
        btnDataSource.clicked.connect(self.view_data_sources)
    
    #Frame SetParameters
    def create_SetParametersFrame(self):
        """defines the frame for parameter settings
        """
        wdirFrame = QGroupBox("Set run parameters")
        layoutWdir = QVBoxLayout()
        layoutSet = QHBoxLayout()
        # Set Frame
        btnSetParameters = QPushButton("Parameters", self)
        btnSetParameters.setToolTip("""Please push the 'Parameters' button to set run parameters or load an existing parameter file.
        Parameters can either be set manually via input mask or loaded from a valid existing parameter file.""")        
        self.labTickPa = QLabel()
        self.labTickPa.setLineWidth(1) 
        layoutSet.addWidget(self.labTickPa)
        layoutSet.addStretch(1)
        layoutSet.addWidget(btnSetParameters)

        layoutWdir.addLayout(layoutSet)
        # InfoFrame
        self.labParaBD = QtWidgets.QLabel() 
        self.labParaBD.setTextFormat(Qt.RichText)
        self.labParaBD.setWordWrap(True)
        layoutInfoFrame= QVBoxLayout()
        layoutInfoFrame.addWidget(self.labParaBD)
        layoutWdir.addLayout(layoutInfoFrame)        
        wdirFrame.setLayout(layoutWdir)        
        self.grid.addWidget(wdirFrame, 3, 0,1,4)        
        # Button Actions
        btnSetParameters.clicked.connect(self.set_load_Parameters)
        
    def create_RunFrame (self):
        """defines the frame where Hapl-o-Mat can be started and output is displayed
        """
        runFrame = QGroupBox("Run Hapl-o-Mat")
        LayoutRun = QVBoxLayout()          
        self.labOutputRun = QtWidgets.QTextBrowser() 
        self.labOutputRun.setStyleSheet("color: white; background-color: black;")
        self.labOutputRun.verticalScrollBar().setStyleSheet('background: #d8d6d6; color: #000000')
        self.labLog = QLabel()
        self.labLog.setStyleSheet(GUI_miscFeatures.label_style_info)
        self.labLog.setWordWrap(True)

        LayoutRunLine = QHBoxLayout()
        btnRun = QPushButton("Run", self)
        btnRun.setStyleSheet(" QPushButton:hover { border: 2px solid #78D64A }" 
                             "QPushButton { background-color: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #ADFF2F, stop: 1 #78D64A); }" )  
        self.btnKillHaplomat =QPushButton("Abort", self)
        self.btnKillHaplomat.setStyleSheet(GUI_miscFeatures.button_style_cancel)
        self.waitFrame = QFrame()
        LayoutRunLine.addWidget(self.waitFrame)
        LayoutRunLine.addWidget(self.btnKillHaplomat)
        LayoutRunLine.addWidget(btnRun)
        LayoutRunLine.setAlignment(Qt.AlignRight)
        LayoutRun.addLayout(LayoutRunLine)
        LayoutRun.addWidget(self.labOutputRun) 
        LayoutRun.addWidget(self.labLog)
        runFrame.setLayout(LayoutRun)
        self.grid.addWidget(runFrame, 4,0,1,4)        
        # Button Actions
        btnRun.clicked.connect(self.run_Haplomat_Test)

    # Frame results
    def create_ResultsFrame(self):
        """defines the frame that displays the results of the Hapl--Mat run
        """
        resultsFrame = QGroupBox("Results")
        LayoutResFrame = QVBoxLayout()
        StatsFrame1 = QFrame()
        self.StatsFrame2 = QFrame()
        layFrame1 = QHBoxLayout()
        layFrame2 = QHBoxLayout()
        StatsBox = QHBoxLayout()
        labStat = QLabel('Statistics:')
        boldFont=QtGui.QFont()
        boldFont.setBold(True)
        labStat.setFont(boldFont)
        labNrHt = QLabel('Total number of haplotypes:')
        self.labStatRes = QtWidgets.QLabel()
        self.labStatRes.setStyleSheet(GUI_miscFeatures.label_style_info)
        labNrGt = QLabel('Number of genotypes (n):')
        self.labStatGT = QtWidgets.QLabel()
        self.labStatGT.setStyleSheet(GUI_miscFeatures.label_style_info)
        labNrHtEps = QLabel('1/(2*n)=')
        self.labStatEps = QtWidgets.QLabel()
        self.labStatEps.setStyleSheet(GUI_miscFeatures.label_style_info)
        labNrHtSum = QLabel('Sum of cut haplotype frequencies:')
        self.labStatSum = QtWidgets.QLabel()
        self.labStatSum.setStyleSheet(GUI_miscFeatures.label_style_info)        
        
        layFrame1.addWidget(labStat)
        layFrame2.addWidget(labNrHt)
        layFrame2.addWidget(self.labStatRes)
        layFrame2.addStretch(1)
        layFrame2.addWidget(labNrGt)
        layFrame2.addWidget(self.labStatGT)
        layFrame2.addStretch(1)
        layFrame2.addWidget(labNrHtEps)
        layFrame2.addWidget(self.labStatEps)
        layFrame2.addStretch(1)
        layFrame2.addWidget(labNrHtSum)
        layFrame2.addWidget(self.labStatSum)
        layFrame2.addStretch(20)
        
        StatsFrame1.setLayout(layFrame1)
        self.StatsFrame2.setLayout(layFrame2)
        
        SepFrame = QFrame()
        SepFrame.setFrameShape(QFrame.HLine)
        SepFrame.setStyleSheet("border: 1px solid #ababab;")
        ChoiceFrame = QFrame()
        ChoiceBox = QHBoxLayout()
        labDisp = QLabel('Display:')
        labDisp.setFont(boldFont)
        self.textEdit_TopX = QLineEdit('100', self)
        self.radioButton1 = QRadioButton("TOP", self)
        self.radioButton2 = QRadioButton("All", self)
        self.radioButton3 = QRadioButton("All haplotypes with frequency >= 1/(2*n)", self)
        self.radioButton4 = QRadioButton("All haplotypes with cumulated frequency <=", self)
        self.radioButton1.setChecked(True)
        self.textEdit_Cum = QLineEdit('0.995', self)
        ChoiceBox.addWidget(labDisp)
        ChoiceBox.addStretch(1)
        ChoiceBox.addWidget(self.radioButton1)
        ChoiceBox.addWidget(self.textEdit_TopX)
        ChoiceBox.addStretch(1)
        ChoiceBox.addWidget(self.radioButton2)
        ChoiceBox.addStretch(1)
        ChoiceBox.addWidget(self.radioButton3)
        ChoiceBox.addStretch(1)
        ChoiceBox.addWidget(self.radioButton4)
        ChoiceBox.addWidget(self.textEdit_Cum)
        ChoiceBox.addStretch(20)        
        self.labTopHTF = QtWidgets.QTextBrowser()
        
        #Plot Frame
        splitter1 = customSplitterHorizontal(Qt.Horizontal)
        # splitter1.setHandleWidth(8)
        self.plot1 = pg.PlotWidget(title="Haplotype frequencies", bottom = "Haplotype rank", left = "Frequency")
        self.plot2 = pg.PlotWidget(title="Epsilon", bottom = "Iteration #", left = "Epsilon value")
        self.plot1.showGrid(True, True)
        self.plot1.setLogMode(False, True)
        # self.plot1.setMenuEnabled(False)    
        self.plot1.plotItem.ctrlMenu = None  
        self.plot2.showGrid(True, True)
        self.plot2.setLogMode(False, True)    
        self.plot2.plotItem.ctrlMenu = None         
        
        FramePlot1 = QFrame()
        ChoiceBoxPlot1 = QVBoxLayout()  
        LayoutChoice1 = QHBoxLayout()     
        labPlot1 = QLabel('Display Log format:')
        self.Plot1CheckBoxX = QCheckBox("x-axis")
        self.Plot1CheckBoxY = QCheckBox("y-axis")
        self.Plot1CheckBoxY.setChecked(True)
        LayoutChoice1.addWidget(labPlot1)
        LayoutChoice1.addWidget(self.Plot1CheckBoxX)
        LayoutChoice1.addWidget(self.Plot1CheckBoxY)
        LayoutChoice1.setAlignment(Qt.AlignLeft)        
        
        FramePlot2 = QFrame()
        ChoiceBoxPlot2 = QVBoxLayout()
        LayoutChoice2 = QHBoxLayout()    
        labPlot2 = QLabel('Display Log format:')
        self.Plot2CheckBoxX = QCheckBox("x-axis", self)
        self.Plot2CheckBoxY = QCheckBox("y-axis", self)
        self.Plot2CheckBoxY.setChecked(True)
        btnReset =QPushButton("Reset plots", self)
        LayoutChoice2.addWidget(labPlot2)
        LayoutChoice2.addWidget(self.Plot2CheckBoxX)
        LayoutChoice2.addWidget(self.Plot2CheckBoxY)
        LayoutChoice2.addStretch(1)
               
        ChoiceBoxPlot1.addWidget(self.plot1)
        ChoiceBoxPlot1.addLayout(LayoutChoice1)
        FramePlot1.setLayout(ChoiceBoxPlot1)
        ChoiceBoxPlot2.addWidget(self.plot2)
        ChoiceBoxPlot2.addLayout(LayoutChoice2)
        FramePlot2.setLayout(ChoiceBoxPlot2)

        FrameReset = QFrame()
        layoutReset = QHBoxLayout()
        layoutReset.setSpacing(0)
        layoutReset.addStretch(2)
        layoutReset.addWidget(btnReset)
        FrameReset.setLayout(layoutReset)
        
        # Checkboxes: state changed action
        self.Plot1CheckBoxX.stateChanged.connect(lambda:self.checkState1())
        self.Plot1CheckBoxY.stateChanged.connect(lambda:self.checkState1())
        self.Plot2CheckBoxX.stateChanged.connect(lambda:self.checkState2())
        self.Plot2CheckBoxY.stateChanged.connect(lambda:self.checkState2())
                
        # Set Layout
        StatsBox.addWidget(StatsFrame1)
        StatsBox.addWidget(self.StatsFrame2)
        LayoutResFrame.addLayout(StatsBox)
        LayoutResFrame.addWidget(SepFrame)
        ChoiceFrame.setLayout(ChoiceBox)
        LayoutResFrame.addWidget(ChoiceFrame)         
        
        splitter1.addWidget(FramePlot1)
        splitter1.addWidget(FramePlot2)        
        splitter2 = customSplitterVertical(Qt.Vertical)        
        # splitter2.setHandleWidth(8)
        splitter2.addWidget(self.labTopHTF)
        splitter2.addWidget(splitter1)
        LayoutResFrame.addWidget(splitter2)  
        LayoutResFrame.addWidget(FrameReset) 

        resultsFrame.setLayout(LayoutResFrame)        
        self.grid.addWidget(resultsFrame, 1,4,4,7)
        self.StatsFrame2.hide()
        
        # Button action
        self.radioButton1.clicked.connect(lambda:self.radioBtn_State())
        self.radioButton2.clicked.connect(lambda:self.radioBtn_State())
        self.radioButton3.clicked.connect(lambda:self.radioBtn_State())
        self.radioButton4.clicked.connect(lambda:self.radioBtn_State())
        btnReset.clicked.connect(lambda:self.radioBtn_State())
        self.textEdit_TopX.returnPressed.connect(self.toggle_Rb1)
        self.textEdit_Cum.returnPressed.connect(self.toggle_Rb4)



#############################
# Functions
 
    @pyqtSlot()
    def display_dialog(self):                                            
        """
        Display dialogs
        With object name defines which option to give                                                        
        """
        dialog_parameters = {
            "tutorial": {
                "file_type": "htm",
                "file_name": "ManualHapl-o-MatViaGUI.htm",
                "parent": self
            },
            "information": {
                "file_type": "txt",
                "file_name": "Licenses.txt",
                "parent": self
            }
        }
        self.dialog = GUI_miscFeatures.InformationDialog(**dialog_parameters[self.sender().objectName()])
        self.dialog.move(self.pos())

    def browse_folder_Hap(self):
        """opens file dialog for choice of the results folder
        """     
        dirHapBackup = self.dirHap
        if (self.dirHap != ''):
            my_path = os.path.relpath(self.dirHap, start=os.curdir)
        else:
            my_path = os.path.join('..')
        self.dirHap = QFileDialog.getExistingDirectory(self, "Choose 'Hapl-o-Mat' folder", my_path)
        if (self.dirHap == ''):     # e.g. if QFileDialog finished by 'cancel'
            self.dirHap = dirHapBackup
        self.pathHapDir = os.path.relpath(self.dirHap, start=os.curdir)
        self.labTickPath.setPixmap(pixmap_Tick)
        self.labHapPath.setText(self.dirHap)
        self.checkForData()
        pathHapFile = open(self.pathHapPath, 'w+')
        pathHapFile.truncate(0)
        pathHapFile.write(self.dirHap+'\n')        
        pathHapFile.close()
        
    def checkForData(self):
        # Last data update
        self.path_data = os.path.join(self.pathHapDir,"data","AllAllelesExpanded.txt")
        my_path = Path(self.path_data)        
        if my_path.is_file():
            self.isDataBD = 1
            self.updateInfo()
        else:
            self.isDataBD = 0
            self.labOutputBuildData.setText('No data files available. Please update!')
            self.labOLociBuildData.setText('No locus data available.')
            self.labTickBD.setPixmap(pixmap_Error)
            self.listLociBD = []
            
        # Update package available?       
        self.fileBD = os.path.join(self.pathHapDir,"prepareData","BuildData.py")
        my_path1 = Path(self.fileBD)
        if not my_path1.is_file():
            textBD = self.labOutputBuildData.text()
            self.labOutputBuildData.setText(textBD+"\nUpdate package not available.\nPlease check correct setting\nof Hapl-o-Mat path.")
            self.labTickBD.setPixmap(pixmap_Error)
            self.labTickPath.setPixmap(pixmap_Error)
        
    def createParamFile_default(self):
        """creates the initial default parameter set
        """
        paraFile = open(self.pathParaDefault, 'w+')
        paraFile.truncate(0)
        paraFile.write('MINIMAL_FREQUENCY_GENOTYPES=1e-5\n')
        paraFile.write('DO_AMBIGUITYFILTER=false\n')
        paraFile.write('EXPAND_LINES_AMBIGUITYFILTER=false\n')
        paraFile.write('INITIALIZATION_HAPLOTYPEFREQUENCIES=perturbation\n')
        paraFile.write('EPSILON=1e-6\n')
        paraFile.write('CUT_HAPLOTYPEFREQUENCIES=1e-6\n')
        paraFile.write('RENORMALIZE_HAPLOTYPEFREQUENCIES=false\n')
        paraFile.write('SEED=0\n')
        paraFile.write('WRITE_GENOTYPES=true\n')
        paraFile.close()

    def view_data_sources(self):
        '''opens Dialog with editable list of download data sources.'''
        if self.dirHap == '':
                QMessageBox.about(self, "Error: No valid directory.", "Please set path to Hapl-o-Mat directory!") 
        else:
            self.viewDataSources = GUI_BuildData.ViewSources(self.pathHapDir)
            self.viewDataSources.setWindowTitle('Download data sources')
            self.viewDataSources.move(self.pos())

    def create_data_prep(self):
        """opens the window of the IPD-IMGT/HLA data update process (GUI_BuildData.CreateDataFrame)
        """
        if self.dirHap == '':
                QMessageBox.about(self, "Error: No valid directory.", "Please set path to Hapl-o-Mat directory!") 
        else:
            self.testData()
            
    def create_data(self):
        self.labTickBD.clear()
        self.labOLociBuildData.clear()
        self.createDataWin = GUI_BuildData.CreateDataFrame(self.pathHapDir)
        self.createDataWin.setWindowTitle('Update in progress ...')
        self.createDataWin.move(self.pos())
        self.createDataWin.stateBD.connect(self.indicateBDState)
        self.createDataWin.stateNoBD.connect(self.errorNoBuild)
            
    def testData(self):
        """searches for existing files in the prepareData folder and asks for instruction how to handle them.
        """
        self.pathBD = os.path.join(self.pathHapDir,"prepareData")
        fileEx = 0
        self.fileTest1 = os.path.join(self.pathBD, "hla_nom_p.txt")
        my_path = Path(self.fileTest1)            
        if my_path.is_file(): 
            fileEx = 1
        self.fileTest2 = os.path.join(self.pathBD, "hla_nom_g.txt")
        my_path = Path(self.fileTest2)            
        if my_path.is_file(): 
            fileEx = 1
        self.fileTest3 = os.path.join(self.pathBD, "alpha.v3.zip")
        my_path = Path(self.fileTest3)            
        if my_path.is_file(): 
            fileEx = 1
        self.fileTest4 = os.path.join(self.pathBD, "hla_ambigs.xml.zip")
        my_path = Path(self.fileTest4)            
        if my_path.is_file(): 
            fileEx = 1

        if fileEx > 0:
            self.msgBox = QMessageBox(self)
            self.msgBox.setIcon(QMessageBox.Warning)
            self.msgBox.setWindowTitle("File handling")
            self.msgBox.setText("Some of the download files needed for data processing are already present in the target directory and will not be refreshed. \nIf you want to download current data files please abort download process and remove files from Hapl-o-Mat directory 'predareData' (s. Tutorial). \nIf you have inserted the files manually, please ignore this message.")            
            self.msgBox.setStandardButtons(QMessageBox.Ok)        
            self.msgBox.exec_()
            self.msgBox.move(self.pos())

        self.create_data()

            
    def indicateBDState(self, stateBD):
        """processes the signal output of GUI_BuildData.CreateDataFrame
        """
        if stateBD == 'tick':
            self.labTickBD.setPixmap(pixmap_Tick)
            self.updateInfo()
        elif stateBD == 'error':
            if self.isDataBD == 0:
                self.labTickBD.setPixmap(pixmap_Error)
                self.updateInfo()
            elif self.isDataBD == 1:
                self.updateInfo()
                self.labTickBD.setPixmap(pixmap_Caution)
                textBD = self.labOutputBuildData.text()
                self.labOutputBuildData.setText("Data download aborted.\nAvailable data is used.\n" + textBD)                
                self.labOLociBuildData.setText(self.strLoc)                
                
    def errorNoBuild(self,stateNoBD):
        self.labTickBD.setPixmap(pixmap_Error)
        self.updateInfo()
        textBD = self.labOutputBuildData.text()
        self.labOutputBuildData.setText("Data download not possible.\nPlese check the correct installation of Hapl-o-Mat file system.\n" + textBD)
        self.labOLociBuildData.setText("No locus data available.")
                
    def updateInfo(self):
        """tests last update date, the need for data update, available loci 
            and creates the user information displayed on the BuildDataFrame
        """
        # Timestamp last update
        atime = round(time.time())
        atime_str = time.strftime("%b %d, %Y", time.gmtime(os.path.getmtime(self.path_data)))
        btime = round(os.stat(self.path_data).st_mtime)    
        diff = (atime-btime)/60
        if (diff > 130000):      # data update older than three months (130000min)
            self.labOutputBuildData.setText("Last data update:\n"+ str(atime_str) + "\nPlease consider an update.")
            self.labTickBD.setPixmap(pixmap_Caution)
        else:
            self.labOutputBuildData.setText("Last data update:\n"+ str(atime_str))
            self.labTickBD.setPixmap(pixmap_Tick)
        # available Loci
        self.labOLociBuildData.clear()
        dictLociBD = {}
        self.listLociBD = []
        f = open(self.path_data, 'r')
        for line in f:
            line = line.rstrip('\r\n')
            loc = line.split('*')[0]
            dictLociBD[loc] = 1
        for key,val in dictLociBD.items():
            self.listLociBD.append(key)
        self.listLociBD.sort()
        self.strLoc = "available Loci:<br><font color= '#0000ff'> "
        z = 0
        for i in self.listLociBD:
            z+=1
            if z==1:            
                self.strLoc = self.strLoc + i
            else:
                zz= z/10
                if int(zz) == zz:
                   self.strLoc = self.strLoc + ", <br>" + i
                else:
                    self.strLoc = self.strLoc + "," + i
        self.labOLociBuildData.setText(self.strLoc)        

    def set_load_Parameters(self):
        """clears display of last run and opens window for parameter selection
        """        
        # Check for Hapl-o-Mat file system
        if (self.dirHap == ''):      
            QMessageBox.about(self, "Error: Hapl-o-Mat files not accessible.", "Please set the path to Hapl-o-Mat directory and update IPD-IMGT/HLA data if necessary!") 
        else:
            # open parameter file
            self.para = GUI_SetParameters.Parameters(self.listLociBD, self.dirHap)
            self.para.setWindowTitle('Set or load run parameters')            
            self.para.strParaSet.connect(self.setTickPara)
            self.para.show()
            self.para.move(self.pos())
    
    def setTickPara(self, strParaSet):
        """processes signal from parameter window and displays chosen run parameters on main window
        """
        self.labTickPa.setPixmap(pixmap_Tick)
        arrPara = strParaSet.split('#')
        self.runIdIn = arrPara[3]
        self.inpForm = arrPara[1]
        self.resRun = arrPara[5]
        resolution = arrPara[0]
        text = "Input file: <font color= '#0000ff'>"+ arrPara[4]+"<br></font>Resolution: <font color= '#0000ff'>" + resolution\
            +"<br></font>Epsilon: <font color= '#0000ff'>"+ arrPara[2]+"<br></font>RunID: <font color= '#0000ff'>"+ arrPara[3]
        self.labParaBD.setText(text)
        self.labOutputRun.clear()
        self.labLog.clear()
        self.labStatRes.clear()
        self.labStatGT.clear()
        self.labStatEps.clear()
        self.labStatSum.clear()
        self.labTopHTF.clear()
        self.plot1.clear()
        self.plot2.clear()
        self.StatsFrame2.hide()
        self.switchLoadSet = 1
        
    def run_Haplomat_Test(self):
        """Tests whether conditions for Hapl-o-Mat run are fulfilled
        """
        if (self.switchLoadSet == 0):
             QMessageBox.about(self, "Error: Run parameters incomplete.", "Please set parameters before starting Hapl-o-Mat!")
        else:
            self.statusBar().showMessage('Hapl-o-Mat running ...')
            self.run_Haplomat()
    
    def run_Haplomat(self):
        """triggers start of Hapl-o-Mat, output display, real time epsilon display, 
        and result display when run is finished
        """
        self.signalBusy = 1
        self.labOutputRun.clear()
        self.labStatRes.clear()
        self.labStatGT.clear()
        self.labStatEps.clear()
        self.labStatSum.clear()
        self.labLog.clear()
        self.plot1.clear()
        self.plot2.clear()
        self.labTopHTF.clear()
        self.StatsFrame2.hide()
        datetime = QDateTime.currentDateTime()
        
        # remove old epsilon file
        if self.inpForm == 'MAC':
            paraFile = os.path.join(self.pathHapDir,"parametersMAC")
        elif self.inpForm == 'GLSC':
            paraFile = os.path.join(self.pathHapDir,"parametersGLSC")
        else:
            QMessageBox.about(self, "Error: Run parameters incomplete.", "Please set parameters before starting Hapl-o-Mat!")
            return
        f = open(paraFile, 'r')
        for line in f:
            row = line.split('=')
            if(row[0] == 'FILENAME_EPSILON_LOGL'): #Epsilon file
                pathEpsilon = os.path.join("..", str(row[1]).strip())
            else:
                continue
        if(os.path.isfile(pathEpsilon)):
            os.remove(pathEpsilon)
            
        #run Process
        self.currDir_US = os.getcwd()
        self.labOutputRun.append('Hapl-o-Mat started.\n'+ datetime.toString())
        pathLog = self.resRun
        # runIDLog = self.runID+'_'
        self.nameLog = str(os.path.join(pathLog, self.runIdIn+'log.dat'))        
        self.logFile = open(self.nameLog, 'w')
        self.procOK = 0
        try: dirParent
        except NameError:        
            QMessageBox.about(self, "Error: No directory.", "Please set working directory!") 
        else:
            if platform.system() == "Windows":
                self.processHaplo = QtCore.QProcess()
                os.chdir(self.dirHap)   #Win special [05.10.2020]
                self.processHaplo.readyReadStandardOutput.connect(lambda: self.labOutputRun.append(str(self.processHaplo.readAllStandardOutput().data().decode('UTF-8')))) 
                if self.inpForm == 'MAC':
                    QtCore.QTimer.singleShot(100, partial(self.processHaplo.start, "Hapl-o-Mat.exe", ["MAC"]))
                elif self.inpForm == 'GLSC':
                    QtCore.QTimer.singleShot(100, partial(self.processHaplo.start, "Hapl-o-Mat.exe", ["GLSC"]))           
                self.processHaplo.waitForStarted()            
                # write out epsilon
                self.timer = QTimer()
                self.timer.setInterval(10000)
                self.timer.timeout.connect(self.display_Epsilon)
                self.timer.start()
                # Process handles
                self.btnKillHaplomat.clicked.connect(self.processHaplo.kill)
                self.processHaplo.finished.connect(self.status_Haplomat)
            elif (platform.system() == "Linux") or (platform.system() == "Darwin"):
                self.processHaplo = QtCore.QProcess()
                self.processHaplo.setWorkingDirectory(os.path.join(self.pathHapDir))
                self.processHaplo.readyReadStandardOutput.connect(lambda: self.labOutputRun.append(str(self.processHaplo.readAllStandardOutput().data().decode('UTF-8')))) 
                if self.inpForm == 'MAC':
                    QtCore.QTimer.singleShot(100, partial(self.processHaplo.start, os.path.join(".","haplomat MAC")))
                elif self.inpForm == 'GLSC':
                    QtCore.QTimer.singleShot(100, partial(self.processHaplo.start, os.path.join(".","haplomat GLSC")))            
                self.processHaplo.waitForStarted()
                # write out epsilon
                self.timer = QTimer()
                self.timer.setInterval(10000)
                self.timer.timeout.connect(self.display_Epsilon)
                self.timer.start()
                # Process handles
                self.btnKillHaplomat.clicked.connect(self.processHaplo.kill)
                self.processHaplo.finished.connect(self.status_Haplomat)
            
    def status_Haplomat(self, exitCode, exitStatus):
        """processes status output of Hapl-o_Mat process
        """
        if platform.system() == "Windows":
            os.chdir(self.currDir_US)        #Win special [05.10.2020]
        self.signalBusy = 2
        self.timer.stop()
        self.statusBar().showMessage('Ready.')
        infoLog = 'Log file saved as ' + self.nameLog
        datetime = QDateTime.currentDateTime()
        if exitStatus == 0 and exitCode == 0:         # Status 0: regularly finished        
            self.labOutputRun.append('\nFinished!\n'+ datetime.toString())
            self.procOK = 1
        elif exitStatus == 1:       # Status 1: process killed          
            self.labOutputRun.append('\nCancelled!\n' + datetime.toString()) 
        elif exitCode != 0:
            self.labOutputRun.append('\nError!\n' + datetime.toString())    
        #Log
        outputLog = self.labOutputRun.toPlainText()
        self.logFile.write(outputLog)
        self.logFile.close()
        self.labLog.setText(infoLog)
        self.make_Stats(exitCode, exitStatus)
            
    def toggle_Rb1(self):
        """radio button toggle after return pressed action
        """
        self.radioButton1.setChecked(True)
        self.rb1EntryCheck()
        self.display_Results()
        
    def toggle_Rb4(self):
        """radio button toggle after return pressed action
        """
        self.radioButton4.setChecked(True)
        self.rb4EntryCheck()        
        self.display_Cum()
        
    def radioBtn_State(self):
        """processes check status of radio button choice for result display
        """ 
        if (self.radioButton1.isChecked()== True):
            self.rb1EntryCheck()
            self.display_Results()
        elif (self.radioButton2.isChecked()== True):
            self.display_All()
        elif (self.radioButton3.isChecked()== True):
            self.display_Eps()
        elif (self.radioButton4.isChecked()== True):
            self.rb4EntryCheck()
            self.display_Cum()

            
    def rb1EntryCheck(self):
        """tests text entry for validity
        """
        try:
            maxLine = int(self.textEdit_TopX.text())
        except ValueError:
            msgTop = QMessageBox(self)
            msgTop.setIcon(QMessageBox.Warning)
            msgTop.setWindowTitle("Invalid entry.")
            msgTop.setText("Please choose an integer value for TOP haplotype number display.")
            msgTop.setStandardButtons(QMessageBox.Ok)
            msgTop.exec_()
            msgTop.move(self.pos())
            return
          
    def rb4EntryCheck(self):
        """tests text entry for validity
        """
        try:
            cumFreq = float(self.textEdit_Cum.text())
        except ValueError:
            msgCum = QMessageBox(self)
            msgCum.setIcon(QMessageBox.Warning)
            msgCum.setWindowTitle("Invalid entry.")
            msgCum.setText("Please choose float value between 0 and 1 for cumulated frequency (e.g. 0.995).")
            msgCum.setStandardButtons(QMessageBox.Ok)
            msgCum.exec_()
            msgCum.move(self.pos())
            return
            
    def checkState1(self):
        """processes check status of log axes choice of plot1 in the result display
        """
        #Plot1
        if (self.Plot1CheckBoxX.isChecked() == True):            
            if (self.Plot1CheckBoxY.isChecked() == True):
                self.plot1.setLogMode(True, True)
            else:
                self.plot1.setLogMode(True, False)
        else:
            if (self.Plot1CheckBoxY.isChecked() == True):
                self.plot1.setLogMode(False, True)
            else:
                self.plot1.setLogMode(False, False)
                
    def checkState2(self):
        """processes check status of log axes choice of plot2 in the result display
        """
        if (self.Plot2CheckBoxX.isChecked() == True):
            if (self.Plot2CheckBoxY.isChecked() == True):
                self.plot2.setLogMode(True, True)
            else:
                self.plot2.setLogMode(True, False)
        else:
            if (self.Plot2CheckBoxY.isChecked() == True):
                self.plot2.setLogMode(False, True)
            else:
                self.plot2.setLogMode(False, False)
                
    def make_Stats(self,  exitCode, exitStatus):
        self.labStatRes.clear()
        self.labStatGT.clear()
        self.labStatEps.clear()
        self.labStatSum.clear()
        self.StatsFrame2.show()
        if self.procOK == 1:       # Status 1: process terminated without errors   
            if self.inpForm == 'MAC':
                paraFile = os.path.join(self.pathHapDir,"parametersMAC")
            elif self.inpForm == 'GLSC':
                paraFile = os.path.join(self.pathHapDir,"parametersGLSC")
            # number of ht; cumulated frequency hash
            f = open(paraFile, 'r')
            for line in f:
                row = line.split('=')
                if (row[0] == 'FILENAME_HAPLOTYPEFREQUENCIES'): # htf file
                    pathHTF = os.path.join("..", str(row[1]).strip())
                else:
                    continue
            fHTF = open(pathHTF, 'r')
            self.htfnr = 0
            freqSum = 0
            self.cumList = []
            for line in fHTF:            
                self.htfnr += 1
                raw = line.strip()
                freq = float(raw.split('\t')[1])
                freqSum = freqSum + freq
                self.cumList.append(freqSum)
            fHTF.close()
            self.labStatRes.setText(str(self.htfnr))              
            # read LOG-file
            log = open(self.nameLog, 'r')
            for line in log:
                if 'Leftover genotypes' in line:
                    raw = line.strip()
                    gtnr = raw.split(': ')[1]
                elif 'Sum cutted haplotype frequencies' in line:
                    raw = line.strip()
                    sumHT = raw.split(': ')[1]
            self.labStatGT.setText(str(gtnr))
            if int(gtnr) > 0:                  
                self.labStatSum.setText(str(sumHT))
                epsStat = 1/(2*int(gtnr))
                epsStatForm ='{:.3e}'.format(epsStat)
                self.labStatEps.setText(str(epsStatForm))
                
                # ht with htf >= epsilon or 
                fHTF = open(pathHTF, 'r')
                self.epsNr = 0
                for line in fHTF:
                    raw = line.strip()
                    freq = float(raw.split('\t')[1])
                    if freq >= epsStat:
                        self.epsNr += 1
                fHTF.close()
                self.radioBtn_State()
            else:
                self.labOutputRun.append('\nNo genotypes evaluated.!\n')

                
    def display_Results(self):
        """induces the display of the results of the finished Hapl-o-Mat run
        """
        if (self.signalBusy != 2):
            self.labTopHTF.clear()
            self.plot1.clear()
            self.plot2.clear()
        else:
            self.labTopHTF.clear()
            maxLine = int(self.textEdit_TopX.text())
            if self.inpForm == 'MAC':
                paraFile = os.path.join(self.pathHapDir,"parametersMAC")
            elif self.inpForm == 'GLSC':
                paraFile = os.path.join(self.pathHapDir,"parametersGLSC")
            f = open(paraFile, 'r')
            #open and display HTF file
            for line in f:
                row = line.split('=')
                if (row[0] == 'FILENAME_HAPLOTYPEFREQUENCIES'): # htf file
                    pathHTF = os.path.join("..", str(row[1]).strip())
                elif(row[0] == 'FILENAME_EPSILON_LOGL'): #Epsilon file
                    pathEpsilon = os.path.join("..", str(row[1]).strip())
                else:
                    continue
            fHTF = open(pathHTF, 'r')
            self.htfnr = 0
            for line in fHTF:
                if (self.htfnr < maxLine):
                    raw = line.strip()
                    self.labTopHTF.append(raw)
                self.htfnr += 1
            fHTF.close()
                    
            # plot1 - htf
            self.plot1.clear()
            freqList = []
            nameList = []
            indexList = []
            tempFile = open('tempHTF.txt', 'w')
            txt = self.labTopHTF.toPlainText()
            tempFile.write(txt)
            tempFile.close()
            t = open('tempHTF.txt', 'r')
            linr = 0
            for line in t:
                if (linr < maxLine):
                    sp = line.split('\t')
                    freq = sp[1].strip()
                    freqList.append(freq)
                    nameList.append(sp[0])
                    indexList.append(linr + 1)
                linr += 1
            freqListN = np.asarray(freqList).astype(np.float32)
            xra = np.arange(1, len(freqListN)+1)
            self.plot1.plot(x=xra, y=freqListN, pen=None, symbolBrush=(255,0,0), symbolPen='w', symbolSize=6)
            vb1 = self.plot1.getPlotItem()
            vb1.enableAutoRange(axis='x', enable=True)
            vb1.enableAutoRange(axis='y', enable=True)
            
            #open and display Epsilon file
            epsList = []
            self.plot2.clear()
            fEps = open(pathEpsilon, 'r')
            for line in fEps:
                raw = line.strip()
                sp = raw.split('\t')
                epsList.append(sp[0])
            fEps.close()
            zEps = len(epsList)
            xrae = np.arange(1, zEps+1)
            # plot2
            epsListN = np.asarray(epsList).astype(np.float32)
            self.plot2.plot(x=xrae, y=epsListN, symbol='+', symbolBrush=(255,0,0), symbolPen='w', symbolSize=5)
            vb2 = self.plot2.getPlotItem()
            vb2.enableAutoRange(axis='x', enable=True)
            vb2.enableAutoRange(axis='y', enable=True)
            t.close()       #Win special [05.10.2020]
            os.remove("tempHTF.txt")
            
    def display_Epsilon(self):
        """induces the real time display of epsilon of the running Hapl-o-Mat
        """
        if (self.signalBusy != 0):
            if platform.system() == "Windows":
                os.chdir(self.currDir_US)       #Win special [05.10.2020]
            epsList = []
            self.plot2.clear()
            if self.inpForm == 'MAC':
                paraFile = os.path.join(self.pathHapDir,"parametersMAC")
            elif self.inpForm == 'GLSC':
                paraFile = os.path.join(self.pathHapDir,"parametersGLSC")
            f = open(paraFile, 'r')
            #htf file
            for line in f:
                row = line.split('=')
                if(row[0] == 'FILENAME_EPSILON_LOGL'): #Epsilon file
                    pathEpsilon = os.path.join("..", str(row[1]).strip())
                else:
                    continue        
            if(os.path.isfile(pathEpsilon)):
                fEps = open(pathEpsilon, 'r')
                for line in fEps:
                    raw = line.strip()
                    sp = raw.split('\t')
                    epsList.append(sp[0])
                fEps.close()
                zEps = len(epsList)
                xrae = np.arange(1, zEps+1)
                # plot2
                epsListN = np.asarray(epsList).astype(np.float32)
                self.plot2.plot(x=xrae, y=epsListN, symbol='+', symbolBrush=(255,0,0), symbolPen='w', symbolSize=5)
                vb2 = self.plot2.getPlotItem()
                vb2.enableAutoRange(axis='x', enable=True)
                vb2.enableAutoRange(axis='y', enable=True)

    def display_All(self):
        """induces display of all htf
        """
        if (self.signalBusy == 2):
            self.textEdit_TopX.setText(str(self.htfnr))
            self.display_Results()

    def display_Eps(self):
        """induces display of ht with htf >= epsilon
        """
        if (self.signalBusy == 2):
            self.textEdit_TopX.setText(str(self.epsNr))
            self.display_Results()
        
    def display_Cum(self):
        """induces display of ht with cululated sum <= given percentage
        """
        if (self.signalBusy == 2):
            cumFreq = float(self.textEdit_Cum.text())
            for i in self.cumList:
                cc = float(i)
                hit = 0
                if (cc > cumFreq):
                    cumNr = self.cumList.index(cc)
                    hit = 1
                    break  
            if (hit == 0):
                cumNr = len(self.cumList)
            self.textEdit_TopX.setText(str(cumNr))
            self.display_Results()


# make QSplitter handle visible            
class Handle(QWidget):
    def paintEvent(self, e=None):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.Dense6Pattern)
        painter.drawRect(self.rect())

class customSplitterHorizontal(QSplitter):
    def addWidget(self, wdg):
        super().addWidget(wdg)
        self.width = self.handleWidth()
        l_handle = Handle()
        l_handle.setMaximumSize(self.width*2, self.width*8)
        layout = QHBoxLayout(self.handle(self.count()-1))
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(l_handle)
        
class customSplitterVertical(QSplitter):
    def addWidget(self, wdg):
        super().addWidget(wdg)
        self.width = self.handleWidth()
        l_handle = Handle()
        l_handle.setMaximumSize(self.width*10, self.width*2)
        layout = QHBoxLayout(self.handle(self.count()-1))
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(l_handle)
        
######################################
# Class Test

class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window")
        layout.addWidget(self.label)
        self.setLayout(layout)

###################################################################
# main

# #fbs app special
# if __name__ == '__main__':

    # os.environ["QT_LOGGING_RULES"] = "*.debug=false"
    # appctxt = AppContext()                      # 4. Instantiate the subclass
    # exit_code = appctxt.run()                   # 5. Invoke run()
    # sys.exit(exit_code)  

if __name__ == '__main__':

    import sys
    os.environ["QT_LOGGING_RULES"] = "*.debug=false" #Win special [05.10.2020]
    app = QApplication([])
    ex = MainW()
    #ex.show() 
    sys.exit(app.exec_())
    