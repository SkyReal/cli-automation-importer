# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 10:39:01 2024

@author: AxelBaillet
"""

import socket 
from subprocess import run 
from time import sleep
import argparse
from struct import pack




PING_NUMBER = 20 




def get_ethernet_mac_address():
    # Exécute la commande PowerShell pour obtenir les adaptateurs réseau
    command = 'powershell "Get-NetAdapter | Format-Table -Property Name, MacAddress -AutoSize"'
    result = run(command, capture_output=True, text=True, shell=True)
    
    # Traiter la sortie pour trouver l'adresse MAC de l'adaptateur Ethernet
    lines = result.stdout.split('\n')
    for line in lines:
        if 'Ethernet' in line:
            # Extraire l'adresse MAC (elle se trouve après le nom de l'adaptateur)
            parts = line.split()
            # name = parts[0]
            mac_address = parts[1]
            return mac_address


def ping_until_answer(ip_address, ping_result):
    global PING_NUMBER
    x = 0
    while x < PING_NUMBER:
        if ip_address == socket.gethostbyname(socket.gethostname()):
            x  = PING_NUMBER
            ping_result = True 
            return ping_result 
        else:
            powershell_ping_result = run(['ping', '-n', '1', ip_address], capture_output=True, text=True)
            if powershell_ping_result.returncode == 0:
                print('the client just reached the host computer ( ping command was successful ) ')
                ping_result = True 
                return ping_result                                      # on a reussi a pinger le server
            x += 1                                                      # on passe à l'essai suivant
            print('Ping command was not successful. Still trying to connect')
            sleep(5)                                                    #  laisser le temps entre deux essais
    ping_result =False                                                  # commande a priori inutile mais on ne sait jamais ( le ping result est par defaut False)
    return ping_result 


def send_mac_address(client_socket, mac_address):
    mac_address_bytes=  mac_address.encode('utf-8')
    message_length = pack('!I', len(mac_address_bytes))
    client_socket.sendall(message_length + mac_address_bytes)
    return 

def send_computer_name(client_socket, computer_name):
    computer_name_bytes =  computer_name.encode('utf-8')
    message_length = pack('!I', len(computer_name_bytes))
    client_socket.sendall(message_length + computer_name_bytes)
    return 


def main():
    
    parser = argparse.ArgumentParser(description = 'Process the arguments')                     # va gerer les differents arguments
    parser.add_argument('--IP_host', type = str, help = 'You have to put the ip of the computer you that will store the mac addresses in a file', required = True)  #le nom du fichier excel
    
    args = parser.parse_args()  # parcourir les differents arguments
    
    IP_address_host =  args.IP_host                            
    
    connected = False
    ping_result = False 
    x = 0 
    computer_name = socket.gethostname()
    # se connecter au serveur 
    
    ping_result = ping_until_answer(IP_address_host, ping_result)
    
    if not ping_result:
        print('error while pinging the computer')
        return
    
    while x < 12 and not connected :                          # 1 minute    
        try:
            print('Attempting to connect')
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            address_host= (IP_address_host, 3000)      # l'adresse du serveur host
            client_socket.connect(address_host)        # si le serveur est bien connecté   
            connected = True
        except socket.error:
            x +=1
            sleep(5)
            
            
    mac_address = get_ethernet_mac_address()
    
    send_computer_name(client_socket, computer_name)
    
    print('Computer name sent')
    
    sleep(1)
    
    send_mac_address(client_socket, mac_address)
    
    print('Mac address sent')
    
    print('the client will close now ')
    
    sleep(10)
    
    client_socket.close()
    
    return


main()


















