# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 09:13:29 2017
#针对Landsat5应用python-fmask
@author: ranyu
"""
import os
from glob import glob
from fmask import landsatangles,saturationcheck,landsatTOA
import fmask,gdal
import numpy as np
from rios import fileinfo

def autofmask(dirname):
    os.chdir(dirname)
    if os.path.exists('cloud.img'):
        print('exist fmask, skip!')
        return
    MTLfile = glob(os.path.join(dirname, '*MTL.TXT'))
    refname=os.path.join(dirname,'ref.img')
    themalname=os.path.join(dirname,'thermal.img')
    if os.path.split(dirname)[-1][2]=='5':
        srcReflist=os.path.join(dirname,'L*_B[1,2,3,4,5,7].TIF')
        srcThemal=os.path.join(dirname,'L*_B6.TIF')
    elif os.path.split(dirname)[-1][2]=='7':
        srcReflist = os.path.join(dirname, 'L*_B[1,2,3,4,5,7].TIF')
        srcThemal = os.path.join(dirname, 'L*_B6_VCID_?.TIF')
    srcThemal=glob(srcThemal)
    srcReflist=glob(srcReflist)
    anglesname=os.path.join(dirname,'angles.img')
    toaname=os.path.join(dirname,'toa.img')
    # 合并文件
    if not os.path.exists(refname):
        LandsatBandMerge(srcReflist,refname,'HFA')
    else:
        print('跳过组合多光谱')
    if not os.path.exists(themalname):
        LandsatBandMerge(srcThemal, themalname, 'HFA')
    else:
        print('跳过组合热红外')
    # 生成角度文件
    # 读取文件信息
    MTLfile = MTLfile[0]
    mtlInfo = fmask.config.readMTLFile(MTLfile)
    if not os.path.exists(anglesname):
        imgInfo = fileinfo.ImageInfo(refname)
        corners = landsatangles.findImgCorners(refname, imgInfo)
        nadirLine = landsatangles.findNadirLine(corners)
        extentSunAngles = landsatangles.sunAnglesForExtent(imgInfo, mtlInfo)
        satAzimuth = landsatangles.satAzLeftRight(nadirLine)
        landsatangles.makeAnglesImage(refname, anglesname, nadirLine, extentSunAngles, satAzimuth, imgInfo)
    # 生成辅助临时文件：反射率
    if not os.path.exists(toaname):
        landsatTOA.makeTOAReflectance(refname, MTLfile, anglesname, toaname)
    print("begin this")
    LandsatFmaskRoutine(MTLfile)

def LandsatBandMerge(imlist,dstname,drivename=''):
    if drivename=='':
        drivename='GTiff'
    firsttime=1
    for bandindex in range(len(imlist)):
        bandfile=imlist[bandindex]
        Dataset=gdal.Open(bandfile)
        bandArray=Dataset.ReadAsArray(0,0,Dataset.RasterXSize,Dataset.RasterYSize)
        if firsttime:
            driver = gdal.GetDriverByName(drivename)
            dst_dataset = driver.Create(dstname, Dataset.RasterXSize,Dataset.RasterYSize, len(imlist), Dataset.GetRasterBand(1).DataType)
            im_geotrans=Dataset.GetGeoTransform()
            im_proj=Dataset.GetProjection()
            dst_dataset.SetGeoTransform(im_geotrans)
            dst_dataset.SetProjection(im_proj)
            firsttime=0
        dst_dataset.GetRasterBand(bandindex+1).WriteArray(bandArray)

def GetLandsatSensor(MTLfile):
    mtlInfo = fmask.config.readMTLFile(MTLfile)
    landsat = mtlInfo['SPACECRAFT_ID'][-1]

    if landsat == '4':
        sensor = fmask.config.FMASK_LANDSAT47
    elif landsat == '5':
        sensor = fmask.config.FMASK_LANDSAT47
    elif landsat == '7':
        sensor = fmask.config.FMASK_LANDSAT47
    elif landsat == '8':
        sensor = fmask.config.FMASK_LANDSAT8
    else:
        raise SystemExit('Unsupported Landsat sensor')
    return sensor

def GlobArgv(Argv):
    outList=[]
    for arg in Argv:
        expanded = glob(arg)
        if len(expanded) == 0:
            # not a file, just add the original string
            outList.append(arg)
        else:
            outList.extend(expanded)

    #outList = ' '.join(outList)
    return outList

def LandsatFmaskRoutine(MTLfile,toafile='toa.img',themalfile='thermal.img',
                        anglesfile='angles.img',outfile='cloud.img',
                        keepintermediates=False,verbose=True,
                        tempdir='.',mincloudsize=0,
                        cloudprobthreshold=100 * fmask.config.FmaskConfig.Eqn17CloudProbThresh,
                        nirsnowthreshold=fmask.config.FmaskConfig.Eqn20NirSnowThresh,
                        greensnowthreshold=fmask.config.FmaskConfig.Eqn20GreenSnowThresh,
                        cloudbufferdistance=300,shadowbufferdistance=300):#threshold的添加
    thermalInfo = fmask.config.readThermalInfoFromLandsatMTL(MTLfile)
    anglesInfo = fmask.config.AnglesFileInfo(anglesfile, 3, anglesfile, 2, anglesfile, 1, anglesfile, 0)
    mtlInfo = fmask.config.readMTLFile(MTLfile)
    sensor=GetLandsatSensor(MTLfile)
    fmaskFilenames = fmask.config.FmaskFilenames()
    fmaskFilenames.setTOAReflectanceFile(toafile)
    fmaskFilenames.setThermalFile(themalfile)
    fmaskFilenames.setOutputCloudMaskFile(outfile)
    fmaskConfig = fmask.config.FmaskConfig(sensor)
    saturationcheck.makeSaturationMask(fmaskConfig,'ref.img','saturationmask.img')
    fmaskFilenames.setSaturationMask('saturationmask.img')
    fmaskConfig.setThermalInfo(thermalInfo)
    fmaskConfig.setAnglesInfo(anglesInfo)
    fmaskConfig.setKeepIntermediates(keepintermediates)
    fmaskConfig.setVerbose(verbose)
    fmaskConfig.setTempDir(tempdir)
    fmaskConfig.setMinCloudSize(mincloudsize)
    fmaskConfig.setEqn17CloudProbThresh(cloudprobthreshold / 100)  # Note conversion from percentage
    fmaskConfig.setEqn20NirSnowThresh(nirsnowthreshold)
    fmaskConfig.setEqn20GreenSnowThresh(greensnowthreshold)
    toaImgInfo = fileinfo.ImageInfo(toafile)
    fmaskConfig.setCloudBufferSize(int(cloudbufferdistance / toaImgInfo.xRes))
    fmaskConfig.setShadowBufferSize(int(shadowbufferdistance / toaImgInfo.xRes))
    fmask.fmask.doFmask(fmaskFilenames, fmaskConfig)

def walkfmask(dirname,pbar):
    subfoldlist = os.listdir(dirname)
    subfoldlist = [os.path.join(dirname, i) for i in subfoldlist if os.path.isdir(os.path.join(dirname, i))]
    pbar.setRange(0,2*len(subfoldlist))
    pbar.setValue(0)
    for subdirname in subfoldlist:
        autofmask(subdirname)
        pbar.setValue(pbar.value()+1)

def walkclearQA(dirname,pbar,QAconfig):
    srcdatasetList=getFmasklist(dirname,QAconfig)
    os.chdir(dirname)
    (dstdataset,gaindiclist)=unionGeo(srcdatasetList,QAconfig)
    clearQA=np.zeros((dstdataset.RasterYSize, dstdataset.RasterXSize))
    for i in range(len(srcdatasetList)):
        thisfmask = srcdatasetList[i].ReadAsArray()
        thisfmask = ((thisfmask == 1)|(thisfmask == 4) | (thisfmask == 5))
        thisfmask = np.pad(thisfmask, gaindiclist[i],'constant',constant_values=False)
        clearQA=clearQA+thisfmask*(2**i)
        pbar.setValue(pbar.value() + 1)
    dstdataset.GetRasterBand(1).WriteArray(clearQA)
    return

def getFmasklist(rootdir,QAconfig):
    fmasklist=[]
    filenamelist=os.listdir(rootdir)
    subfoldlist = [os.path.join(rootdir, i) for i in filenamelist if os.path.isdir(os.path.join(rootdir, i))]
    subfoldlist = sorted(subfoldlist, key=lambda d: float(os.path.split(d)[-1][9:15]))
    f=open(os.path.join(rootdir, QAconfig.indexname), 'w')
    strsubfoldlist='\r\n'.join(subfoldlist)
    #f.write(filenamelist)
    f.writelines(strsubfoldlist)
    #print filename
    for subdirname in subfoldlist:
        #subdirname=dirname+'\\'+fn
        subdirname=os.path.join(rootdir, subdirname, 'cloud.img')
        dataset=gdal.Open(subdirname)
        fmasklist.append(dataset)
    return fmasklist

def unionGeo(srcdatasetList, QAconfig):
    extentlist=np.zeros((len(srcdatasetList),4))
    for i in range(len(srcdatasetList)):
        trans=srcdatasetList[i].GetGeoTransform()
        extentlist[i,:]=[trans[3],
                         trans[3] + (srcdatasetList[i].RasterYSize-1) * trans[5],
                         trans[0],
                         trans[0] + (srcdatasetList[i].RasterXSize-1) * trans[1]]
    uExtent=[max(extentlist[:,0]),
             min(extentlist[:,1]),
             min(extentlist[:,2]),
             max(extentlist[:,3]),
             ]
    deltaExtent=np.abs(extentlist-uExtent)
    #暂时只处理横竖分辨率相同的情况
    uGeotransform=srcdatasetList[0].GetGeoTransform()
    gaindiclist=(deltaExtent/uGeotransform[1]).astype('int16')
    gaindiclist=[
        [(gaindiclist[i,0],gaindiclist[i,1]),
        (gaindiclist[i,2],gaindiclist[i,3])]
        for i in range(len(gaindiclist))]
    uGeotransform=list(uGeotransform)
    uGeotransform[0]=uExtent[2]
    uGeotransform[3]=uExtent[0]
    uGeotransform=tuple(uGeotransform)
    a = np.array([[uGeotransform[1], uGeotransform[2]], [uGeotransform[4], uGeotransform[5]]])
    b = np.array([uExtent[3] - uGeotransform[0], uExtent[1] - uGeotransform[3]])
    (pixel, line)=np.linalg.solve(a, b)
    uSizeX=pixel+1
    uSizeY=line+1
    #print ('union size: %d,%d'%(uSizeX,uSizeY))
    driver = gdal.GetDriverByName(QAconfig.drivername)
    if (len(srcdatasetList)/8)==0:
        bitformat=gdal.GDT_Byte
    elif (len(srcdatasetList)/8)==1:
        bitformat = gdal.GDT_Int16
    dstgeo=driver.Create(QAconfig.QAname, int(uSizeX),int(uSizeY),1,bitformat)
    return (dstgeo,gaindiclist)

if __name__=='__main__':
    autofmask('D:\\chang_Delta\\2010\\LT51200382010231BJC00')