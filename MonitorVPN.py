"""
Name: VPN Monitor Script - V1.0
Objective: The purpose of this script is to ping accross VPN tunnel
            to remote server and verify VPN is forwarding traffic.
            If VPN does not forward traffic then reset VPN.
            Script will send 1 email if VPN down and 1 email after VPN
            comes back up.

Date: 05-28-2018
"""
__author__ = "Miguel Bonilla"
__version__ = "1.0"
__email__ = "miguel.bonilla@startek.com"
__status__ = "Development"

from netmiko import ConnectHandler
import logging
import re
import time
import os
import datetime
import shelve
import threading

class fw_process():

    def __init__(self, ip_address, vpnIP):
        self.ip_address =  ip_address
        self.vpnIP = vpnIP
        identity = [line.strip() for line in
                open("/home/mbonilla/scripts/.identity")]
        self.username = identity[0]
        self.passwd = identity[1]
        self.secret = identity[2]

    def connect(self):
        cisco_asa = {
            'device_type': 'cisco_asa',
            'ip': self.ip_address,
            'username': self.username,
            'password': self.passwd,
            'secret': self.secret,
            'verbose': False,
        }
        self.ssh_session = ConnectHandler(**cisco_asa)

    def disconnect(self):
        self.ssh_session.disconnect()

    def vpn_uptime(self):
        output = self.ssh_session.send_command_expect(
                "show vpn-sessiondb l2l filter name " + self.vpnIP + \
                " | i Duration")
        try:
            return(output.strip())
        except:
            return(False)
    
    def vpn_stats(self):
        output = self.ssh_session.send_command_expect(
                 "show vpn-sessiondb l2l filter name " + self.vpnIP)
        try:
            return(output.strip())
        except:
            return(False)

    def clear_vpn(self):
        output = self.ssh_session.send_command_expect(
        "clear ipsec sa peer " + self.vpnIP)
        return(output)


class core_process():

    def __init__(self, ip_address, targetHost):
        self.ip_address =  ip_address
        self.targetHost = targetHost
        identity = [line.strip() for line in
                open("/home/mbonilla/scripts/.identity")]
        self.username = identity[0]
        self.passwd = identity[1]
        self.secret = identity[2]
        self.re_success = re.compile(r'\((\d)\/(\d)+\)')

    def connect(self):
        cisco_ios = {
            'device_type': 'cisco_ios',
            'ip': self.ip_address,
            'username': self.username,
            'password': self.passwd,
            'verbose': False,
        }
        self.ssh_session = ConnectHandler(**cisco_ios)

    def ping(self):
        output = self.ssh_session.send_command(
                'ping ' + targetHost + ' source vlan 125 repeat 5')
        success_rate = self.re_success.search(output)
        try:
            result = (success_rate.group(1))
            return(result)
        except:
            pass

    def disconnect(self):
        self.ssh_session.disconnect()

logging.basicConfig(
    level=logging.WARNING,
    )



if __name__ == '__main__':

    coreIP = '10.236.0.252'
    fwIP = '10.229.192.75'
    vpnIP = '208.115.44.66'
    targetHost = '172.20.1.154'
    
    with shelve.open('vpn_status.db') as vpn_status:
        vpn_status = vpn_status['status']
        localtime_is_up = vpn_status['ifDown_Start']
        end_time = vpn_status['end_time']
        start_time = vpn_status['start_time']
        ping_success = vpn_status['start_time']
        vpn_uptime = vpn_status['VPN_Uptime']
        localtime_is_down = vpn_status['ifDown_End']
    
    print('VPN_STATUS - Values before new assignments: ')
    print(vpn_status)

    def core_connect(coreIP, targetHost):
        global ping_success
        global localtime_is_up
        global localtime_is_down
        global start_time
        global end_time
        SW_Session = core_process(coreIP, targetHost)
        try:
            SW_Session.connect()
            ping_success = SW_Session.ping()
            if int(ping_success) > 0:
                ping_success = True
                localtime_is_up = \
                              time.asctime(time.localtime(time.time()))
                start_time = \
                    datetime.datetime.now().time().strftime('%H:%M:%S')
            else:
                ping_success = False
                localtime_is_down = \
                    time.asctime(time.localtime(time.time()))
                end_time = \
                    datetime.datetime.now().time().strftime('%H:%M:%S')
        
            SW_Session.disconnect()
        except:
            print('Could not connect to ', coreIP)

    def fw_connect(fwIP, vpnIP):
        global vpn_uptime
        FW_Session = fw_process(fwIP, vpnIP)
        try:
            FW_Session.connect()
            vpn_uptime = FW_Session.vpn_uptime()
            FW_Session.disconnect()
        except:
            print('Could not connect to ', fwIP)
                   
                   
    core = threading.Thread(target=core_connect, \
           args=(coreIP,targetHost,))
    firewall = threading.Thread(target=fw_connect, args=(fwIP, vpnIP,))
    core.start()
    firewall.start()
    core.join()
    firewall.join()
        
    with shelve.open('vpn_status.db') as vpn_info:
        vpn_info['status'] = {
            'ifDown_Start': localtime_is_up,
            'end_time': end_time,
            'start_time': start_time,
            'Ping_Success': ping_success,
            'VPN_Uptime': vpn_uptime,
            'ifDown_End': localtime_is_down,
            'email_counter': 0,
            'VPN_Up': 0,
        }

    print('VPN STATUS after new assignments:\n')
    with shelve.open('vpn_status.db') as vpn_stored:
        print(vpn_stored['status'])
