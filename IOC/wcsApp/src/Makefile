TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = wcs
# wcs.dbd will be created and installed
DBD += wcs.dbd

# wcs.dbd will be made up from these files:
wcs_DBD += base.dbd

# Include dbd files from all support applications:
#wcs_DBD += xxx.dbd

# Add all the support libraries needed by this IOC
#wcs_LIBS += xxx

ifdef EPICS_QSRV_MAJOR_VERSION
    wcs_LIBS += qsrv
    wcs_LIBS += $(EPICS_BASE_PVA_CORE_LIBS)
    wcs_DBD += PVAServerRegister.dbd
    wcs_DBD += qsrv.dbd
endif



# wcs_registerRecordDeviceDriver.cpp derives from wcs.dbd
wcs_SRCS += wcs_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
wcs_SRCS_DEFAULT += wcsMain.cpp
wcs_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#wcs_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries
wcs_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

