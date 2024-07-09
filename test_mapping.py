# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 15:47:29 2024

@author: AxelBaillet
"""

import subprocess
from sys import argv
import os
import logging
from time import sleep
import win32serviceutil
import win32service
import win32event
import servicemanager

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

def create_mapping_road(username, password,drive_letter, share_path):
    
    powershell_orders= f"""
    $user = '{username}'
    $securePassword = ConvertTo-SecureString '{password}' -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential ($user, $securePassword)
    New-PSDrive -Name {drive_letter} -PSProvider FileSystem -Root '{share_path}' -Credential $credential -Persist
    """
    powershell_command =  subprocess.run(["Powershell", "-Command", powershell_orders], capture_output=True, text=True)
    if powershell_command.stderr != '':
        logging.error('error on password')
        logging.error(powershell_command.stderr)
    sleep(10)
    return 




    
    # Lister les fichiers dans le répertoire

            
class cad_importer_client(win32serviceutil.ServiceFramework):
    _svc_name_ = "cad_test"
    _svc_display_name_ = "Import CAD Files"
    _svc_description_ = "Automates the import of CAD files from a network share."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        logger.info('Service started.')

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        logger.info('Service is stopping...')

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                               servicemanager.PYS_SERVICE_STARTED,
                               (self._svc_name_, ''))
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main()

    def main(self):
        
        # variable nécessaires au mapping
        
        server_ip = '192.168.0.3'
        share_name  = 'FastShare'
        share_path = fr'\\{server_ip}\{share_name}'
        username = ''
        password = ''
        drive_letter = 'Z'
        
        
        if not password:
            raise ValueError("the password cant be empty")
        
  
        create_mapping_road(username, password,drive_letter, share_path)
        
        return
        
if len(argv) == 1:
    servicemanager.Initialize()
    servicemanager.PrepareToHostSingle(cad_importer_client)
    servicemanager.StartServiceCtrlDispatcher()
else:
    win32serviceutil.HandleCommandLine(cad_importer_client)
    
    
    
# def check_mapping_existence(drive_letter): 
    
#     get_mappings_cmd = 'Get-PSDrive -PSProvider FileSystem | Format-Table -Property Name'
    
#     # Exécution de la commande PowerShell à travers subprocess
#     result = subprocess.run(["powershell.exe", "-Command", get_mappings_cmd], capture_output=True, text=True)
   
#     if result.returncode != 0:
#         logging.error("The program wont be able to access the file (mapping error):")
#         logging.error(result.stderr)
#         return None 
#     for k in result.stdout:
#         if k == drive_letter:
#             drive_letter = take_another_letter(drive_letter)
#     return drive_letter
   
# def take_another_letter(letter):
#     alphabet = ['O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
#     alphabet.pop(letter)
#     letter = alphabet(0)
#     return letter
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    