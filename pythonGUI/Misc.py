import sys, os, platform
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class OverwriteProtectionWidget(QWidget):
    def __init__(self, protected):
        super().__init__()
        self.layout = QGridLayout(self)
        self.setGeometry(500,500,200,100)
        self.setFixedSize(300,100)

        self.setWindowTitle("Overwrite Protection")

        self.protectedItem = protected

        self.message = QLabel()
        self.message.setText(self.protectedItem+" already exists.")
        self.layout.addWidget(self.message, 0,0,2,1)

        self.okBtn = QPushButton()
        self.okBtn.setText("OK")
        self.layout.addWidget(self.okBtn, 2, 1)
        #self.okBtn.clicked.connect(self.confirm)

        self.newName = QLineEdit()
        self.layout.addWidget(self.newName, 1, 0, 2, 1)

    def confirm(self):
        if self.newName.text() != "":
            self.protectedItem = self.newName.text()

        self.destroy(destroyWindow=True)
