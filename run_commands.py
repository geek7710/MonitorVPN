import os
from netmiko import ConnectHandler
from time import time
from napalm import get_network_driver
from multiprocessing.dummy import Pool as ThreadPool
import csv
import logging

Script_Start = time()
DeviceList = []
with open('/home/mbonilla/Devel/libertyVPN_reset/Change_Commands/Jamaica.csv') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        DeviceList.append((row[0].strip(),row[1].strip()))

""" Load show commands or configuration changes commands """
with open('/home/mbonilla/Devel/libertyVPN_reset/Change_Commands/commands.txt', 'r') as f:
    commands_list = f.read().splitlines()


class SSH:
    """ SSH WAN Routers """
    def __init__(self, ipaddress, routername):
        self.ipaddress = ipaddress
        self.routername = routername
        identity = [line.strip() for line in open(
                                            '/home/mbonilla/scripts/.identity')]
        self.username = identity[0]
        self.passwd = identity[1]
        self.enable = identity[2]
        
        self.srtCisco = {
            'device_type': 'cisco_ios',
            'ip': self.ipaddress,
            'username': self.username,
            'password': self.passwd,
            'verbose': False,
        }
        

    def connect(self):
        try:
            self.sshinstance = ConnectHandler(**self.srtCisco)
            print("Connected to {}".format(self.routername))
        except:
            with open(
                '/home/mbonilla/Devel/libertyVPN_reset/Change_Commands/Failed_Execute_Command_Script.txt',
                'a') as f:
                f.write(self.routername + ',' + self.ipaddress + '\n')
            
    def disconnect(self):
        self.sshinstance.disconnect()
        print("Disconnected from {}".format(self.routername))
         
    def config_change_commands(self, commands_list):
        #this method will send list of config changes
        self.configChangeOutput = self.sshinstance.send_config_set(commands_list)
        print(self.configChangeOutput)
    
    def send_show_commands(self):
        #this method will send list of show commands
        self.configChangeOutput = self.sshinstance.send_command_expect('show ver | i uptime')
        print(self.configChangeOutput)
    
    def save_ios_config(self):
        #save config changes on device
        self.sshinstance.send_command_expect('write mem')
    
    def save_configChange(self):
        #save configuration changes and log output
        os.chdir(
            '/home/mbonilla/Devel/libertyVPN_reset/Change_Commands')
        
        if not os.path.exists(self.routername):
            os.makedirs(self.routername)
            
        elif os.path.exists(self.routername + '/' + self.routername + '_config_output.txt'):
            pass
        
        else:
            with open(self.routername + '/' + self.routername + '_config_output.txt', 'w') as configfile:
                for line in self.configChangeOutput:
                    configfile.write(line)
 

def worker(DeviceList):
    ipaddress = DeviceList[1]
    routername = DeviceList[0]
    
    ios_ssh = SSH(ipaddress, routername)
    try:
        ios_ssh.connect()
        if ios_ssh:
            #ios_ssh.config_change_commands(commands_list)
            ios_ssh.send_show_commands()
            #ios_ssh.save_ios_config()
            ios_ssh.disconnect()
    except:
        with open(
            '/home/mbonilla/Devel/libertyVPN_reset/Change_Commands/Failed_Execute_Command_Script.txt',
            'a') as f:
            f.write(self.routername + ',' + self.ipaddress + '\n')


logging.basicConfig(
    level=logging.WARNING,
    )

threads = ThreadPool( 10 )
results = threads.map( worker, DeviceList )

threads.close()
threads.join()
print('\n---- Number of devices: ',len(DeviceList) )
print('\n---- End get config threadpool, elapsed time= {:.2} min'.format((time()- Script_Start)/60))