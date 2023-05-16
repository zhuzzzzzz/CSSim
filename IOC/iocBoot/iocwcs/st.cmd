#!../../bin/linux-x86_64/wcs

#- You may have to change wcs to something else
#- everywhere it appears in this file

< envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/wcs.dbd"
wcs_registerRecordDeviceDriver pdbbase

## Load record instances
#dbLoadRecords("db/wcs.db","user=zhu")
dbLoadTemplate "db/wcs.substitutions"

cd "${TOP}/iocBoot/${IOC}"
iocInit

## Start any sequence programs
#seq sncxxx,"user=zhu"
