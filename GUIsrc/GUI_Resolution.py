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

GUI_Resolution.py
Widget for locus resolution settings

@author: Ute Solloch
'''

# fbs app special
# from fbs_runtime.application_context.PyQt5 import ApplicationContext


# import modules:
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5 import QtCore
import os, platform
import sys

# import own modules
import GUI_miscFeatures


class Resolution(QWidget):
    """Window for choice of loci resolution 
    """
    strRes = pyqtSignal(str)    

    def __init__(self, listLoci, dictRes):
        super(Resolution, self).__init__()
        
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)        
        self.center()        
        self.listLoci = listLoci
        self.dictRes = dictRes
        
        self.initUI()
        
    def initUI(self):
        """define the GUI
        """       
        
        global pixmap_TT 
        
        # platform and stylesheet  
        try:        
            styleFile = GUI_miscFeatures.CONFIGURATION_FILES[platform.system()]["styleSheet"]  
        except:
            print("StyleSheet: Your current OS is not supported.")
        # fbs app special
        self.setStyleSheet(open(styleFile, "r").read())
        # appctxt = ApplicationContext()
        # appctxt.app.setStyleSheet(open(appctxt.get_resource(styleFile)).read())  
        
        self.drop_resolutions = ['g', 'G', 'P', '1field', '2field', '3field', '4field', 'ignore locus']              
        
        self.layout = QVBoxLayout()
        layoutH0 = QHBoxLayout()
        layoutH1 = QHBoxLayout()
        labL = QLabel('Locus')
        labR = QLabel('Resolution')
        layoutH0.addStretch(1)
        layoutH1.addWidget(labL)
        layoutH1.addWidget(labR)
        
        self.layout.addLayout(layoutH0)
        self.layout.addLayout(layoutH1)

        self.labDict = dict()
        self.comboDict = dict()
        # dynamic generation of Locus lines
        for loc in self.listLoci:
            layoutH = QHBoxLayout()
            lab = QLabel(loc)
            lab.setMinimumWidth(60)
            labName = loc
            lab.setObjectName(labName)
            self.labDict[labName] = lab
            combo = QComboBox()
            combo.setMinimumWidth(120)
            combo.addItems(self.drop_resolutions)            
            # default combo setting
            set = self.dictRes[loc]
            if set == 'null':
                pass
            else: 
                index = combo.findText(set)
                if index >= 0:
                    combo.setCurrentIndex(index)
            self.comboDict[labName] = combo
            layoutH.addWidget(lab)
            layoutH.addWidget(combo)
            self.layout.addLayout(layoutH)
        
        hbox0 = QHBoxLayout()
        lab = QLabel('')
        hbox0.addWidget(lab)
        hbox1 = QHBoxLayout()
        btnReadRes = QPushButton('Save')
        btnCancel = QPushButton('Cancel')
        btnCancel.setStyleSheet(GUI_miscFeatures.button_style_cancel)
        hbox1.addStretch(1)
        hbox1.addWidget(btnCancel)
        hbox1.addWidget(btnReadRes)
        self.layout.addLayout(hbox0)
        self.layout.addLayout(hbox1)
        btnReadRes.clicked.connect(self.saveResolution)
        btnCancel.clicked.connect(self.close)
        
        self.setLayout(self.layout)
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
    
    def saveResolution(self):
        """emits signal with resolution choice to SetParameter window
        """
        stringR = ''
        for loc in self.listLoci:
            combo = self.comboDict[loc]
            res = str(combo.currentText())
            if res == 'ignore locus':
                pass
            else:
                stringR = stringR +','+loc+':'+res
        stringR = stringR[1:]
        self.strRes.emit(stringR)
        self.close()



###################################################################
# main

if __name__ == '__main__':
 
    app = QApplication(sys.argv)
    listLoci = ['A', 'B', 'C','D']
    dictRes = {'A':'g','B':'G','C':'null','D':'ignore locus'}
    window = Resolution(listLoci, dictRes)
    app.exec_()