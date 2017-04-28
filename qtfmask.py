# coding=utf-8
import sys
from PyQt5.QtWidgets import (QWidget, QTextEdit,QLineEdit,QHBoxLayout, QPushButton,QVBoxLayout,
                             QAction, QFileDialog, QApplication,QLabel,QProgressBar,QMessageBox)
import fmaskLandsat5
from PyQt5.QtGui import QIcon
class qUfmask(QWidget):
    def __init__(self):
        super(qUfmask, self).__init__()#super
        self.initUI()#self
    def initUI(self):
        hboxdir=QHBoxLayout()#QhBoxLayout
        hboxrun=QHBoxLayout()
        vbox=QVBoxLayout()
        self.exButton = QPushButton("浏览",self)
        self.exButton.clicked.connect(self.selectfold)
        self.runButton=QPushButton("运行")
        self.runButton.sizeHint()
        self.runButton.clicked.connect(self.domainwork)
        hboxrun.addStretch(0)
        hboxrun.addWidget(self.runButton)
        hboxrun.addStretch(0)
        self.pbar= QProgressBar(self)
        self.foldnEdit=QLineEdit(self)
        foldlabel=QLabel(r'影像根目录：')
        hboxdir.addStretch(1)
        hboxdir.addWidget(foldlabel)
        hboxdir.addWidget(self.foldnEdit)
        hboxdir.addWidget(self.exButton)
        hboxdir.addStretch(1)
        vbox.addLayout(hboxdir)
        vbox.addWidget(self.pbar)
        vbox.addLayout(hboxrun)
        self.setLayout(vbox)
        self.setWindowTitle(r'序列遥感数据质量检测-云')
        self.sizeHint()
        self.show()

    def selectfold(self):
        name = QFileDialog.getExistingDirectory(self)
        self.foldnEdit.setText(name)
        return

    def domainwork(self):
        rootdir=self.foldnEdit.text()
        fmaskLandsat5.walkfmask(rootdir,self.pbar)
        fmaskLandsat5.walkclearQA(rootdir,self.pbar)
        ok=QMessageBox.information(self,'信息','完成！')
        self.pbar.reset()
        self.foldnEdit.clear()
        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex=qUfmask()
    sys.exit(app.exec_())