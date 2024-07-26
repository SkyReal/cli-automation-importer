# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 11:44:13 2024

@author: AxelBaillet
"""

import os
import json 
from subprocess import run 




def create_directory(directory, config_file_path):
    if not os.path.exists(directory):
        print('A directory called cli_automation_importer is created in program data \nIt will contains a log file "report"')
        os.makedirs(directory)
        return False
    else:
        return True
    
    
def create_config_file(config_file_path):
    if not os.path.exists(config_file_path):                # si le client n'a jamais ete installé
        print(' a config file is created. You will need to put the required informations in it')
        cad_importer_config_file  = {
            "path_cli": "C:\\SkyRealSuite\\1.18\\XRCenterCLI\\Skr.XRCenter.Cmd.exe",
            "ip_address_server": "value_to_fill",
            "share_path": "value_to_fill",
            "XRCENTER": "https://ip_adress:port/",
            "extensions": [".description", ".CATPart", ".CATProduct", ".CGR", ".CATProcess", ".model", ".3dxml", ".plmxml", ".jt", ".prt", ".asm", ".ifc", ".sldprt", ".sldasm", ".stp", ".step", ".stl", ".iam", ".ipt", ".x_t", ".dwg"]
            }
        with open(config_file_path, 'w') as file:
             json.dump(cad_importer_config_file, file, indent=4)            # on cree le config file
    return


def does_importer_exe_exists(service_program):
    if not os.path.exists(service_program):
        print('please, restart the installer with "cad_importer_client_service.exe" in the cli_automation_importer repertory (in program data)')
        return False
    else: 
        return True

def install_service(service_program):
    powershell_install_command = f'''
    New-service "cad_importer_client" -BinarypathName {service_program} -DisplayName "cad_importer_client" -startupType Automatic
    '''
    print(powershell_install_command)
    powershell_install = run([ "Powershell", "-Command",  powershell_install_command], capture_output=True, text=True)
    if powershell_install.returncode == 0:
        print('your windows service was created and will be active next time you turn on your computer')
        return True
    else:
        try:
            powershell_delete_command = '''
            sc.exe delete "cad_importer_client"
            '''
            powershell_install = run([ "Powershell", "-Command",  powershell_delete_command], capture_output=True, text=True)
        finally:
                powershell_install = run([ "Powershell", "-Command",  powershell_install_command], capture_output=True, text=True)
                if powershell_install.returncode == 0:
                    print('your windows service was created and will be active next time you turn on your computer')
                    return True
        return False 

def main():
    
    directory = r'C:\ProgramData\cli_automation_importer'
    config_file_path = os.path.join(directory, 'cad_importer_config_file.json')
    service_program = os.path.join(directory, 'cad_importer_client_service.exe')


    print('Warning : you have to run this program as an admin')
    
    create_directory(directory, config_file_path)             # creer le repertoire 
    
    if not does_importer_exe_exists(service_program):      # verifier que le .exe est dedans
        return 
    
    create_config_file(config_file_path)            # creer le config file
    
    if not install_service(service_program):            # installer le service windows
        return 
    
    
    return

main()