"""
This Tool is designed for upgrading Versa CPE.
"""

__author__ = "Sathishkumar murugesan"
__copyright__ = "Copyright(c) 2018 Colt Technologies india pvt ltd."
__credits__ = ["Danny Pinto", "Anoop Jhon", "Pravin Karunakaran"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Sathishkumar Murugesan"
__email__ = "Sathishkumar.Murugesan@colt.net"
__status__ = "Developed"

import json
import logging.handlers
from datetime import datetime
from Utils import templates as t1
from Utils.Commands import *
from Utils.Variables import *
from netmiko import redispatch
import errno
import csv
import os

LOGFILE = "LOGS/upgrade_log_" + str(datetime.now()) + ".log"
logger = logging.getLogger("")
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=(1048576*5), backupCount=7)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


fileDir = os.path.dirname(os.path.realpath('__file__'))
cpe_details = os.path.join(fileDir, 'upgrade_device_list.xlsx')

interface_template = os.path.join(fileDir, 'TEXTFSM/versa_interface_template')
bgp_nbr_template = os.path.join(fileDir, 'TEXTFSM/versa_bgp_neighbor_template')
route_template = os.path.join(fileDir, 'TEXTFSM/versa_route_template')
show_config_template = os.path.join(fileDir, 'TEXTFSM/versa_show_config_template')


def write_result(results):
    data_header = ['cpe', 'upgrade', 'interface', 'bgp_nbr_match', 'route_match', 'config_match']
    with open('RESULT.csv', 'w') as file_writer:
        writer = csv.writer(file_writer)
        writer.writerow(data_header)
        for item in results:
            writer.writerow(item)
        for result1 in results:
            print "==" * 50
            for header, res in zip(data_header, result1):
                print header + ":" + res
            print "==" * 50


