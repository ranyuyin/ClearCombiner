# coding=utf-8
import sys
from PyQt5.QtWidgets import (QWidget, QTextEdit,QLineEdit,QHBoxLayout, QPushButton,QVBoxLayout,
                             QAction, QFileDialog, QApplication,QLabel)
import fmaskLandsat5
from PyQt5.QtGui import QIcon
class qUfmask(QWidget):
    def __init__(self):
        super(qUfmask, self).__init__()
        self.initUI()
    def initUI(self):
        hbox = QHBoxLayout()
        hboxrun=QHBoxLayout()
        vbox=QVBoxLayout()
        self.exButton = QPushButton("浏览",self)
        self.exButton.clicked.connect(self.selectfold)
        self.runButton=QPushButton("运行")
        self.runButton.sizeHint()
        self.runButton.clicked.connect(self.dowalkfmask)
        hboxrun.addStretch(0)
        hboxrun.addWidget(self.runButton)
        hboxrun.addStretch(0)
        self.foldnEdit=QLineEdit(self)
        foldlabel=QLabel(r'影像根目录：')
        hbox.addStretch(1)
        hbox.addWidget(foldlabel)
        hbox.addWidget(self.foldnEdit)
        hbox.addWidget(self.exButton)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addLayout(hboxrun)
        self.setLayout(vbox)
        self.setWindowTitle(r'序列遥感数据质量检测-云')
        self.sizeHint()
        self.show()

    def selectfold(self):
        name = QFileDialog.getExistingDirectory(self)
        self.foldnEdit.setText(name)
    def dowalkfmask(self):
        rootdir=self.foldnEdit.text()
        fmaskLandsat5.walkfmask(rootdir)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = qUfmask()
    sys.exit(app.exec_())