# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 09:13:29 2017
#针对Landsat5应用python-fmask
@author: ranyu
"""
import os
from glob import glob
from fmask import landsatangles,saturationcheck
import fmask
import gdal_merge
from rios import fileinfo
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
def LandsatFmaskRoutine(MTLfile,toafile='toa.img',themalfile='thermal.img',
                        anglesfile='angles.img',outfile='cloud.img',
                        keepintermediates=False,verbose=True,
                        tempdir='.',mincloudsize=0,
                        cloudprobthreshold=100 * fmask.config.FmaskConfig.Eqn17CloudProbThresh,
                        nirsnowthreshold=fmask.config.FmaskConfig.Eqn20NirSnowThresh,
                        greensnowthreshold=fmask.config.FmaskConfig.Eqn20GreenSnowThresh,
                        cloudbufferdistance=300,shadowbufferdistance=300):
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

def autofmask(dirname):
    os.chdir(dirname)
    MTLfile = glob(os.path.join(dirname, '*MTL.TXT'))
    refname=os.path.join(dirname,'ref.img')
    themalname=os.path.join(dirname,'thermal.img')
    srcReflist=os.path.join(dirname,'L*_B[1,2,3,4,5,7].TIF')
    srcReflist=glob(srcReflist)
    srcThemal=os.path.join(dirname,'L*_B6.TIF')
    srcThemal=glob(srcThemal)
    anglesname=os.path.join(dirname,'angles.img')
    toaname=os.path.join(dirname,'toa.img')
    # 合并文件
    refMergeArgv = ['', '-separate', '-of', 'HFA', '-co', 'COMPRESSED=YES', '-o', refname]
    refMergeArgv.extend(srcReflist)
    themalMergeArgv = ['', '-separate', '-of', 'HFA', '-co', 'COMPRESSED=YES', '-o',themalname]
    themalMergeArgv.extend(srcThemal)
    if not os.path.exists(refname):
        gdal_merge.main(refMergeArgv)
    else:
        print('跳过组合多光谱')
    if not os.path.exists(themalname):
        gdal_merge.main(themalMergeArgv)
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
        fmask.landsatTOA.makeTOAReflectance(refname, MTLfile, anglesname, toaname)
    print("begin this")
    LandsatFmaskRoutine(MTLfile)
def walkfmask(dirname):
    subfoldlist = os.listdir(dirname)
    subfoldlist = [os.path.join(dirname, i) for i in subfoldlist if os.path.isdir(os.path.join(dirname, i))]
    for subdirname in subfoldlist:
        autofmask(subdirname)
if __name__=='__main__':
    autofmask('D:\\chang_Delta\\2010\\LT51200382010231BJC00')


