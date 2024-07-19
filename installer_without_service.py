# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 11:11:23 2024

@author: AxelBaillet
"""

import os 
import json 

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
            "ip_address_XRCENTER": "value_to_fill"
        }
        with open(config_file_path, 'w') as file:
             json.dump(cad_importer_config_file, file, indent=4)            # on cree le config file
    return

def main():
    
    directory = r'C:\ProgramData\cli_automation_importer'
    config_file_path = os.path.join(directory, 'cad_importer_config_file.json')

    create_directory(directory, config_file_path)             # creer le repertoire 
    
    
    create_config_file(config_file_path)            # creer le config file
    
    return

main()