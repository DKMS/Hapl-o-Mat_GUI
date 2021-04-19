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

GUI_SetParameters.py
Widget for run parameter settings

@author: Ute Solloch
'''

# # fbs app special
# from fbs_runtime.application_context.PyQt5 import ApplicationContext

# import modules:
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtCore import pyqtSignal
import os, platform
import sys
import shutil
import re

# import own modules
import GUI_Resolution, GUI_miscFeatures


class Parameters(QWidget):
    """Parameter window
    """
    strParaSet = pyqtSignal(str)

    def __init__(self, listLociBD, dirHap):
        """constructor
        """
        super(Parameters, self).__init__()
        
        self.listLociBD = listLociBD
        self.dirHap = dirHap
        
        self.initUI()
        
    def closeEvent(self, event):
        try: self.resW
        except:
            pass
        else:
            self.resW.close()   
        event.accept()
        
    def initUI(self):
        """define the GUI
        """   
      
        # stylesheet and platform
        # # fbs app special
        # appctxt = ApplicationContext()
        if platform.system() == "Windows":
            # # fbs app special
            self.setStyleSheet(open("styleWin.qss", "r").read())
            # stylesheet = appctxt.get_resource('styleWin.qss')
            # appctxt.app.setStyleSheet(open(stylesheet).read()) 
        elif platform.system() == "Linux":
            # # fbs app special
            self.setStyleSheet(open("styleLinux.qss", "r").read())
            # stylesheet = appctxt.get_resource('styleLinux.qss')
            # appctxt.app.setStyleSheet(open(stylesheet).read())    
        
        global dictLoci
        dictLoci = {}
        self.listLoci = []
        self.dictRes = {}
        self.path = ''
        self.countDon = 0
        self.pathHapDir = os.path.relpath(self.dirHap, start=os.curdir)
        self.path_ResDir = ''
        self.path_InpFile = ''
        
        #positioning
        # self.center()
       
        # GUIsrc working directory      
        self.dirParent = os.getcwd()
        self.pathParaDefault = str(os.path.join(self.dirParent, "parametersDefault"))
        
        # RunID default
        self.runID = "RunX"
        
        # combo choices
        list_ini = ["equal", "numberOccurrence","perturbation", "random"]
        list_bool = ["false", "true"]
        
        # Read default parameters 
        self.dictPara = {}
        if(os.path.isfile(self.pathParaDefault)):
            # read parameters
            fi = open(self.pathParaDefault, 'r')
            for line in fi:
                line = line.rstrip('\r\n')
                listLine = line.split('=')
                if (len(listLine)>1):
                    self.dictPara[listLine[0]]= listLine[1] 
        else:
            QMessageBox.about(self, "Caution: No default parameter file found!","\n")                        
        
        #file names (as available in default parameters)      
        if 'FILENAME_HAPLOTYPEFREQUENCIES' in self.dictPara.keys(): 
            filename_htf = self.dictPara['FILENAME_HAPLOTYPEFREQUENCIES']
            fileSplit = os.path.split(filename_htf)
            # savePath parameters
            self.path_ResDir = fileSplit[0]
            path1, filename1 = os.path.split(self.path)
            if "_" in fileSplit[1]:
                self.runID = fileSplit[1].split('_')[0]
                self.runIdIn = self.runID + "_"
                filename2 = self.runID + "_" + filename1
            else:
                self.runID = ""
                self.runIdIn = self.runID
                filename2 = filename1               
            filename_parameters = os.path.join(self.path_ResDir, filename2)
            textSave = ""
        else:
            filename_htf = ""
            textSave = ""
        if 'FILENAME_INPUT' in self.dictPara.keys(): 
            self.path_InpFile = self.dictPara['FILENAME_INPUT']
            self.processInputDefault()
            # set recommendation Epsilon 1/2*self.countDon
            self.epsilonRec = 1/(2*self.countDon)
            self.textCut = "1/(2n) = {0:1.2g}".format(self.epsilonRec)            
        else:
            self.path_InpFile = ""
            self.textCut = ""
        if 'FILENAME_HAPLOTYPES' in self.dictPara.keys(): 
            filename_haplotypes = self.dictPara['FILENAME_HAPLOTYPES']            
        else:
            filename_haplotypes = ""
        if 'FILENAME_GENOTYPES' in self.dictPara.keys(): 
            filename_genotypes = self.dictPara['FILENAME_GENOTYPES']
        else:
            filename_genotypes = ""
        if 'FILENAME_EPSILON_LOGL' in self.dictPara.keys(): 
            filename_epsLog = self.dictPara['FILENAME_EPSILON_LOGL']
        else:
            filename_epsLog = ""
        
        min_freq_genos = self.dictPara['MINIMAL_FREQUENCY_GENOTYPES']
        doAmb = self.dictPara['DO_AMBIGUITYFILTER']
        expLinesAmb = self.dictPara['EXPAND_LINES_AMBIGUITYFILTER']
        iniHTF = self.dictPara['INITIALIZATION_HAPLOTYPEFREQUENCIES']
        epsilon = self.dictPara['EPSILON']
        cut_htf = self.dictPara['CUT_HAPLOTYPEFREQUENCIES']
        renormHTF = self.dictPara['RENORMALIZE_HAPLOTYPEFREQUENCIES']
        seed = self.dictPara['SEED'] 
        genoPrint = self.dictPara['WRITE_GENOTYPES']
        
        # Initialize self.dictRes
        if 'LOCI_AND_RESOLUTIONS' in self.dictPara.keys(): 
            locAndRes0 = self.dictPara['LOCI_AND_RESOLUTIONS']
            locAndRes = locAndRes0.replace('2d','1f').replace('4d','2f').replace('6d','3f').replace('8d','4f')
            resList = locAndRes.split(',')
            self.dictRes = {}
            for i in resList:
                duo = i.split(':')
                resF = duo[1].replace("f", "field")
                self.dictRes[duo[0]] = resF
            for i in self.listLoci:
                if (i not in self.dictRes):
                    self.dictRes[i] = 'ignore locus'
        else:
            #default
            locAndRes=''
            for i in self.listLoci:
                self.dictRes[i] = 'null'
        
        # Window layout
        # self.layout = QGridLayout()
        self.setWindowTitle('Set or Load Parameters')
        # self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        layoutAll = QVBoxLayout()
        
        hbox1 = QHBoxLayout()
        btnLoadPara_tab1 =QPushButton('Load Parameters')
        hbox1.addStretch(1)
        hbox1.addWidget(btnLoadPara_tab1)        
        layoutAll.addLayout(hbox1)
        
        setFrame = QGroupBox('Set or change parameters')
        layoutFrame = QVBoxLayout()
        
        ## Top1
        labNull= QLabel()
        labInp = QLabel("# Input genotypes")
        labInp.setStyleSheet("QLabel { font: bold }")
        labInput_tab1 = QLabel("FILENAME_INPUT") 
        self.textEdit_Input_tab1 = QLabel(self.path_InpFile)
        self.textEdit_Input_tab1.setFrameShape(QFrame.Panel)
        self.textEdit_Input_tab1.setStyleSheet(GUI_miscFeatures.label_style_white)
        self.textEdit_Input_tab1.setMinimumSize(70,15)
        btnInpChoice_tab1 = QPushButton('...')
        labOut = QLabel("# Result files")
        labOut.setStyleSheet("QLabel { font: bold }")
        labRes_tab1 = QLabel("FOLDER_RESULTS")  
        self.textEdit_FoldRes_tab1 = QLabel(self.path_ResDir)
        self.textEdit_FoldRes_tab1.setFrameShape(QFrame.Panel)
        self.textEdit_FoldRes_tab1.setStyleSheet(GUI_miscFeatures.label_style_white)
        self.textEdit_FoldRes_tab1.setMinimumSize(70,15)
        btnResChoice_tab1 = QPushButton('...')
        labResHap_tab1 = QLabel("FILENAME_HAPLOTYPES") 
        self.textEdit_ResHap_tab1 = QLabel(filename_haplotypes)
        self.textEdit_ResHap_tab1.setStyleSheet(GUI_miscFeatures.label_style_inactive)
        labResGen_tab1 = QLabel("FILENAME_GENOTYPES") 
        self.textEdit_ResGen_tab1 = QLabel(filename_genotypes)
        self.textEdit_ResGen_tab1.setStyleSheet(GUI_miscFeatures.label_style_inactive)
        labResHTF_tab1 = QLabel("FILENAME_HAPLOTYPEFREQUENCIES") 
        self.textEdit_ResHTF_tab1 = QLabel(filename_htf)
        self.textEdit_ResHTF_tab1.setStyleSheet(GUI_miscFeatures.label_style_inactive)
        labResEps_tab1 = QLabel("FILENAME_EPSILON_LOGL") 
        self.textEdit_ResEps_tab1 = QLabel(filename_epsLog)
        self.textEdit_ResEps_tab1.setStyleSheet(GUI_miscFeatures.label_style_inactive)
        labRunId_tab1 = QLabel("RunID")
        self.textEdit_RunId_tab1 = QLineEdit(self.runID)
        
        tab1layout = QGridLayout()
        tab1layout.addWidget(labNull, 0,1)
        tab1layout.addWidget(labInp, 1,1)
        tab1layout.addWidget(self.textEdit_Input_tab1, 2,1)
        tab1layout.addWidget(labInput_tab1, 2,2,1,1)
        tab1layout.addWidget(btnInpChoice_tab1, 2,3)    
        tab1layout.addWidget(labOut, 3,1)
        tab1layout.addWidget(self.textEdit_FoldRes_tab1, 4,1)
        tab1layout.addWidget(labRes_tab1, 4,2,1,1)
        tab1layout.addWidget(btnResChoice_tab1, 4,3)
        tab1layout.addWidget(self.textEdit_RunId_tab1, 5,1)
        tab1layout.addWidget(labRunId_tab1, 5,2)
        tab1layout.addWidget(self.textEdit_ResHap_tab1, 6,1)
        tab1layout.addWidget(labResHap_tab1, 6,2)
        tab1layout.addWidget(self.textEdit_ResGen_tab1, 7,1)
        tab1layout.addWidget(labResGen_tab1, 7,2)
        tab1layout.addWidget(self.textEdit_ResHTF_tab1, 8,1)
        tab1layout.addWidget(labResHTF_tab1, 8,2)
        tab1layout.addWidget(self.textEdit_ResEps_tab1, 9,1)
        tab1layout.addWidget(labResEps_tab1, 9,2)        
        tab1layout.addWidget(labNull, 10,1)
        
        ## Top2
        lab_Top2_tab1 = QLabel("# Reports")
        lab_Top2_tab1.setStyleSheet("QLabel { font: bold }")
        labResolution_tab1 = QLabel("LOCI AND RESOLUTIONS") 
        self.textEdit_Resolution_tab1 = QLabel(locAndRes)
        self.textEdit_Resolution_tab1.setStyleSheet(GUI_miscFeatures.label_style_inactive)
        btnResolutionMAC =QPushButton('...')
        labMinFreq_tab1 = QLabel("MINIMAL FREQUENCY GENOTYPES") 
        self.textEdit_MinFreq_tab1 = QLineEdit(min_freq_genos)
        labAmbi_tab1 = QLabel("DO AMBIGUITYFILTER") 
        self.combo_Amb_tab1 = QComboBox()
        self.combo_Amb_tab1.addItems(list_bool)
        index = self.combo_Amb_tab1.findText(doAmb)
        self.combo_Amb_tab1.setCurrentIndex(index)
        labExpLines_tab1 = QLabel("EXPAND LINES AMBIGUITYFILTER") 
        self.combo_ExpLines_tab1 = QComboBox()
        self.combo_ExpLines_tab1.addItems(list_bool)
        index = self.combo_ExpLines_tab1.findText(expLinesAmb)
        self.combo_ExpLines_tab1.setCurrentIndex(index)        
        labWriteGeno_tab1 = QLabel("WRITE_GENOTYPES") 
        self.combo_WriteGeno_tab1 = QComboBox()
        self.combo_WriteGeno_tab1.addItems(list_bool)
        index = self.combo_WriteGeno_tab1.findText(genoPrint)
        self.combo_WriteGeno_tab1.setCurrentIndex(index)
        
        hbox2 = QHBoxLayout()    
        tab2layout = QGridLayout()
        tab2layout.addWidget(lab_Top2_tab1, 1,1)
        hboxRes = QHBoxLayout()
        hboxRes.addWidget(btnResolutionMAC)
        hboxRes.addStretch(1)
        tab2layout.addLayout(hboxRes,2,1)     
        tab2layout.addWidget(labResolution_tab1, 2,2)        
        tab2layout.addWidget(self.textEdit_Resolution_tab1, 3,1, 1,2)
        tab2layout.addWidget(self.textEdit_MinFreq_tab1, 4 ,1)
        tab2layout.addWidget(labMinFreq_tab1, 4,2)
        tab2layout.addWidget(self.combo_Amb_tab1, 5,1)
        tab2layout.addWidget(labAmbi_tab1, 5,2)
        tab2layout.addWidget(self.combo_ExpLines_tab1, 6,1)
        tab2layout.addWidget(labExpLines_tab1, 6,2)  
        tab2layout.addWidget(self.combo_WriteGeno_tab1, 7,1)
        tab2layout.addWidget(labWriteGeno_tab1, 7,2)        
        # tab2layout.addWidget(labNull, 7,1)
        
        ## Top3
        lab_Top3_tab1 = QLabel("# EM algorithm")
        lab_Top3_tab1.setStyleSheet("QLabel { font: bold }")
        labIni_tab1 = QLabel("INITIALIZATION HAPLOTYPE FREQUENCIES") 
        self.combo_Ini_tab1 = QComboBox()
        self.combo_Ini_tab1.addItems(list_ini)
        index = self.combo_Ini_tab1.findText(iniHTF)
        self.combo_Ini_tab1.setCurrentIndex(index)
        labEpsilon_tab1 = QLabel("EPSILON") 
        self.textEdit_Epsilon_tab1 = QLineEdit(epsilon)
        self.textEdit_CutRec_tab1 = QLabel()
        self.textEdit_CutRec_tab1.setStyleSheet(GUI_miscFeatures.label_style_info)
        self.textEdit_CutRec_tab1.setText(self.textCut)
        labCut_tab1 = QLabel("CUT HAPLOTYPE FREQUENCIES") 
        self.textEdit_Cut_tab1 = QLineEdit(cut_htf)
        labNorm_tab1 = QLabel("RENORMALIZE HAPLOTYPE FREQUENCIES") 
        self.combo_Norm_tab1 = QComboBox()        
        self.combo_Norm_tab1.addItems(list_bool)
        index = self.combo_Norm_tab1.findText(renormHTF)
        self.combo_Norm_tab1.setCurrentIndex(index)
        labSeed_tab1 = QLabel("SEED") 
        self.textEdit_Seed_tab1 = QLineEdit(seed)        
        
        tab3layout = QGridLayout()
        tab3layout.addWidget(lab_Top3_tab1, 1,1)
        tab3layout.addWidget(self.combo_Ini_tab1, 2,1)
        tab3layout.addWidget(labIni_tab1, 2,2)
        tab3layout.addWidget(self.textEdit_Epsilon_tab1, 3,1)
        tab3layout.addWidget(labEpsilon_tab1, 3,2)        
        tab3layout.addWidget(self.textEdit_Cut_tab1, 4,1)
        tab3layout.addWidget(labCut_tab1, 4,2)
        tab3layout.addWidget(self.textEdit_CutRec_tab1, 4, 3)
        tab3layout.addWidget(self.combo_Norm_tab1, 5,1)
        tab3layout.addWidget(labNorm_tab1, 5,2)
        tab3layout.addWidget(self.textEdit_Seed_tab1, 6,1)
        tab3layout.addWidget(labSeed_tab1, 6,2)
        tab3layout.addWidget(labNull, 7,1)
        
        SepFrameH = QFrame()
        SepFrameH.setFrameShape(QFrame.HLine)
        SepFrameH.setStyleSheet("border: 1px solid #ababab;")
        SepFrameV = QFrame()
        SepFrameV.setFrameShape(QFrame.VLine)
        SepFrameV.setStyleSheet("border: 1px solid #ababab;")
        
        layoutFrame.addLayout(tab1layout)
        layoutFrame.addWidget(SepFrameH)
        hbox2.addLayout(tab2layout)
        hbox2.addWidget(SepFrameV)
        hbox2.addLayout(tab3layout)
        layoutFrame.addLayout(hbox2)
        
        setFrame.setLayout(layoutFrame)
        layoutAll.addWidget(setFrame)
         
        # Save line
        hbox2 = QHBoxLayout()
        self.lab_Save_tab1 = QLabel()
        self.lab_Save_tab1.setStyleSheet(GUI_miscFeatures.label_style_info)
        self.lab_Save_tab1.setText(textSave)
        btnParametersMAC = QPushButton("Proceed")
        btnCancel = QPushButton('Cancel')
        btnCancel.setStyleSheet(GUI_miscFeatures.button_style_cancel)
        hbox2.addWidget(self.lab_Save_tab1)
        hbox2.addStretch(1)
        hbox2.addWidget(btnCancel)
        hbox2.addWidget(btnParametersMAC)
        layoutAll.addLayout(hbox2)

        self.setLayout(layoutAll)
        
        # TextEdit validation        
        self.textEdit_Cut_tab1.editingFinished.connect(self.validate_input_cut)
        self.textEdit_Seed_tab1.editingFinished.connect(self.validate_input_seed)
        self.textEdit_MinFreq_tab1.editingFinished.connect(self.validate_input_MinFreq)
        self.textEdit_Epsilon_tab1.editingFinished.connect(self.validate_input_Eps)
        self.textEdit_RunId_tab1.editingFinished.connect(self.validate_input_RunID)        
        
        ## ButtonActions
        btnInpChoice_tab1.clicked.connect(self.browse_files_input)
        btnResChoice_tab1.clicked.connect(self.browse_folder_results)
        btnLoadPara_tab1.clicked.connect(self.loadParameters)    # load parameter file
        btnResolutionMAC.clicked.connect(self.chooseResolution) # choice of resolution
        self.textEdit_RunId_tab1.textChanged.connect(self.refreshFiles) #changed runID
        btnParametersMAC.clicked.connect(self.saveAsTest)  #save parameters  
        btnCancel.clicked.connect(self.close)

        self.show()


####################################        
# Functions

    def center(self):
        """moves window to screen center
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())   
     
    def underConstruction(self):
        """opens 'under construction' dialog
        """
        self.constructionAlert = GUI_miscFeatures.UnderConstruction()
        
    def get_Loci(self):
        """reads gene loci from input file and tests availability in current IPD-IMGT/HLA data
        """
        dictLoci = {}
        self.countDon = 0
        self.listLoci = []
        fi = open(self.path_InpFile, 'r')
        for i, line in enumerate(fi):
            if i == 0:
                line = line.rstrip('\r\n')
                listLine1 = line.split('\t')
                el = len(listLine1)
                if self.inputForm == 'MAC':
                    for k in range (1, el):
                        dictLoci[listLine1[k]] = 1
                elif self.inputForm == 'GLSC':
                    for k in range (1, el):
                        loc = listLine1[k].split('*',1)[0]
                        dictLoci[loc] = 1
            elif i>0:
                self.countDon+=1
        fi.close()
        for key,val in dictLoci.items():
            self.listLoci.append(key)
        self.listLoci.sort()
        
        # Update self.dictRes
        for key in self.dictRes.keys():
            if (key not in self.dictRes):
                del self.dictRes[key]
        for i in self.listLoci:
            if (i not in self.dictRes):
                self.dictRes[i] = 'null'
                
        # Test if all loci valid
        listMiss = []
        self.listLociValid = []
        sch = 0
        for i in self.listLoci:
            if (i not in self.listLociBD):
                listMiss.append(i)
                sch = 1
            else:
                self.listLociValid.append(i)
                
        if (len(listMiss) != 0):
            # join
            if (len(listMiss) == 1):
                locMissStr = ", ".join(listMiss)
            elif (len(listMiss) == 2):
                locMissStr = " and ".join(listMiss)
            else:
                last = listMiss[-1]
                rem = listMiss[:-1]
                locMissStrInt = ", ".join(rem)
                locMissStr = locMissStrInt + ", and " + last
            msgInvalidLoc = QMessageBox()
            msgInvalidLoc.setIcon(QMessageBox.Warning)
            msgInvalidLoc.setWindowTitle("Warning")
            msgInvalidLoc.setText("Input file: Invalid locus/loci.")
            msgInvalidLoc.setInformativeText("For Loci\n" + locMissStr + "\nno allele information is available in the current IPD-IMGT/HLA data. These loci will be ignored in the haplotype frequency estimation.")
            msgInvalidLoc.setStandardButtons(QMessageBox.Ok)
            msgInvalidLoc.exec_()
                
        
    def browse_folder_results(self):
        """opens file dialog for choice of the results folder
        """
        read = os.path.join("..", self.textEdit_FoldRes_tab1.text())
        if (not read == ''):
            self.path_ResDir = QFileDialog.getExistingDirectory(self, "Pick a folder", read)
        else:
            self.path_ResDir = QFileDialog.getExistingDirectory(self, "Pick a folder")
        if self.path_ResDir != "":
            self.path_ResDir = os.path.normpath(self.path_ResDir)
            self.textEdit_FoldRes_tab1.setText(self.path_ResDir)
            self.refreshFiles()        
    
    def browse_files_input(self):
        """opens file dialog for choice of the input file
        """
        read = os.path.join("..", self.textEdit_Input_tab1.text())
        self.textEdit_Resolution_tab1.clear()
        if (not read == ''):        
            self.path_InpFile,_ = QFileDialog.getOpenFileName(self, 'Pick input file', read)
        else:
            self.path_InpFile,_ = QFileDialog.getOpenFileName(self, 'Pick input file', '.')
        if self.path_InpFile != "":
            self.path_InpFile = os.path.normpath(self.path_InpFile)
            self.textEdit_Input_tab1.setText(str(self.path_InpFile))
        self.processInput()
    
    def processInputDefault(self):
        """identifies input file format and input loci
        """
        # MAC or GLSC?
        try:
            with open(self.path_InpFile) as f:
                if '*' in f.read(): # identification of input format
    
                    self.inputForm = 'GLSC'
                    self.path = os.path.join(self.pathHapDir, "parametersGLSC")
                else:
                    self.inputForm = 'MAC'
                    self.path = os.path.join(self.pathHapDir, "parametersMAC")
            self.listLoci.clear()
            self.get_Loci()
            # set recommendation Epsilon 1/2*self.countDon
            self.epsilonRec = 1/(2*self.countDon)
            self.textCut = "1/(2n) = {0:1.2g}".format(self.epsilonRec)
        except:
            msgInvalidPara = QMessageBox()
            msgInvalidPara.setIcon(QMessageBox.Warning)
            msgInvalidPara.setWindowTitle("Warning")
            msgInvalidPara.setText("Input path or file not found.")
            msgInvalidPara.setInformativeText("Please select a valid parameter file or set parameters via input mask.")
            msgInvalidPara.setStandardButtons(QMessageBox.Ok)
            msgInvalidPara.exec_()
        
    def processInput(self):
        """identifies input file format, input loci, and calculates maximum epsilon value
        triggers refreshFiles()
        """
        try:
            # MAC or GLSC?
            with open(self.path_InpFile) as f:
                if '*' in f.read(): # identification of input format
                    self.inputForm = 'GLSC'
                    self.path = os.path.join(self.pathHapDir, "parametersGLSC")
                else:
                    self.inputForm = 'MAC'
                    self.path = os.path.join(self.pathHapDir, "parametersMAC")            
            self.listLoci.clear()
            self.get_Loci()
            # set recommendation Epsilon 1/2*self.countDon
            self.epsilonRec = 1/(2*self.countDon)
            self.textCut = "1/(2n) = {0:1.2g}".format(self.epsilonRec)
            self.textEdit_CutRec_tab1.setText(self.textCut)
            self.refreshFiles() 
        except FileNotFoundError:            
            # QMessageBox.about(self, 'Input File:','Please choose path to valid input file.')
            pass    
             
    
    def refreshFiles(self):
        """reads runID and triggers setFilenames()
        """
        self.runID = self.textEdit_RunId_tab1.text()
        self.setFilenames()
        
    def setFilenames(self):
        """refreshes filenames with current runID and results folder
        """
        global filename_haplotypes
        global filename_genotypes
        global filename_htf
        global filename_epsLog
        global filename_parameters
        if (self.runID != ""):
            self.runIdIn = self.runID + "_"
        else:
            self.runIdIn = self.runID
        filename_haplotypes = os.path.normpath(os.path.join(self.path_ResDir, self.runIdIn + 'haplotypes.dat'))
        filename_genotypes = os.path.normpath(os.path.join(self.path_ResDir, self.runIdIn + 'genotypes.dat'))
        filename_htf = os.path.normpath(os.path.join(self.path_ResDir, self.runIdIn + 'htf.dat'))
        filename_epsLog = os.path.normpath(os.path.join(self.path_ResDir, self.runIdIn + 'epsilon.dat'))
        path1, filename1 = os.path.split(self.path)
        filename2 = self.runIdIn + filename1
        filename_parameters = os.path.normpath(os.path.join("..", self.path_ResDir, filename2))
        textSave = "Parameters will be saved as:\n" + filename_parameters

        self.textEdit_ResHap_tab1.setText(filename_haplotypes)
        self.textEdit_ResGen_tab1.setText(filename_genotypes)
        self.textEdit_ResHTF_tab1.setText(filename_htf)
        self.textEdit_ResEps_tab1.setText(filename_epsLog)
        self.lab_Save_tab1.setText(textSave)
        
    def chooseResolution(self):
        """opens window for choice of loci resolution
        """
        inpRead = self.textEdit_Input_tab1.text()
        if (inpRead == ''):
            msgFileIn = QMessageBox()
            msgFileIn.setIcon(QMessageBox.Warning)
            msgFileIn.setWindowTitle("Incomplete entries.")
            msgFileIn.setText("Please choose genotype input file.")
            msgFileIn.setStandardButtons(QMessageBox.Ok)
            msgFileIn.exec_()
        else:
            self.resW = GUI_Resolution.Resolution(self.listLociValid, self.dictRes)
            self.resW.setWindowTitle('Locus resolution')
            self.resW.strRes.connect(self.printResolution)        
            self.resW.show()
        
    def printResolution(self, strRes):
        """processes signal from resolution choice window
        """
        strResF = strRes.replace("field", "f")
        self.textEdit_Resolution_tab1.setText(strResF)
        # update self.dictRes
        dictInterim = {}
        arrRes = strRes.split(',')
        for i in arrRes:
            arri = i.split(':')
            dictInterim[str(arri[0])]=arri[1]
        for key in self.dictRes:
            if key in dictInterim:
                val = dictInterim[key]
                self.dictRes[key] = val
            else:
                self.dictRes[key] = 'ignore locus'
        
    def loadParameters(self):
        """triggered by button 'btnLoadPara_tab1'; opens file dialog for the choice of existing parameter file,
        reads parameter file and fills settings in SetParameters mask
        """
        self.listLoci.clear()
        LoadP,_ = QFileDialog.getOpenFileName(self, 'Pick parameter file', '..')
        relDirLoadP = os.path.relpath(LoadP, start=os.curdir)
        # Read default parameters in dictPara
        self.dictPara = {}
        try:
            fi = open(relDirLoadP, 'r')
            for line in fi:
                line = line.rstrip('\r\n')
                listLine = line.split('=')
                if (len(listLine)>1):
                    self.dictPara[listLine[0]]= listLine[1]
        except:
            msgInvalidPara = QMessageBox()
            msgInvalidPara.setIcon(QMessageBox.Warning)
            msgInvalidPara.setWindowTitle("Warning")
            msgInvalidPara.setText("Invalid parameter file.")
            msgInvalidPara.setStandardButtons(QMessageBox.Ok)
            msgInvalidPara.exec_()
        else:                
            arr_indexes = ['FILENAME_HAPLOTYPEFREQUENCIES', 'FILENAME_INPUT', 'FILENAME_HAPLOTYPES', 'FILENAME_GENOTYPES',
                           'FILENAME_EPSILON_LOGL', 'MINIMAL_FREQUENCY_GENOTYPES', 'DO_AMBIGUITYFILTER',
                           'EXPAND_LINES_AMBIGUITYFILTER', 'WRITE_GENOTYPES', 'INITIALIZATION_HAPLOTYPEFREQUENCIES', 'EPSILON',
                           'CUT_HAPLOTYPEFREQUENCIES', 'RENORMALIZE_HAPLOTYPEFREQUENCIES', 'SEED', 'LOCI_AND_RESOLUTIONS']
           
            try:      # all keys defined?
                for i in arr_indexes:
                    t = self.dictPara[i]
            except KeyError:
                msgInvalidPara = QMessageBox()
                msgInvalidPara.setIcon(QMessageBox.Warning)
                msgInvalidPara.setWindowTitle("Warning")
                msgInvalidPara.setText("Parameter file not valid.")
                msgInvalidPara.setInformativeText("One or more of the mandatory entries are missing. Please select a valid parameter file or set parameters via input mask.")
                msgInvalidPara.setStandardButtons(QMessageBox.Ok)
                msgInvalidPara.exec_()
            else:   
                #file names  
                filename_htf = self.dictPara['FILENAME_HAPLOTYPEFREQUENCIES']
                fileSplit = os.path.split(filename_htf)
                if "_" in fileSplit[1]:
                    self.runID = fileSplit[1].split('_')[0]
                else:
                    self.runID = ""
                self.path_ResDir = fileSplit[0]
                
                self.path_InpFile = self.dictPara['FILENAME_INPUT']
                self.processInputDefault()
                self.textEdit_CutRec_tab1.setText(self.textCut)
                
                filename_haplotypes = self.dictPara['FILENAME_HAPLOTYPES']
                filename_genotypes = self.dictPara['FILENAME_GENOTYPES']
                filename_epsLog = self.dictPara['FILENAME_EPSILON_LOGL']
                min_freq_genos = self.dictPara['MINIMAL_FREQUENCY_GENOTYPES']
                doAmb = self.dictPara['DO_AMBIGUITYFILTER']
                expLinesAmb = self.dictPara['EXPAND_LINES_AMBIGUITYFILTER']
                genoPrint = self.dictPara['WRITE_GENOTYPES']
                iniHTF = self.dictPara['INITIALIZATION_HAPLOTYPEFREQUENCIES']
                epsilon = self.dictPara['EPSILON']
                cut_htf = self.dictPara['CUT_HAPLOTYPEFREQUENCIES']
                renormHTF = self.dictPara['RENORMALIZE_HAPLOTYPEFREQUENCIES']
                seed = self.dictPara['SEED']
                locAndRes0 = self.dictPara['LOCI_AND_RESOLUTIONS']
                locAndRes = locAndRes0.replace('2d','1f').replace('4d','2f').replace('6d','3f').replace('8d','4f')
                
                # write settings to parameter mask
                self.textEdit_FoldRes_tab1.setText(self.path_ResDir)
                self.textEdit_Input_tab1.setText(self.path_InpFile)
                self.textEdit_ResHap_tab1.setText(filename_haplotypes)
                self.textEdit_ResGen_tab1.setText(filename_genotypes)
                self.textEdit_ResHTF_tab1.setText(filename_htf)
                self.textEdit_ResEps_tab1.setText(filename_epsLog)
                self.textEdit_RunId_tab1.setText(self.runID)
                self.textEdit_Resolution_tab1.setText(locAndRes)
                self.textEdit_MinFreq_tab1.setText(min_freq_genos)
                index = self.combo_Amb_tab1.findText(doAmb)
                self.combo_Amb_tab1.setCurrentIndex(index)
                index = self.combo_ExpLines_tab1.findText(expLinesAmb)
                self.combo_ExpLines_tab1.setCurrentIndex(index)                
                index = self.combo_WriteGeno_tab1.findText(genoPrint)
                self.combo_WriteGeno_tab1.setCurrentIndex(index)                
                index = self.combo_Ini_tab1.findText(iniHTF)
                self.combo_Ini_tab1.setCurrentIndex(index)
                self.textEdit_Epsilon_tab1.setText(epsilon)
                self.textEdit_Cut_tab1.setText(cut_htf)
                index = self.combo_Norm_tab1.findText(renormHTF)
                self.combo_Norm_tab1.setCurrentIndex(index)
                self.textEdit_Seed_tab1.setText(seed)      
                
                # Initialize self.dictRes
                self.dictRes = {}
                resList = locAndRes.split(',')
                for i in resList:
                    duo = i.split(':')
                    resF = duo[1].replace("f", "field")
                    self.dictRes[duo[0]] = resF
                for i in self.listLoci:
                    if (i not in self.dictRes):
                        self.dictRes[i] = 'ignore locus'
    
    def validate_input_cut(self):
        """tests whether CUT_HAPLOTYPEFREQUENCIES settings are valid and complete
        """
        # tests for validity of parameter entries
        try:
            cut_htf = float(self.textEdit_Cut_tab1.text())
        except ValueError:
            QMessageBox.about(self, 'CUT_HAPLOTYPEFREQUENCIES:','Invalid. Please choose float value between 0 and 1 (e.g. 0.00001 or 1e-5).')
            pass  
            
    def validate_input_MinFreq(self):
        """tests whether MINIMAL_FREQUENCY_GENOTYPES settings are valid and complete
        """
        # tests for validity of parameter entries
        try:
            min_freq_genos = float(self.textEdit_MinFreq_tab1.text())
        except ValueError:
            QMessageBox.about(self, 'MINIMAL_FREQUENCY_GENOTYPES:','Invalid. Please choose float value between 0 and 1 (e.g. 0.00001 or 1e-5).')
            pass  
    
    def validate_input_seed(self):
        """tests whether SEED settings are valid and complete
        """
        # tests for validity of parameter entries
        try:
            seed = int(self.textEdit_Seed_tab1.text())
            if (seed > 1000000000):
                raise ValueError
        except ValueError:
            QMessageBox.about(self, 'SEED:','Invalid seed. Please choose an integer value for SEED between 0 and 1,000,000,000.')
            pass  
    
    def validate_input_Eps(self):
        """tests whether EPSILON settings are valid and complete
        """
        # tests for validity of parameter entries
        try:
            epsilon = float(self.textEdit_Epsilon_tab1.text())
        except ValueError:
            errTxt = "Epsilon value must be <= " + "{0:1.4g}".format(self.epsilonRec) + " (1/(2*n))."
            QMessageBox.about(self, 'EPSILON:','Invalid epsilon. Please choose float value between 0 and 1 (e.g. 0.00001 or 1e-5). \n' + errTxt)
            pass  
    
    def validate_input_RunID(self):
        """tests whether RunID is valid
        """
        # tests for validity of parameter entries
        rID = self.textEdit_RunId_tab1.text()
        if (re.search("[_,\,/,*,?,:,\",<,>,|,%, ]", rID)):
            QMessageBox.about(self, 'Invalid RunID:','RunID must not contain space characters or one of the following characters: _, \, /, *, ?, :, \", <, >, |, or %.')
            return
                        
    def saveAsTest(self):
        """tests whether all settings required to save the parameters are complete, 
        whether result file does not exist under specified name, sends warnings otherwise
        triggers saveAs() when complete
        """
        
        # tests for validity of parameter entries
        
        try:
            with open(self.path_InpFile) as f:
                pass
        except:
            QMessageBox.about(self, 'INVALID INPUT FILE:','Input path or file not found. Please select a valid parameter file or set parameters via input mask.')
            return

        try:
            cut_htf = float(self.textEdit_Cut_tab1.text())
        except ValueError:
            QMessageBox.about(self, 'CUT_HAPLOTYPEFREQUENCIES:','Invalid. Please choose float value between 0 and 1 (e.g. 0.00001 or 1e-5).')
            return
        
        try:
            epsilon = float(self.textEdit_Epsilon_tab1.text())
        except ValueError:
            errTxt = "Epsilon value must be <= " + "{0:1.4g}".format(self.epsilonRec) + " (1/(2*n))."
            QMessageBox.about(self, 'EPSILON:','Invalid epsilon. Please choose float value between 0 and 1 (e.g. 0.00001 or 1e-5). \n' + errTxt)
            return
            
        try:
            min_freq_genos = float(self.textEdit_MinFreq_tab1.text())
        except ValueError:
            QMessageBox.about(self, 'MINIMAL_FREQUENCY_GENOTYPES:','Invalid. Please choose float value between 0 and 1 (e.g. 0.00001 or 1e-5).')
            return
            
        try:
            seed = int(self.textEdit_Seed_tab1.text())
        except ValueError:
            QMessageBox.about(self, 'SEED:','Invalid seed. Please choose an integer value for SEED between 0 and 1,000,000,000.')
            return
            
        rID = self.textEdit_RunId_tab1.text()
        if (re.search("[\,/,*,?,:,\",<,>,|,%, ]", rID)):
            QMessageBox.about(self, 'Invalid RunID:','RunID must not contain space characters or one of the following characters: \, /, *, ?, :, \", <, >, |, or %.')
            return
            
        resRead = self.textEdit_FoldRes_tab1.text()
        inpRead = self.textEdit_Input_tab1.text()
        strRes = self.textEdit_Resolution_tab1.text()
        if ((resRead == '') or (inpRead == '')):
            QMessageBox.about(self, 'Incomplete entries.','Please choose results folder and input file.')
            return
        elif (strRes is ''):
            QMessageBox.about(self, 'Incomplete entries.','Please choose loci resolution.')
            return
        elif (seed > 1000000000):
            QMessageBox.about(self, 'Invalid seed.','Please choose an integer value for SEED between 0 and 1,000,000,000.')
            return
        elif (epsilon > self.epsilonRec):
            msgEps = QMessageBox()
            msgEps.setIcon(QMessageBox.Warning)
            msgEps.setWindowTitle("Invalid epsilon:")
            errTxt = "{0:1.4g}".format(self.epsilonRec)
            msgEps.setText("Please choose epsilon value <= " + errTxt + " (1/(2*n)).")
            msgEps.setStandardButtons(QMessageBox.Ok)
            msgEps.exec_()
            return
            
        path_htf = self.textEdit_ResHTF_tab1.text()
        self.saveAs() 


    def saveAs(self):
        """opens 'save as' file dialog
        triggers createParamFile()
        """
        global dirSave
        path1, filename1 = os.path.split(self.path)
        filename2 = self.runIdIn+filename1
        filename_parameters = str(os.path.join(self.path_ResDir, filename2))
        dirSave,_ = QFileDialog.getSaveFileName(self, 'Save file', filename_parameters)
        self.createParamFile(dirSave)

    def createParamFile(self, dirSave):
        """saves parameter file for Hapl-o-Mat run in default destination and in copy to result folder
        """
        strRes = self.textEdit_Resolution_tab1.text() 
        self.runID = self.textEdit_RunId_tab1.text()
        inpRun = os.path.join("..", self.textEdit_Input_tab1.text())
        resRun = os.path.join("..", self.textEdit_FoldRes_tab1.text())        
        strResChanged = strRes.replace("1f", "2d").replace("2f", "4d").replace("3f", "6d").replace("4f", "8d")
        paraFile = open(self.path, 'w+')
        paraFile.truncate(0)
        paraFile.write('#file name\n')
        paraFile.write('FILENAME_INPUT='+self.textEdit_Input_tab1.text() +'\n')
        paraFile.write('FILENAME_HAPLOTYPES='+ self.textEdit_ResHap_tab1.text() +'\n')
        paraFile.write('FILENAME_GENOTYPES='+ self.textEdit_ResGen_tab1.text() +'\n')
        paraFile.write('FILENAME_HAPLOTYPEFREQUENCIES='+ self.textEdit_ResHTF_tab1.text() +'\n')
        paraFile.write('FILENAME_EPSILON_LOGL='+ self.textEdit_ResEps_tab1.text() +'\n')
        paraFile.write('#reports\n')
        paraFile.write('LOCI_AND_RESOLUTIONS='+ strResChanged +'\n')
        paraFile.write('MINIMAL_FREQUENCY_GENOTYPES='+ self.textEdit_MinFreq_tab1.text() +'\n')
        paraFile.write('DO_AMBIGUITYFILTER='+ self.combo_Amb_tab1.currentText() +'\n')
        paraFile.write('EXPAND_LINES_AMBIGUITYFILTER='+ self.combo_ExpLines_tab1.currentText() +'\n')
        paraFile.write('WRITE_GENOTYPES='+ self.combo_WriteGeno_tab1.currentText() +'\n')
        paraFile.write('#EM-algorithm\n')
        paraFile.write('INITIALIZATION_HAPLOTYPEFREQUENCIES='+ self.combo_Ini_tab1.currentText() +'\n')
        paraFile.write('EPSILON='+ self.textEdit_Epsilon_tab1.text() +'\n')
        paraFile.write('CUT_HAPLOTYPEFREQUENCIES='+ self.textEdit_Cut_tab1.text() +'\n')
        paraFile.write('RENORMALIZE_HAPLOTYPEFREQUENCIES='+ self.combo_Norm_tab1.currentText() +'\n')
        paraFile.write('SEED='+ self.textEdit_Seed_tab1.text() +'\n')
        
        paraFile.close()
        
        # save copies of parameter file
        try:
            shutil.copyfile(self.path, dirSave)
        except FileNotFoundError:
            return
        shutil.copyfile(self.path, self.pathParaDefault)
        
        # emit Signal
        strResField = strRes.replace("f","field")
        epsSig = self.textEdit_Epsilon_tab1.text()
        paraDone = str(strResField)+"#"+self.inputForm+'#'+str(epsSig)+'#'+self.runIdIn+'#'+inpRun+'#'+resRun
        self.strParaSet.emit(paraDone)

        self.close()           


###################################################################
# main

if __name__ == '__main__':

    app = QApplication(sys.argv)
    listLociBD = ['A', 'B', 'C', 'DMA', 'DMB', 'DOA', 'DOB', 'DPA1', 'DPB1', 'DQA1', 'DQB1', 'DRB1', 'DRB3', 'DRB4', 'DRB5', 'E', 'F', 'G']
    dirHap = "\home"
    window = Parameters(listLociBD, dirHap)

    app.exec_()
