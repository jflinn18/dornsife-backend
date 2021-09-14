#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot


# This is to edit and create a selected POI from the list of POIs in the GUI

class POIWidget(QWidget):
    # oldData needs to be a dictionary
    # param edit is to see what to name the window
    def __init__(self, poiNames, edit=False):
        super().__init__()
        self.layout = QGridLayout(self)
        self.setGeometry(250,250,700,500)
        #self.setFixedSize(500,500)

        # Need to edit this depending on if we are editing or creating a POI
        if edit:
            self.setWindowTitle("Edit Point")
        else:
            self.setWindowTitle("Create Point")

        self.newPOIData = {}
        self.savedData = True
        self.existingPOINames = poiNames
        #self.oldPOIData = None

        poiDataNames = ["name", "address", "latitude", "longitude", "type", "website", "pictureFile", "audioFile","excerpt", "tourDescription", "description", "phone"]
        poiLineEditDataNames = ["name", "address", "latitude", "longitude", "website","phone", "pictureFile", "audioFile", "additionalWebsites", "excerpt", "tourDescription"]
        poiNameMap = {"name":"Name","address": "Address", "description": "Description", "type": "Type", "latitude": "Latitude", "tourDescription":"Tour Description", "longitude":"Longitude","pictureFile":"Picture Filename", "audioFile":"Audio Filename", "excerpt":"Excerpt (50 chars)", "website":"Website URL", "phone": "Phone Number", "additionalWebsites":"Additional Websites \n(Space seperated)"}

        # This needs to be redone. Put the type of point at the top in a drop down
        #   If the the type of point is a waypoint, then only show GPS, else show
        #   all fields. This can be done with the hide() and show() functions

        self.pointTypes = ["Business", "Informational", "Volunteer", "Worship", "Waypoint"]
        self.typeDropDownBox = (QLabel(), QComboBox())
        self.typeDropDownBox[0].setText("Type")
        for pType in self.pointTypes:
            self.typeDropDownBox[1].addItem(pType)
        self.layout.addWidget(self.typeDropDownBox[0], 0, 0)
        self.layout.addWidget(self.typeDropDownBox[1], 0, 1)


        self.poiTextBoxes = {}
        incrementor = 1
        for data in poiLineEditDataNames:
            self.poiTextBoxes[data] = (QLabel(), QLineEdit())
            self.poiTextBoxes[data][0].setText(poiNameMap[data])
            self.layout.addWidget(self.poiTextBoxes[data][0], incrementor,0)
            self.layout.addWidget(self.poiTextBoxes[data][1], incrementor,1)
            incrementor += 1


        self.poiDescriptionTextBox = (QLabel(), QTextEdit())
        self.poiDescriptionTextBox[0].setText("Description")
        self.layout.addWidget(self.poiDescriptionTextBox[0], incrementor,0)
        self.layout.addWidget(self.poiDescriptionTextBox[1], incrementor,1, 5, 1)

        self.saveBtn = QPushButton("Save")
        #self.saveBtn.clicked.connect(self.saveNewData)
        self.layout.addWidget(self.saveBtn, incrementor+4,2)

        self.picPath = ""
        self.picBrowseBtn = QPushButton("Browse")
        self.picBrowseBtn.clicked.connect(self.picBrowse)
        self.layout.addWidget(self.picBrowseBtn, 7, 2)

        self.audioPath = ""
        self.audioBrowseBtn = QPushButton("Browse")
        self.audioBrowseBtn.clicked.connect(self.audioBrowse)
        self.layout.addWidget(self.audioBrowseBtn, 8, 2)

        #self.layout.addWidget(poiTextBoxes["address"], 1, 0)

    # Creates a new POI in the DynamoDB
    def saveNewData(self):
        for key, val in self.poiTextBoxes.items():
            if val[1].text() != '':
                self.newPOIData[key] = val[1].text()
            else:
                try:
                    del self.newPOIData[key]
                except:
                    pass


        self.newPOIData["type"] = self.typeDropDownBox[1].currentText()
        if self.poiDescriptionTextBox[1].toPlainText() != "":
            self.newPOIData["description"] = self.poiDescriptionTextBox[1].toPlainText()
        if self.picPath != "":
            self.newPOIData["pictureFile"] = self.picPath
        if self.audioPath != "":
            self.newPOIData["audioFile"] = self.audioPath

        try:
            nameIncrementor = 1
            if not edit:
                while self.newPOIData["name"] in self.existingPOINames:
                    self.newPOIData["name"] += str(nameIncrementor)
                    nameIncrementor += 1
        except:
            pass

        self.savedData = True

    def picBrowse(self):
        selectedFilename = QFileDialog.getOpenFileName(directory="mydir/images")
        tempFileName = selectedFilename[0].split("/")
        self.poiTextBoxes["pictureFile"][1].setText(tempFileName[-1])


    def audioBrowse(self):
        selectedFilename = QFileDialog.getOpenFileName(directory="mydir/audio")
        tempFileName = selectedFilename[0].split("/")
        self.poiTextBoxes["audioFile"][1].setText(tempFileName[-1])


    def closeEvent(self, event):
        if self.savedData == False:
            quit_msg = "Are you sure you want Cancel?"
            reply = QMessageBox.question(self, 'Message',
                        quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
