import csv
from netmiko import ConnectHandler
import textfsm
import re
from netaddr import *

class VlanAudit:
    
    def __init__(self, ipaddress, hostname):
        '''initialize Core switches IPs'''
        self.ipaddress = ipaddress
        self.hostname = hostname
    
    def connect(self):
        '''Netmiko ConnectHandler dictionary'''
        IOS = {
            'device_type':'cisco_ios',
            'ip':self.ipaddress,
            'username':'swnetwork',
            'password':'C!$c0_Adm!n',
        }
        
        try:
            '''will try to SSH into core switch, if it fails then print 
                device's hostname it cannot connect'''
            self.net_connect = ConnectHandler(**IOS)
            print("Connected to {} with IP: {}".format(self.hostname, self.ipaddress))
        except:
            print("cannot connect to: {} with IP: {}".format(self.hostname, self.ipaddress))
    
    def disconnect(self):
        # disconnect from SSH session
        self.net_connect.disconnect()
        print("disconnected from: {} with IP: {}".format(self.hostname, self.ipaddress))
    
    def show_vlan(self):
        # run show vlan brief command
        self.showVlanBrief = self.net_connect.send_command_expect('terminal length 0')
        self.showVlanBrief = self.net_connect.send_command_expect('show vlan brief')
    
    def VlanList(self):
        #generate a list with VLANs into variable self.VlanItems
        self.VlanItems = []
        self.VlanElements = []
        with open(self.hostname + '.csv') as VlanList:
            self.VlanList = VlanList
            for line in VlanList:
                self.VlanElements.append(line.split(','))
                self.VlanItems.append(line.split(',')[1])
        with open(self.hostname + '_VlanInventory.csv', 'w+') as newCSVInventory:
            newCSVInventory.write('HOSTNAME' + ',' + 'VLAN_ID' + ',' + 'VLAN_Name' + ',' + \
                                   'IPAddress' ',' + 'Subnet' + ',' + 'CIDR' + ',' + '\n')
        self.getSubnet()
        
    def getSubnet(self):
        # run show run int vlan(X) to get vlan subnet
        for VlanId in self.VlanElements:
            self.VlanSubnet = self.net_connect.send_command(\
                              'show run int vlan' + VlanId[1] + ' | i ip address')
            self.subnet = self.VlanSubnet.split()
            # Verify IP address is IPv4 valid
            try:
                IPAddress(self.subnet[2]).version
            except: # if it is not an Network or a subnet then pass to next item
                continue
            # Information to generate new CSV 
            IPAdd = self.subnet[2]
            VLSM = self.subnet[3]
            CIDR = IPAddress(self.subnet[3]).netmask_bits()
            self.NewCSV(IPAdd, VLSM, CIDR, VlanId)
    
    def NewCSV(self, IPAdd, VLSM, CIDR, VlanId):
        #Test if we have valid IPv4 address before printing
        
        if IPAddress(IPAdd).version == 4:
            with open(self.hostname + '_VlanInventory.csv', 'a') as InventoryFile:
                InventoryFile.write(str(VlanId[0]) + ',' + str(VlanId[1]) + ',' + str(VlanId[2]) + ',' + \
                                    str(IPAdd) + ',' + str(VLSM) + ',' + str(CIDR) + '\n')

        
    def parseVlanOutput(self):
        """ get VLANs information by using textFSM library"""
        template = open('template.txtfsm')
        self.re_table = textfsm.TextFSM(template)
        self.fsmResult = self.re_table.ParseText(self.showVlanBrief)
    
    def generateCSV(self):
        # this method will write a csv file with Core Switch VLAN information
        outfileName = open(self.hostname + ".csv", 'w+')
        
        for s in self.re_table.header:
            outfileName.write("%s," % s)
        outfileName.write('\n')
        
        for row in self.fsmResult:
            outfileName.write("%s," % self.hostname)
            for s in row:
                if s != "":
                    outfileName.write("%s," % s)
            outfileName.write('\n')
            
