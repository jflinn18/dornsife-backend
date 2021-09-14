#!/usr/bin/python3
# -*- coding: utf-8 -*-

import dataInit

import sys, os, copy, configparser
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot

from POIWidget import POIWidget
from TourWidget import TourWidget
import Misc
from Misc import OverwriteProtectionWidget

class DornsifeCMSWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # initialize tab screen
        self.tabs = QTabWidget()
        self.tourTab = QWidget()
        self.poiTab = QWidget()
        self.awsTab = QWidget()
        self.tabs.resize(500,500)

        self.savedData = True

        # Add tabs
        self.tabs.addTab(self.awsTab, "AWS")
        self.tabs.addTab(self.tourTab, "Tours")
        self.tabs.addTab(self.poiTab, "Points")

        #-----------------------------------------------------------------------
        # Create AWS Update Tab
        self.awsTab.layout = QGridLayout(self.awsTab)
        self.awsTab.layout.setSpacing(10)

        self.awsTabDescription = QLabel()
        self.awsTabDescription.setText("Amazon Web Services Commands")
        self.awsTab.layout.addWidget(self.awsTabDescription, 0, 0)

        self.tempBtn = QPushButton("I should be hidden")
        self.awsTab.layout.addWidget(self.tempBtn, 0, 1)
        self.tempBtn.hide()

        # Update tours/points
        # Upload pictures/audio
        self.updateTourAndPointsBtn = QPushButton("Update Tours/Points")
        self.updateTourAndPointsBtn.clicked.connect(self.awsUpdateData)
        self.awsTab.layout.addWidget(self.updateTourAndPointsBtn, 1, 0)

        self.updateTourAndPointsDescription = QLabel()
        self.updateTourAndPointsDescription.setText("This updates all of the tour and point data")
        self.awsTab.layout.addWidget(self.updateTourAndPointsDescription, 1, 1)

        self.uploadFilesBtn = QPushButton("Upload Pictures/Audio")
        self.uploadFilesBtn.clicked.connect(self.awsUploadFiles)
        self.awsTab.layout.addWidget(self.uploadFilesBtn, 2, 0)

        self.uploadFilesDescription = QLabel()
        self.uploadFilesDescription.setText("This uploads new images and audio files placed in mydir/images or mydir/audio.\nWARNING: This may take a while")
        self.awsTab.layout.addWidget(self.uploadFilesDescription, 2, 1)

        self.tempLabel = QLabel()
        self.awsTab.layout.addWidget(self.tempLabel, 5, 0)
        self.awsTab.layout.addWidget(self.tempLabel, 6, 0)
        self.awsTab.layout.addWidget(self.tempLabel, 7, 0)
        self.awsTab.layout.addWidget(self.tempLabel, 8, 0)
        self.awsTab.layout.addWidget(self.tempLabel, 9, 0)
        self.awsTab.layout.addWidget(self.tempLabel, 10, 0)

        #-----------------------------------------------------------------------
        self.tourListSelected = None

        # Create Tours tab
        self.tourTab.layout = QGridLayout(self.tourTab)
        self.tourTab.layout.setSpacing(10)


        self.editBtn = QPushButton("Edit")
        self.editBtn.clicked.connect(self.editTour)        # onclick function
        self.tourTab.layout.addWidget(self.editBtn, 0, 4)

        self.createBtn = QPushButton("Create")
        self.createBtn.clicked.connect(self.createTour)      # onclick function
        self.tourTab.layout.addWidget(self.createBtn, 1, 4)

        self.deleteBtn = QPushButton("Delete")
        self.deleteBtn.clicked.connect(self.deleteTour)
        self.tourTab.layout.addWidget(self.deleteBtn, 2, 4)

        #self.updateBtn = QPushButton("Update AWS")
        #self.updateBtn.clicked.connect(dataInit.formatDataForUpload)
        #self.tourTab.layout.addWidget(self.updateBtn, 5, 4)

        self.tourList = QListWidget()
        self.tourList.resize(50, 50)
        self.tourList.setSortingEnabled(True)

        myFiles = os.listdir("mydir/")
        # Pull all tours from s3 and put into .csv files
        #for index, tourName in enumerate(myFiles):
        for index, tourName in enumerate(dataInit.tourData):
             #tempFileName = tourName.split(".")
             #self.tourList.addItem(tempFileName[0])
             self.tourList.addItem(tourName)
             #if index % 2 == 0:
            #     self.tourList.item(index).setBackground(QColor(227,235,247,255))

        self.recolorListItemBackgrounds(self.tourList)
        try: # Makes sure that there is an element in the list to select
            self.tourListSelected = self.tourList.item(0)
        except:
            pass
        self.tourList.itemClicked.connect(self.tourListSelectedObject)
        self.tourTab.layout.addWidget(self.tourList, 0, 0, 6, 1)

        self.tourTab.setLayout(self.tourTab.layout)



        #-----------------------------------------------------------------------
        self.newData = None
        self.oldData = None
        self.poiListSelected = None

        # Create poi tab
        self.poiTab.layout = QGridLayout(self.poiTab)
        self.poiTab.layout.setSpacing(10)
        self.editBtn = QPushButton("Edit")
        self.editBtn.clicked.connect(self.editPOI)
        self.poiTab.layout.addWidget(self.editBtn, 0, 4)


        self.createBtn = QPushButton("Create")
        self.createBtn.clicked.connect(self.createPOI)
        self.poiTab.layout.addWidget(self.createBtn, 1, 4)

        self.deleteBtn = QPushButton("Delete")
        self.deleteBtn.clicked.connect(self.deletePOI)
        self.poiTab.layout.addWidget(self.deleteBtn, 2, 4)

        self.poiList = QListWidget()
        self.poiList.resize(50, 50)
        self.poiList.setSortingEnabled(True)

        # Pull all tours from s3 and put into .csv files
        # This needs a little more thought and conversation with the backend


        #index = 0
        for poiID in dataInit.poiData:
            self.poiList.addItem(dataInit.poiData[poiID]["name"])
            #if index % 2 == 0:
            #    self.poiList.item(index).setBackground(QColor(227,235,247,255))
            #index += 1
        for poiID in dataInit.waypointData:
            self.poiList.addItem(dataInit.waypointData[poiID]["name"])
            #if index % 2 == 0:
            #    self.poiList.item(index).setBackground(QColor(227,235,247,255))
            #index += 1
        self.recolorListItemBackgrounds(self.poiList)
        try: # Makes sure that there is an element in the list to select
            self.poiListSelected = self.poiList.item(0)
        except:
            pass
        self.poiList.itemClicked.connect(self.poiListSelectedObject)
        self.poiTab.layout.addWidget(self.poiList, 0, 0, 6, 1)

        self.poiTab.setLayout(self.poiTab.layout)


        # Add tabs to Widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)



    def printMessage(self):
        print("[+] Not implemented yet")

    def poiListSelectedObject(self):
        self.poiListSelected = self.poiList.currentItem()

    def tourListSelectedObject(self):
        self.tourListSelected = self.tourList.currentItem()


    def createTour(self):
        self.createTourWindow = TourWidget(dataInit.poiData, dataInit.waypointData, dataInit.existingTourNames)
        self.createTourWindow.show()
        self.createTourWindow.saveBtn.clicked.connect(lambda: self.getNewTourData(False))

        self.savedData = False

    def editTour(self):
        self.editTourWindow = TourWidget(dataInit.poiData, dataInit.waypointData, dataInit.existingTourNames, edit=True)

        self.editTourWindow.tourName.setTourName(self.tourListSelected.text())

        for index, point in enumerate(dataInit.tourData[self.tourListSelected.text()]):
            try:
                try:
                    self.editTourWindow.tourPointsList.addItem(dataInit.poiData[point]["name"])
                except:
                    self.editTourWindow.tourPointsList.addItem(dataInit.waypointData[point]["name"])
            except KeyError:
                print("[!] A point in this tour has been deleted. Please save all, close, and reopen the program. The point will automatically be removed from the tour on close.")
            #if index % 2 == 0:
            #    self.editTourWindow.tourPointsList.item(index).setBackground(QColor(227,235,247,255))

        self.recolorListItemBackgrounds(self.editTourWindow.tourPointsList)
        self.editTourWindow.show()
        self.editTourWindow.saveBtn.clicked.connect(lambda: self.getNewTourData(True))

        self.savedData = False

    def deleteTour(self):
        try:
            tempTour = self.tourList.takeItem(self.tourList.row(self.tourListSelected))
            dataInit.deletedTours.append(tempTour.text().replace(" ", "_")+".json")
            del dataInit.tourData[tempTour.text()]

            #self.recolorTourListItemBackgrounds()
            self.recolorListItemBackgrounds(self.tourList)
        except Exception as e:
            print("[!]", e)

        self.tourListSelected = self.tourList.currentItem()

        self.savedData = False

    def getNewTourData(self, edit):
        if edit:
            self.editTourWindow.saveNewData()
            self.newData = self.editTourWindow.newTourPoints
            tourName = self.editTourWindow.tourName.getTourName()
            # Renaming a Tour
            if tourName != self.tourListSelected.text():
                del dataInit.tourData[self.tourListSelected.text()]
                dataInit.tourData[tourName] = self.newData
                dataInit.existingTourNames.remove(self.tourListSelected.text())
                tempTour = self.tourList.takeItem(self.tourList.row(self.tourListSelected))
                dataInit.deletedTours.append(tempTour.text().replace(" ", "_")+".json")
                self.tourList.addItem(tourName)

                self.recolorListItemBackgrounds(self.tourList)
                # Automatically reselects the same tour
                for itemIndex in range(self.tourList.count()):
                    if self.tourList.item(itemIndex).text() == tourName:
                        self.tourListSelected = self.tourList.item(itemIndex)
                        self.tourList.setCurrentRow(itemIndex)
                        break

        else:
            self.createTourWindow.saveNewData()
            self.newData = self.createTourWindow.newTourPoints
            tourName = self.createTourWindow.tourName.getTourName()

            self.tourList.addItem(tourName)
            self.recolorListItemBackgrounds(self.tourList)

        newIDList = []
        for poiName in self.newData:
            newIDList.append(dataInit.IDLookupTable[poiName])

        dataInit.tourData[tourName] = newIDList
        dataInit.existingTourNames.append(tourName)

        self.oldData = None
        self.newData = None


    def createPOI(self):
        self.createPOIWindow = POIWidget(dataInit.existingPOINames)
        self.createPOIWindow.show()
        self.createPOIWindow.saveBtn.clicked.connect(lambda: self.getNewPOIData(False))

        self.savedData = False

    def editPOI(self):
        self.editPOIWindow = POIWidget(dataInit.existingPOINames, edit=True)
        try:
            # Assumes that the name of the point is unique
            self.oldData = dataInit.poiData[dataInit.IDLookupTable[self.poiListSelected.text()]]
        except KeyError:
            self.oldData = dataInit.waypointData[dataInit.IDLookupTable[self.poiListSelected.text()]]

        if self.oldData != None:
            self.editPOIWindow.newPOIData = self.oldData
            for key, textBox in self.editPOIWindow.poiTextBoxes.items():
                try:
                    textBox[1].setText(self.oldData[key])
                    textBox[1].setCursorPosition(0)
                except KeyError:
                    pass
                except AttributeError:
                    pass

            try:
                self.editPOIWindow.poiDescriptionTextBox[1].setText(self.oldData["description"])
            except KeyError:
                pass

            currentIndex = self.editPOIWindow.typeDropDownBox[1].findText(self.oldData["type"])
            self.editPOIWindow.typeDropDownBox[1].setCurrentIndex(currentIndex)


        self.editPOIWindow.show()
        self.editPOIWindow.saveBtn.clicked.connect(lambda: self.getNewPOIData(True))


        self.savedData = False

    def deletePOI(self):
        try:
            tempPOI = self.poiList.takeItem(self.poiList.row(self.poiListSelected))
            tempPOIid = dataInit.IDLookupTable[tempPOI.text()]
            dataInit.deletedPOIs.append(tempPOIid)
            try:
                del dataInit.poiData[tempPOIid]
            except:
                del dataInit.waypointData[tempPOIid]
            del dataInit.IDLookupTable[tempPOI.text()]

            self.recolorListItemBackgrounds(self.poiList)
        except Exception as e:
            print("[!]", e)

        self.poiListSelected = self.poiList.currentItem()

        self.savedData = False

    def getNewPOIData(self, edit):
        newDataID = ""
        if edit:
            self.editPOIWindow.saveNewData()
            self.newData = self.editPOIWindow.newPOIData
            newDataID = self.newData["ID"]
            dataInit.editedPOIs[newDataID]  = copy.deepcopy(self.newData)

            if self.newData["name"] != self.poiListSelected.text():
                del dataInit.IDLookupTable[self.poiListSelected.text()]
                dataInit.IDLookupTable[self.newData["name"]] = self.newData["ID"]

                tempPOI = self.poiList.takeItem(self.poiList.row(self.poiListSelected))
                self.poiList.addItem(self.newData["name"])

                self.recolorListItemBackgrounds(self.poiList)
                for itemIndex in range(self.poiList.count()):
                    if self.poiList.item(itemIndex).text() == self.newData["name"]:
                        self.poiListSelected = self.poiList.item(itemIndex)
                        self.poiList.setCurrentRow(itemIndex)
                        break
        else:
            self.createPOIWindow.saveNewData()
            self.newData = self.createPOIWindow.newPOIData
            newDataID = str(dataInit.nextID)
            dataInit.nextID += 1
            self.newData["ID"] = newDataID
            dataInit.createdPOIs[newDataID] = copy.deepcopy(self.newData)


            dataInit.IDLookupTable[self.newData["name"]] = newDataID
            self.poiList.addItem(self.newData["name"])
            #if (self.poiList.count() - 1) % 2 == 0:
            #    self.poiList.item(self.poiList.count() -1).setBackground(QColor(227,235,247,255))

        self.recolorListItemBackgrounds(self.poiList)
        if self.newData["type"] == "Waypoint":
            dataInit.waypointData[newDataID] = self.newData
        else:
            dataInit.poiData[newDataID] = self.newData
        dataInit.existingPOINames.append(self.newData["name"])

        # Resets the types of data so that a list can be stored in it later
        self.oldData = None
        self.newData = None


    def recolorListItemBackgrounds(self, myList):
        for itemIndex in range(myList.count()):
            if itemIndex % 2 == 0:
                myList.item(itemIndex).setBackground(QColor(240,240,240,255))
            else:
                myList.item(itemIndex).setBackground(QColor(255,255,255,255))

    def awsUpdateData(self):
        tempList = []
        for index in range(self.tourList.count()):
            tempList.append(self.tourList.item(index).text())

        self.savedData = True
        dataInit.formatDataForUpload(listToursToDelete=tempList)

    def awsUploadFiles(self):
        #self.savedData = True
        dataInit.uploadFiles()

class TabWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dornsife CMS")
        self.setGeometry(150,150,750,500)

        self.tableWidget = DornsifeCMSWidget(self)
        self.setCentralWidget(self.tableWidget)

        self.show()

    def closeEvent(self, event):
        if self.tableWidget.savedData == False:
            quit_msg = "WARNING: You have unsaved changes.\nAre you sure you want exit?"
            reply = QMessageBox.question(self, 'Message',
                    quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                #dataInit.formatDataForUpload()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #print(app.desktop().screenGeometry())
    mainWidget = TabWindow()

    sys.exit(app.exec_())
