#!/bin/bash


PHOEBUS_PATH=/home/zhu/Phoebus/product-sns-4.6.10-SNAPSHOT



APWD=`pwd`
echo $APWD

gnome-terminal --window --title 'wcsIOC' -- bash -c 'cd ./IOC/iocBoot/iocwcs; ./st.cmd'

################### end #######################
#gnome-terminal --window -- sh -c 'echo 111; cd /home/zhu/EPICS/product-sns-4.6.10-SNAPSHOT;./phoebus.sh -resource "/home/zhu/SimCS/opi/wcs.bob"'
#用这种方式跑不起来

cd $PHOEBUS_PATH
./phoebus.sh -resource ${APWD}/opi/wcs.bob
