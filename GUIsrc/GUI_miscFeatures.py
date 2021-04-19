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

GUI_miscFeatures.py
some general settings and dialoges

@author: Ute Solloch
'''''

# # fbs app special
# from fbs_runtime.application_context.PyQt5 import ApplicationContext

# import modules:
import sys, os
from collections import defaultdict
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (QApplication, QGridLayout, QVBoxLayout, QTextBrowser,
                             QLabel, QFrame, QPushButton, QMessageBox, QDesktopWidget)
from PyQt5.Qt import (QWidget, pyqtSlot, QVBoxLayout, pyqtSignal)
from PyQt5.QtCore import QObject, pyqtSignal, QFile, QTextStream, Qt

# QT settings:
label_style_normal = "QLabel {default}"
label_style_info = "QLabel { color: blue; }"
label_style_white = "QLabel {background-color: white; border: 1px solid #7accde; border-radius: 2;}"
label_style_grey = "QLabel {background-color: white; inset grey; min-height: 200px; border-radius: 2;}"
label_style_inactive = "QLabel { background-color: #ededed; border: 1px solid #d1d1cd; border-radius: 2;}"

button_style_cancel = " QPushButton:hover { border: 2px solid #E2001A }" " QPushButton { background-color: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #e6e9eb, stop: 1 #fc6d73); }"
button_style_info = " QPushButton:hover { border: 2px solid #707070 }" " QPushButton { background-color: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #e6e9eb, stop: 1 #90aba9); }"

#"DKMSred" : "#E2001A",
#"DKMSyellow" : "#FDDB00",
#"DKMSpurple" : "#743BBC",
#"DKMSblue" : "#00A2E1",
#"DKMSgreen" : "#78D64A",
#"DKMSlightpink" : "#F59BA5",
#"DKMSpink" : "#ED6676",
#"DKMSdarkpink" : "#E53449",

# classes:    
class UnderConstruction(QWidget):
    """a widget to show that something is not implemented yet
    """
    def __init__(self):
        """constructor
        """
        super().__init__()
        self.initUI()
        
    def initUI(self):
        """define the GUI
        """  

        # # fbs app special
        # appctxt = ApplicationContext()
        # pixmap= QPixmap(appctxt.get_resource("construction.jpg")).scaledToWidth(100)
        pixmap = QPixmap(os.path.join("Icons","construction.jpg")).scaledToWidth(100)
        
        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300,30)
        
        # move to center of App
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
        self.pic_lbl = QLabel(self)
        self.pic_lbl.setPixmap(pixmap)
        grid.addWidget(self.pic_lbl, 0, 0)
        
        self.text = QLabel("Under construction!", self)
        self.text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        grid.addWidget(self.text, 0, 1)
        
        self.show()
        




#################################        

class InfoWidget(QWidget):
    """Parameter window
    """

    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        """define the GUI
        """   
        
        # # fbs app special
        # appctxt = ApplicationContext()
        # infoText = open(appctxt.get_resource('Licenses.txt')).read()
        infoText = open("Licenses.txt").read()

        #positioning
        self.setMinimumSize(800,400)
        self.center()
        layout = QVBoxLayout()
        labOutputBD = QTextBrowser()
        labOutputBD.verticalScrollBar().setStyleSheet('background: grey')
        layout.addWidget(labOutputBD)
        labOutputBD.setText(infoText)
        self.setLayout(layout)
        self.show()

# Functions

    def center(self):
        """moves window to screen center
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        
#####################################
        
class TutorialWidget(QWidget):
    """Parameter window
    """

    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        """define the GUI
        """   
        #positioning
        self.setMinimumSize(800,400)
        self.center()
        layout = QVBoxLayout()
        labOutputT = QTextBrowser()
        labOutputT.verticalScrollBar().setStyleSheet('background: grey')

        # fbs app special
        # appctxt = ApplicationContext()
        # f = QFile(appctxt.get_resource('ManualHapl-o-MatViaGUI.htm'))
        f = QFile("ManualHapl-o-MatViaGUI.htm")
        
        f.open(QFile.ReadOnly|QFile.Text)
        istream = QTextStream(f)
        labOutputT.setHtml(istream.readAll())
        f.close()
        layout.addWidget(labOutputT)
        
        self.setLayout(layout)
        self.show()
        
        
        
# Functions

    def center(self):
        """moves window to screen center
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        
        
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