class VlanAudit:
    
    def __init__(self, ipaddress, hostname):
        '''initialize Core switches IPs'''
        self.ipaddress = ipaddress
        self.hostname = hostname
    
    def connect(self):
        '''Netmiko ConnectHandler dictionary'''
        IOS = {
            'device_type':'cisco_ios',
            'ip':self.ipaddress,
            'username':'swnetwork',
            'password':'C!$c0_Adm!n',
        }
        
        try:
            '''will try to SSH into core switch, if it fails then print 
                device's hostname it cannot connect'''
            self.net_connect = ConnectHandler(**IOS)
            print("Connected to {} with IP: {}".format(self.hostname, self.ipaddress))
        except:
            print("cannot connect to: {} with IP: {}".format(self.hostname, self.ipaddress))
    
    def disconnect(self):
        # disconnect from SSH session
        self.net_connect.disconnect()
        print("disconnected from: {} with IP: {}".format(self.hostname, self.ipaddress))
    
    def show_vlan(self):
        # run show vlan brief command
        self.showVlanBrief = self.net_connect.send_command_expect('terminal length 0')
        self.showVlanBrief = self.net_connect.send_command_expect('show vlan brief')
    
    def VlanList(self):
        #generate a list with VLANs into variable self.VlanItems
        self.VlanItems = []
        self.VlanElements = []
        with open(self.hostname + '.csv') as VlanList:
            self.VlanList = VlanList
            for line in VlanList:
                self.VlanElements.append(line.split(','))
                self.VlanItems.append(line.split(',')[1])
        with open(self.hostname + '_VlanInventory.csv', 'w+') as newCSVInventory:
            newCSVInventory.write('HOSTNAME' + ',' + 'VLAN_ID' + ',' + 'VLAN_Name' + ',' + \
                                   'IPAddress' ',' + 'Subnet' + ',' + 'CIDR' + ',' + '\n')
        self.getSubnet()
        
    def getSubnet(self):
        # run show run int vlan(X) to get vlan subnet
        for VlanId in self.VlanElements:
            self.VlanSubnet = self.net_connect.send_command(\
                              'show run int vlan' + VlanId[1] + ' | i ip address')
            self.subnet = self.VlanSubnet.split()
            # Verify IP address is IPv4 valid
            try:
                IPAddress(self.subnet[2]).version
            except: # if it is not an Network or a subnet then pass to next item
                continue
            # Information to generate new CSV 
            IPAdd = self.subnet[2]
            VLSM = self.subnet[3]
            CIDR = IPAddress(self.subnet[3]).netmask_bits()
            self.NewCSV(IPAdd, VLSM, CIDR, VlanId)
    
    def NewCSV(self, IPAdd, VLSM, CIDR, VlanId):
        #Test if we have valid IPv4 address before printing
        
        if IPAddress(IPAdd).version == 4:
            with open(self.hostname + '_VlanInventory.csv', 'a') as InventoryFile:
                InventoryFile.write(str(VlanId[0]) + ',' + str(VlanId[1]) + ',' + str(VlanId[2]) + ',' + \
                                    str(IPAdd) + ',' + str(VLSM) + ',' + str(CIDR) + '\n')

        
    def parseVlanOutput(self):
        """ get VLANs information by using textFSM library"""
        template = open('template.txtfsm')
        self.re_table = textfsm.TextFSM(template)
        self.fsmResult = self.re_table.ParseText(self.showVlanBrief)
    
    def generateCSV(self):
        # this method will write a csv file with Core Switch VLAN information
        outfileName = open(self.hostname + ".csv", 'w+')
        
        for s in self.re_table.header:
            outfileName.write("%s," % s)
        outfileName.write('\n')
        
        for row in self.fsmResult:
            outfileName.write("%s," % self.hostname)
            for s in row:
                if s != "":
                    outfileName.write("%s," % s)
            outfileName.write('\n')
            
with open('CoreIPs.txt') as CoreSW:
    for line in CoreSW:
        SwInfo = line.split(',')
        IPAdd = SwInfo[1].strip()
        HostName = SwInfo[0].strip()
        Core = VlanAudit(IPAdd,HostName)
        Core.connect()
        Core.show_vlan()
        Core.parseVlanOutput()
        Core.generateCSV()
        Core.VlanList()
        Core.disconnect()