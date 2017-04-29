# coding=utf-8
import os
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
        filenamelist=os.listdir(name)
        subfoldlist=[i for i in filenamelist if os.path.isdir(os.path.join(name,i))]
        if len(subfoldlist)>16:
            reply1=QMessageBox.information(self,'warnning',"The number of documents does't satisfy the requirements!")
        else:
            sorted(subfoldlist, key=lambda d: float(d[3:8]))
            if subfoldlist[0][3:9]==subfoldlist[-1][3:9]:
                self.foldnEdit.setText(name)
            else:
                  reply2=QMessageBox.information(self,'warnning',"The image you selected is not in the same area!")
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
