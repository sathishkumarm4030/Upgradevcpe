# Upgradevcpe
step1: install packages
below are the packages used in script.please install pkgs before running script or when facing error install
1) netmiko - https://github.com/sathishkumarm4030/netmiko_enhanced.git
2) textfsm
3) pandas
4) requests
5) json

install below packages
1) download netmiko pkg from github - git clone https://github.com/sathishkumarm4030/netmiko_enhanced.git
2) cd netmiko & run "python setup.py install"

step2: Update upgrade_device_list.xlsx for your devices

step3: run DoCpeUpgrade.py


after script run:

RESULT stored in RESULT.csv

device cmd output stored in PARSED_DATA FOLDER

SCRIPT LOGS stored in LOGS



