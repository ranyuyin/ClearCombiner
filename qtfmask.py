# coding=utf-8
import sys
from PyQt5.QtWidgets import (QWidget, QTextEdit,QLineEdit,QHBoxLayout, QPushButton,QVBoxLayout,
                             QAction, QFileDialog, QApplication,QLabel)
from PyQt5.QtGui import QIcon
class qUfmask(QWidget):
    def __init__(self):
        super(qUfmask, self).__init__()
        self.initUI()
    def initUI(self):
        hbox1 = QHBoxLayout()
        hboxrun=QHBoxLayout()
        vbox=QVBoxLayout()
        self.exButton = QPushButton("浏览",self)
        self.exButton.clicked.connect(self.selectfold)
        self.runButton=QPushButton("运行")
        self.runButton.sizeHint()
        hboxrun.addStretch(0)
        hboxrun.addWidget(self.runButton)
        hboxrun.addStretch(0)
        self.foldnEdit=QLineEdit(self)
        foldlabel=QLabel(r'影像根目录：')
        hbox1.addStretch(1)
        hbox1.addWidget(foldlabel)
        hbox1.addWidget(self.foldnEdit)
        hbox1.addWidget(self.exButton)
        hbox1.addStretch(1)
        vbox.addLayout(hbox1)
        vbox.addLayout(hboxrun)
        self.setLayout(vbox)
        self.setWindowTitle(r'序列遥感数据质量检测-云')
        self.sizeHint()
        self.show()

    def selectfold(self):
        name = QFileDialog.getExistingDirectory(self)
        self.foldnEdit.setText(name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = qUfmask()
    sys.exit(app.exec_())