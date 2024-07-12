# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 15:47:29 2024

@author: AxelBaillet
"""

from subprocess import run
import os
import logging
from time import sleep

log_directory = r'C:\ProgramData\cli_automation_importer'
log_file_path = os.path.join(log_directory, 'report.log')

if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    level=logging.DEBUG,                                     # on affichera les messages de gravite minimale 'info'
    format='%(asctime)s - %(levelname)s - %(message)s',     # le format des messages affiches 
    handlers=[logging.FileHandler(log_file_path, mode = 'w'),logging.FileHandler("smbprotocol_debug.log"), logging.StreamHandler()]   # le path du fichier ou seront ecrites les erreurs de debogage
)

logger = logging.getLogger('logger')        #initialisation du logger

def create_mapping_road(username, password, drive_letter, share_path):
    
    powershell_drive_existence  = f"""
    if (Get-PSDrive -Name '{drive_letter}' -ErrorAction SilentlyContinue) {{
            net use '{drive_letter}' /delete 
    }}
    """
    
    powershell_identification_orders= f"""
    $user = '{username}'
    $securePassword = ConvertTo-SecureString '{password}' -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential ($user, $securePassword)
    """
    
    powershell_new_driver = f"New-PSDrive -Name '{drive_letter}' -PSProvider FileSystem -Root '{share_path}' -Credential $credential -Persist -Scope Global"
    
    
    print( 'powershell_identification_orders', powershell_identification_orders)
    print(powershell_new_driver)
    
    
    powershell_command_existence = run(["Powershell", "-Command",  powershell_drive_existence], capture_output=True, text=True)
    if powershell_command_existence.stderr != '':
        print('unidentified error')
        print(powershell_command_existence.stderr)
        
        
    powershell_command_1 = run(["Powershell", "-Command",  powershell_identification_orders], capture_output=True, text=True)
    if powershell_command_1.stderr != '':
        print('error on password')
        print(powershell_command_1.stderr)
        return False
    
    powershell_command_2 = run(["Powershell", "-Command",  powershell_new_driver], capture_output=True, text=True)
    if powershell_command_2.stderr != '':
        print('error on driver')
        print(powershell_command_2.stderr)
        return False
    
    sleep(10)
    
    return True




def main():
    
    # variable nécessaires au mapping
    
    server_ip = '192.168.0.3'
    share_name  = 'FastShare'
    share_path = fr'\\{server_ip}\{share_name}'
    username = input ('username :')
    password = input('password: ')
    drive_letter = 'Z'
    
    
    if not password:
        raise ValueError("the password or username can not be empty")
    
  
    create_mapping_road(username, password,drive_letter, share_path)
    
    return
    
main()