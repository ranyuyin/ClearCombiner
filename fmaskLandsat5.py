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
def GlobArgv(Arcv):
    outlist=[]
    return outlist
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
def LandsatFmaskRoutine(MTLfile,toafile='toa.tif',themalfile='thermal.tif',
                        anglesfile='angles.tif',outfile='cloud.tif',
                        keepintermediates=False,verbose=False,
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
    saturationcheck.makeSaturationMask(fmaskConfig,'ref.tif','saturationmask.tif')
    fmask.fmaskFilenames.setSaturationMask('saturationmask.tif')
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
    fmask.doFmask(fmaskFilenames, fmaskConfig)
if __name__=='__main__':
    os.chdir('D:\\chang_Delta\\2010\\LT51200382010231BJC00')
    MTLfile=glob(os.path.join(os.getcwd(), '*MTL.TXT'))
    refMergeArgv=['-separate','-of','GTiff','-co','COMPRESSED=YES','-o','ref.tif','L*_B[1,2,3,4,5,7].TIF']
    refMergeArgv=GlobArgv(refMergeArgv)
    themalMergeArgv=['-separate','-of','GTiff','-co','COMPRESSED=YES','-o','thermal.tif','L*_B6.TIF']
    gdal_merge.main(refMergeArgv)
    gdal_merge.main(themalMergeArgv)
    mtlInfo = fmask.config.readMTLFile(MTLfile)
    imgInfo = fileinfo.ImageInfo('ref.tif')
    corners = landsatangles.findImgCorners('ref.tif', imgInfo)
    nadirLine = landsatangles.findNadirLine(corners)
    extentSunAngles = landsatangles.sunAnglesForExtent(imgInfo, mtlInfo)
    satAzimuth = landsatangles.satAzLeftRight(nadirLine)
    landsatangles.makeAnglesImage('ref.tif','angles.tif',nadirLine, extentSunAngles, satAzimuth, imgInfo)
    fmask.landsatTOA.makeTOAReflectance('ref.tif', MTLfile, 'angles.tif', 'toa.tif')
    LandsatFmaskRoutine(MTLfile)

