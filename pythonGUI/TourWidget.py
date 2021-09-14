#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot


class TourWidget(QWidget):
    # param edit is to see what to name the window
    def __init__(self, poiData, waypointData, tourNames, edit=False):
        super().__init__()
        self.layout = QGridLayout(self)
        self.setGeometry(500,300,750,400)
        #self.setFixedSize(750,500)

        # Need to edit this depending on weather we are creating or editing
        if edit:
            self.setWindowTitle("Edit Tour")
        else:
            self.setWindowTitle("Create Tour")

        self.savedData = True

        # Member variable Declaration
        self.poiListCurrentItemSelected = None
        self.waypointsListCurrentItemSelected = None
        self.tourPointsListCurrentItemSelected = None
        self.oldTourPoints = None
        #self.tourName = None
        self.existingTourNames = tourNames
        # Chose a list because the order of the points needs to be saved
        self.newTourPoints = []

        self.tourName = TourNameWidget()
        self.layout.addWidget(self.tourName, 0, 0)
        """
        self.tourNameLabel = QLabel()
        self.tourNameLabel.setText("Tour Name: ")
        self.layout.addWidget(self.tourNameLabel, 0, 0)

        self.editTourName = QLineEdit()
        self.layout.addWidget(self.editTourName, 0, 0)
        """

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs, 1,0,5,1)

        self.tabIndex = {0:"poiList", 1:"waypointsList"}

        self.poiList = QListWidget()
        self.poiList.setSortingEnabled(True)
        #self.layout.addWidget(self.poiList, 1, 0, 5, 1)
        self.poiList.clicked.connect(self.poiListItemGetSelected)
        for index, poi in enumerate(poiData):
            self.poiList.addItem(poiData[poi]["name"])
            #if index % 2 == 0:
            #    self.poiList.item(index).setBackground(QColor(227,235,247,255))
        self.recolorListItemBackgrounds(self.poiList)

        self.waypointsList = QListWidget()
        self.waypointsList.setSortingEnabled(True)
        self.waypointsList.clicked.connect(self.waypointsListItemGetSelected)
        for index, waypoint in enumerate(waypointData):
            try:
                self.waypointsList.addItem(waypointData[waypoint]["name"])
            except:
                self.waypointsList.addItem(waypointData[waypoint]["ID"])
            #if index % 2 == 0:
            #    self.waypointsList.item(index).setBackground(QColor(227,235,247,255))
        self.recolorListItemBackgrounds(self.waypointsList)

        self.tabs.addTab(self.poiList, "POIs")
        self.tabs.addTab(self.waypointsList, "Waypoints")


        self.tourPointsList = QListWidget()
        self.layout.addWidget(self.tourPointsList, 1, 2, 5, 1)
        self.tourPointsList.clicked.connect(self.tourPointsListGetSelected)

        self.addBtn = QPushButton()
        self.addBtn.setText(" -> ")
        self.addBtn.clicked.connect(self.addPOI2Tour)
        self.layout.addWidget(self.addBtn, 3, 1)

        self.upBtn = QPushButton()
        self.upBtn.setText("Up")
        self.upBtn.clicked.connect(self.movePointUp)
        self.layout.addWidget(self.upBtn, 1, 5)

        self.downBtn = QPushButton()
        self.downBtn.setText("Down")
        self.downBtn.clicked.connect(self.movePointDown)
        self.layout.addWidget(self.downBtn, 2, 5)

        self.deleteBtn = QPushButton()
        self.deleteBtn.setText("Delete")
        self.deleteBtn.clicked.connect(self.deletePOIFromTour)
        self.layout.addWidget(self.deleteBtn, 3, 5)

        self.saveBtn = QPushButton()
        self.saveBtn.setText("Save Tour")
        self.layout.addWidget(self.saveBtn, 5, 5)

        #self.setLayout(self.layout)


    def poiListItemGetSelected(self):
        self.poiListCurrentItemSelected = self.poiList.currentItem()

    def tourPointsListGetSelected(self):
        self.tourPointsListCurrentItemSelected = self.tourPointsList.currentItem()

    def waypointsListItemGetSelected(self):
        self.waypointsListCurrentItemSelected = self.waypointsList.currentItem()

    def addPOI2Tour(self):
        newPoint2Add = None
        # A little bit of duplicate code is needed because to decrease conditional
        #  checks. By having the duplicate code, we reduce one check
        if self.tabs.currentIndex() == 0:
            if self.poiListCurrentItemSelected != None:
                self.tourPointsList.addItem(self.poiListCurrentItemSelected.text())
        else:
            if self.waypointsListCurrentItemSelected != None:
                self.tourPointsList.addItem(self.waypointsListCurrentItemSelected.text())
        self.recolorListItemBackgrounds(self.tourPointsList)

        self.savedData = False

    def deletePOIFromTour(self):
        try:
            self.tourPointsList.takeItem(self.tourPointsList.row(self.tourPointsListCurrentItemSelected))
        except:
            print("[*] Nothing Selected")
        self.tourPointsListCurrentItemSelected = self.tourPointsList.currentItem()

        self.recolorListItemBackgrounds(self.tourPointsList)

        self.savedData = False

    def saveNewData(self):
        tempNewTour = []
        for index in range(self.tourPointsList.count()):
            #self.newTourPoints.append(self.tourPointsList.item(index).text())
            tempNewTour.append(self.tourPointsList.item(index).text())
        self.newTourPoints = tempNewTour


        try:
            nameIncrementor = 1
            if self.tourName.getTourName() == "":
                self.tourName.setTourName("Unnamed Tour")
            if not edit:
                while self.tourName.getTourName() in self.existingTourNames:
                    self.tourName.setTourName(self.tourName.getTourName() + str(nameIncrementor))
                    nameIncrementor += 1
        except:
            pass

        #self.destroy(destroyWindow=True)
        self.savedData = True


    def movePointUp(self):
        currentlySelectedIndex = self.tourPointsList.currentRow()

        try:
            tempListItem = self.tourPointsList.takeItem(currentlySelectedIndex)
            self.tourPointsList.insertItem(currentlySelectedIndex - 1, tempListItem)
            self.tourPointsList.setCurrentItem(tempListItem)
            self.recolorListItemBackgrounds(self.tourPointsList)
        except:
            print("[!] movePointUp failed!")

        self.savedData = False

    def movePointDown(self):
        currentlySelectedIndex = self.tourPointsList.currentRow()

        try:
            tempListItem = self.tourPointsList.takeItem(currentlySelectedIndex)
            self.tourPointsList.insertItem(currentlySelectedIndex + 1, tempListItem)
            self.tourPointsList.setCurrentItem(tempListItem)
            self.recolorListItemBackgrounds(self.tourPointsList)
        except:
            print("[!] movePointDown failed!")

        self.savedData = False


    def recolorListItemBackgrounds(self, myList):
        for itemIndex in range(myList.count()):
            if itemIndex % 2 == 0:
                myList.item(itemIndex).setBackground(QColor(240,240,240,255))
            else:
                myList.item(itemIndex).setBackground(QColor(255,255,255,255))

    def closeEvent(self, event):
        if self.savedData == False:
            quit_msg = "You have unsaved changes. Are you sure you want to close?"
            reply = QMessageBox.question(self, 'Message',
                     quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

class TourNameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(self)
        self.setFixedHeight(100)

        self.tourNameLabel = QLabel()
        self.tourNameLabel.setText("Tour Name: ")
        self.layout.addWidget(self.tourNameLabel, 0, 0)

        self.editTourName = QLineEdit()
        self.layout.addWidget(self.editTourName, 0, 1)

        # This just makes it pleasant to look at
        self.blankSpace = QLabel()
        self.blankSpace.setText(" ")
        self.layout.addWidget(self.blankSpace, 0, 2)
        self.layout.addWidget(self.blankSpace, 0, 3)
        self.layout.addWidget(self.blankSpace, 0, 4)

    def setTourName(self, tourName):
        self.editTourName.setText(tourName)
        self.editTourName.setCursorPosition(0)

    def getTourName(self):
        return self.editTourName.text()
