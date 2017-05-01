# coding=utf-8
import os
import sys
from PyQt5.QtWidgets import (QWidget, QTextEdit,QLineEdit,QHBoxLayout, QPushButton,QVBoxLayout,
                             QAction, QFileDialog, QApplication,QLabel,QProgressBar,QMessageBox,
                             )
from PyQt5.QtGui import QFont
import fmaskLandsat5
from PyQt5.QtGui import QIcon
class qUfmask(QWidget):
    def __init__(self):
        super(qUfmask, self).__init__()#super
        self.initUI()#self
    def initUI(self):
        #大标题
        Title=QLabel(r'序列遥感数据质量评估v1.0')
        TitleFont=QFont('楷体',20,QFont.Bold)
        Title.setFont(TitleFont)
        #影像根目录BOX
        hboxdir=QHBoxLayout()#QhBoxLayout
        self.direxButton = QPushButton("浏览", self)
        self.direxButton.clicked.connect(self.selectfold)
        self.foldnEdit=QLineEdit(self)
        foldlabel=QLabel(r'  影像根目录：')
        hboxdir.addStretch(1)
        hboxdir.addWidget(foldlabel)
        hboxdir.addWidget(self.foldnEdit)
        hboxdir.addWidget(self.direxButton)
        hboxdir.addStretch(1)

        #clearQA路径选择BOX
        clearQAlable=QLabel(r'序列评估结果：')
        self.QAEdit = QLineEdit(self)
        self.QAexButton = QPushButton("浏览", self)
        self.QAexButton.clicked.connect(self.saveQAindex)
        QAhbox=QHBoxLayout()
        QAhbox.addStretch(1)
        QAhbox.addWidget(clearQAlable)
        QAhbox.addWidget(self.QAEdit)
        QAhbox.addWidget(self.QAexButton)
        QAhbox.addStretch(1)

        #运行按钮BOX
        hboxrun=QHBoxLayout()
        self.runButton=QPushButton("运行")
        self.runButton.sizeHint()
        self.runButton.clicked.connect(self.domainwork)
        hboxrun.addStretch(0)
        hboxrun.addWidget(self.runButton)
        hboxrun.addStretch(0)

        #总BOX
        self.pbar= QProgressBar(self)
        self.pbar.setValue(0)
        vbox=QVBoxLayout()
        vbox.addSpacing(10)
        vbox.addWidget(Title)
        vbox.addSpacing(10)
        vbox.addLayout(hboxdir)
        vbox.addSpacing(5)
        vbox.addLayout(QAhbox)
        vbox.addSpacing(5)
        vbox.addWidget(self.pbar)
        vbox.addSpacing(5)
        vbox.addLayout(hboxrun)
        self.setLayout(vbox)
        self.setWindowTitle(r'序列遥感数据质量检测-云')
        self.sizeHint()
        self.show()
        #运行标记
        self.doQAtag=True

    def selectfold(self):
        rootdirname = QFileDialog.getExistingDirectory(self,'选择文件夹',self.foldnEdit.text())
        if rootdirname=='':
            return
        rootdirname=rootdirname.replace('/','\\')
        filenamelist=os.listdir(rootdirname)
        subfoldlist=[i for i in filenamelist if os.path.isdir(os.path.join(rootdirname,i))]
        if len(subfoldlist)>16:
            reply1=QMessageBox.information(self,'警告',"输入数量过多，无法进行综合，将只进行云检测！")
            self.doQAtag=False
        try:
            sorted(subfoldlist, key=lambda d: float(d[3:8]))
        except ValueError:
            QMessageBox.information(self, '错误', "请保证输入路径内仅包含未修改名称的Landsat原始数据文件夹!")
            return
        if subfoldlist[0][3:9]!=subfoldlist[-1][3:9]:
            reply2=QMessageBox.information(self, '警告', "输入空间范围不一致，无法进行综合，将只进行云检测！")
            self.doQAtag=False
        if self.doQAtag&(self.QAEdit.text() == ''):
            self.QAEdit.setText(os.path.join(rootdirname,'clearQA.tif'))
        self.foldnEdit.setText(rootdirname)
        self.QAformat = 'GTiff'
        return

    def saveQAindex(self):
        clearQAname = QFileDialog.getSaveFileName(self,'保存为',self.QAEdit.text(),
                                                  'GeoTiff(*.tif);;Erdas Image(*.img)')
        if clearQAname[0] == '':
            return
        if clearQAname[1] == 'GeoTiff(*.tif)':
            self.QAformat='GTiff'
        elif clearQAname[1] == 'Erdas Image(*.img)':
            self.QAformat = 'HFA'

        clearQAname = clearQAname[0].replace('/','\\')
        self.QAEdit.setText(clearQAname)

    def domainwork(self):
        rootdir = self.foldnEdit.text()
        fmaskLandsat5.walkfmask(rootdir,self.pbar)
        if self.doQAtag:
            #在clearQA影像的同一目录下生成index.txt
            QAconfigPar = QAconfig(drivename=self.QAformat, QAname=self.QAEdit.text(),
                                   indexname=os.path.join(
                                       os.path.split(self.QAEdit.text())[-2],
                                       'index.txt'))
            fmaskLandsat5.walkclearQA(rootdir,pbar=self.pbar,QAconfig=QAconfigPar)
        else:
            self.pbar.setValue(2*self.pbar.value())
            ok = QMessageBox.information(self, '信息', '完成！(已跳过综合评估)')
        ok=QMessageBox.information(self,'信息','完成！')
        self.pbar.reset()
        self.foldnEdit.clear()
        self.QAEdit.clear()
        return

class QAconfig:
    def __init__(self,drivename='GTiff',QAname='clearQA.tif',indexname='index.txt'):
        self.drivername=drivename
        self.QAname=QAname
        self.indexname=indexname

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex=qUfmask()
    sys.exit(app.exec_())