def write_output(results):
    write_output_filename = "PARSED_DATA/" + str(results[0][0]) + "_outputs.txt"
    data_header = ['cpe', 'before_upgrade_package_info', 'after_upgrade_package_info', 'before_upgrade_interface', 'after_upgrade_interface', 'before_upgrade_bgp_nbr_match', 'after_upgrade_bgp_nbr_match', 'before_upgrade_route_match', 'after_upgrade_route_match', 'before_upgrade_config_match', 'after_upgrade_config_match']
    if not os.path.exists(os.path.dirname(write_output_filename)):
        try:
            os.makedirs(os.path.dirname(write_output_filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(write_output_filename, "w") as f:
        for i, j in zip(data_header, results):
            print >> f, i
            print >> f, "===" * 50
            for idx, k in enumerate(j):
                    print >> f, k
            print >> f, "===" * 50


def cpe_upgrade():
    pl = read_excel_sheet(cpe_details, 'Sheet1')
    pl = pl.loc[pl['day'] == int(day)]
    report = []
    for i, rows in pl.iterrows():
        netconnect = make_connection(vd_ssh_dict)
        dev_dict = {
            "device_type": pl.ix[i, 'type'], "ip": pl.ix[i, 'ip'], \
            "username": pl.ix[i, 'username'], "password": pl.ix[i, 'password'], \
            "port": pl.ix[i, 'port']
        }
        cpe_name = pl.ix[i, 'device_name_in_vd']
        check_status = check_device_status(netconnect, cpe_name)
        if check_status != "PASS":
            print check_status
            cpe_result = [cpe_name, check_status]
            report.append(cpe_result)
            continue
        else:
            print cpe_name + " is in sync with VD & able to ping & connect"
        netconnect.write_channel("ssh " + dev_dict["username"] + "@" + dev_dict["ip"] + "\n")
        time.sleep(5)
        output = netconnect.read_channel()
        print output
        if 'assword:' in output:
            netconnect.write_channel(dev_dict["password"] + "\n")
        elif 'yes' in output:
            print "am in yes condition"
            netconnect.write_channel("yes\n")
            time.sleep(1)
            netconnect.write_channel(dev_dict["password"] + "\n")
        else:
            print "output"
            print "check reachabilty to " + dev_dict["ip"]
            continue
        netconnect.write_channel("cli\n")
        time.sleep(2)
        redispatch(netconnect, device_type='versa')
        parse1 = parse_send_command(netconnect, cmd1, interface_template)
        parse2 = parse_send_command(netconnect, cmd2, bgp_nbr_template)
        parse3 = parse_send_command(netconnect, cmd3, route_template)
        parse4 = parse_send_command(netconnect, cmd4, show_config_template)
        pack_info = get_package_info(netconnect)
        close_cross_connection(netconnect)
        close_connection(netconnect)
        if pack_info['PACKAGE_NAME'] == pl.ix[i, 'package_info']:
            print "REASON: device already running with same package"
            cpe_result = [cpe_name, "device already running with same package"]
            report.append(cpe_result)
            continue
        body_params = {
            'PACKAGE_NAME': pl.ix[i, 'package_name'],
            'DEVICE_NAME': pl.ix[i, 'device_name_in_vd']
        }
        body = config_template(t1.body_temp, body_params)
        json_data = json.loads(body)
        rest_result = rest_operation(vdurl, user, passwd, json_data)
        logging.info("Upgrade REST REQUEST : " + rest_result)
        # After Upgrade
        netconnect = make_connection(vd_ssh_dict)
        check_status = check_device_status(netconnect, cpe_name)
        if check_status != "PASS":
            print check_status
            cpe_result = [cpe_name, "After Upgrade, " + check_status]
            report.append(cpe_result)
            continue
        else:
            print "After upgrade " + cpe_name + " is in sync with VD & able to ping & connect"
        netconnect.is_alive()
        netconnect.write_channel("ssh " + dev_dict["username"] + "@" + dev_dict["ip"] + "\n")
        time.sleep(5)
        output = netconnect.read_channel()
        print output
        if 'assword:' in output:
            netconnect.write_channel(dev_dict["password"] + "\n")
        elif 'yes' in output:
            print "am in yes condition"
            netconnect.write_channel("yes\n")
            time.sleep(1)
            netconnect.write_channel(dev_dict["password"] + "\n")
        else:
            print "output"
            print "check reachabilty to " + dev_dict["ip"]
            continue
        netconnect.write_channel("cli\n")
        redispatch(netconnect, device_type='versa')
        time.sleep(2)
        parse5 = parse_send_command(netconnect, cmd1, interface_template)
        parse6 = parse_send_command(netconnect, cmd2, bgp_nbr_template)
        parse7 = parse_send_command(netconnect, cmd3, route_template)
        parse8 = parse_send_command(netconnect, cmd4, show_config_template)
        pack_info_after_upgrade = get_package_info(netconnect)
        close_cross_connection(netconnect)
        close_connection(netconnect)
        upgrade = check_parse(cpe_name, "package", pl.ix[i, 'package_info'], pack_info_after_upgrade['PACKAGE_NAME'])
        if upgrade == "OK":
            upgrade = "Success - " + str(pack_info['PACKAGE_NAME']) + " to " + pack_info_after_upgrade['PACKAGE_NAME']
        else:
            upgrade = "Failed"
        interface_match = check_parse(cpe_name, " interface ", parse1, parse5)
        bgp_nbr_match = check_parse(cpe_name, " bgp ", parse2, parse6)
        route_match = check_parse(cpe_name, " route ", parse3, parse7)
        config_match = check_parse(cpe_name, " running-config ", parse4, parse8)
        cpe_result = [cpe_name, upgrade, interface_match, bgp_nbr_match, route_match, config_match]
        cpe_parsed_data = [[cpe_name], [pack_info['PACKAGE_NAME']], [pack_info_after_upgrade['PACKAGE_NAME']], parse1, parse5, parse2, parse6, parse3, parse7, parse4, parse8]
        report.append(cpe_result)
        write_output(cpe_parsed_data)
    close_connection(netconnect)
    write_result(report)


def main():
    logging.info("SCRIPT Started")
    start_time = datetime.now()
    cpe_upgrade()
    print "SCRIPT Completed. Result Stored in RESULT.csv"
    print "Time elapsed: {}\n".format(datetime.now() - start_time)


if __name__ == "__main__":
    main()