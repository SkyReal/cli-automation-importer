# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 16:53:35 2024

@author: AxelBaillet
"""


import win32serviceutil
import win32service
import win32event
import servicemanager

import os 
from pathlib import Path
import socket 
from time import time 
from time import sleep
from subprocess import run 
from json import load
from ipaddress import ip_address, AddressValueError
import logging
from sys import argv
from struct import unpack

IDLE_TIME_OUT = 300     # temps en secondes pour lequel le programme s'arrete
PING_NUMBER = 20 



# on va repertorier les erreurs dans un journal

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


# Mapping du reseau

def create_mapping_road(username, password, drive_letter, share_path):
    
    powershell_identification_orders= f"""
    $user = '{username}'
    $securePassword = '{password}'
    $pass = ConvertTo-SecureString $securePassword -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential ($user, $pass)
    $credential
    New-SMbGlobalMapping -RemotePath '{share_path}' -Credential $credential -LocalPath G:
    """
   
    try:
        powershell_command_1 = run([ "Powershell", "-Command",  powershell_identification_orders], capture_output=True, text=True)
        logger.info('You can map your files')
    except Exception as e:
        logger.info("error is :", e)
        #if powershell_command_1.stderr != '':
        logger.info('error on password')
        logger.info(powershell_command_1)
        logger.info("ERRORS : ")
        logger.info(powershell_command_1.stderr)
        return False

    return True


def find_config_files_path():
   #le config file est toujours au meme endroit 
   if not os.path.exists("C:\ProgramData\cli_automation_importer"):         # destiné a etre supprime avec l'installeur
       logger.info('do you have your config file?')
       return ''
   else:
       config_file_path = "C:\ProgramData\cli_automation_importer\cad_importer_config_file.json"
   return config_file_path

def get_config_files_datas(path_CLI_local, JSON_file ):
    if JSON_file.lower().endswith('.json'):          # on vérifie qu'on nous donne un json
        pass 
    else :
        logger.info("The config file is not a json file")
        return None
    file = open(JSON_file, 'r')
    config_files_dictionnaire = load(file)                                     #on convertit le json en dictionnaire 
    path_CLI_local = config_files_dictionnaire["adresse_cli"] 
    if (path_CLI_local == None): 
        logger.info(' adress_xrcenter is missing in the config file.')
        return None
    file.close
    return path_CLI_local
        
def more_config_file_datas(share_path, JSON_file):      # a executer apres  get_config_files_datas
    with open(JSON_file, 'r') as file: 
        config_files_dictionnaire = load(file)   
        share_path = config_files_dictionnaire["share_path"]     
    if share_path == '':
        logger.info(' the share path must be \\\\"IP_address"\\"share_name", dont forget to double your backslashes as you are working with a json')
    return share_path

def verif_CLI(path_CLI_local):
    if not os.path.exists(path_CLI_local):
        logger.info('You need to write the correct local path of your cli in the config file')
        return False
    commande_CLI_opti1= f'& "{path_CLI_local}" health ping'
    CLI_ope = run(["Powershell", "-Command", commande_CLI_opti1], capture_output=True, text=True)
    if 'success' in CLI_ope.stdout.lower():                                #le XRCENTER se lance avec le chemin basique 
        logger.info("CLI functional")
    else:                                                                       #on fait l'opération avec les paramètres que l'utilisateur a inséré
        logger.info("Error : Is your XRCenter activated?")
        stdout = CLI_ope.stdout
        logger.info(f"stdout :  {stdout}")
        return False
    return True

def import_CAD_file(time_record, save_id_workspace, path_CLI_local, file):
    logger.info(f'your file "{file}" is sent in SkyReal')
    commande_fichier_import= f'& "{path_CLI_local}"  cad import "{save_id_workspace}" "{file}"' #commande pour importer sur le deck
    start = time()
    import_final = run(["Powershell", "-Command", commande_fichier_import], capture_output=True, text=True)
    end = time()
    time_record= end - start                                                                           # on mesure le temps de chaque import
    if "failed" in import_final.stdout.lower() or "error" in import_final.stdout.lower():
            logger.info(f' \n the file "{file}" cant be put in SkyReal \n ')   
            time_record= -1             # l'import a echoue
    else:
        logger.info(f'your file "{file}" is in SkyReal')
    return time_record


##  COTE SERVEUR CLIENT

## on va d'abord pinger le serveur jusqu'a avoir une reponse 

def ping_until_answer(ip_address):
    global PING_NUMBER
    x = 0
    while x < PING_NUMBER:
        powershell_ping_result = run(['ping', '-c', '1', ip_address], capture_output=True, text=True)
        
        if powershell_ping_result.returncode == 0:
            logger.info('the client just reached the host pc ( ping command was successful')
            return True# on a reussi a pinger le server
         
        x += 1 # on passe à l'essai suivant
        logger.info(powershell_ping_result.returncode)
        sleep(5)    # laisser le temps entre deux essais
    logger.info(' The client was not able to reach the host computer ( no answer )')
    return False 
        
    
def verif_IP_address(ip_address_host):               # verifier la validite de l'adresse ip du host
    try:
       ip_address(ip_address_host)
       logger.info('Warning : make sure to verify that the IP adress in the json file is the one of your host computer, or the program wont work')
       return True
    except AddressValueError:
        logger.warning('your ipadress is not valid')
        return False
    
    
def get_IP_address(JSON_file):
        file = open(JSON_file, 'r')
        config_files_dictionnaire = load(file)     
        IP_address = config_files_dictionnaire["adresse_ip_server"] 
        if IP_address == '' or IP_address == None:
            logger.warning('Did you put the right IP_address in the config file ?')
            return False
        return IP_address
    
def get_mapping_username(client_socket, mapping_username):
    try: 
        id_length = client_socket.recv(4)                                             # longeur de l'id workspace
        received_id_length = unpack('!I', id_length)[0]                               # traduit de binaire a string
        sleep(3)
        logger.info(f'received_mapping_username_length "{received_id_length}"')
        mapping_username_bytes = client_socket.recv(received_id_length)                   # le fichier arrive en binaire, normalement sans erreur si il est apres select()        
        mapping_username =mapping_username_bytes.decode('utf-8')                             # on le retransforme en string
        logger.info(f' mapping_username "{mapping_username}"')
        sleep(3)
    except socket.error as e:
        logger.warning('connexion error', e)
        return ''
    except Exception:
        logger.warning('an error has occured, please try again')
        return ''
    return mapping_username  

def get_mapping_password(client_socket, mapping_password):
    try: 
        id_length = client_socket.recv(4)                                             # longeur de l'id workspace
        received_id_length = unpack('!I', id_length)[0]                               # traduit de binaire a string
        sleep(3)
        logger.info(f'received_password_length "{received_id_length}"')
        mapping_password_bytes = client_socket.recv(received_id_length)                   # le fichier arrive en binaire, normalement sans erreur si il est apres select()        
        mapping_password = mapping_password_bytes.decode('utf-8')                             # on le retransforme en string
        sleep(3)
        logger.info('mapping_password')
    except socket.error as e:
        logger.warning('connexion error', e)
        return ''
    except Exception:
        logger.warning('an error has occured, please try again')
        return ''
    return mapping_password  
     
        
def get_ID_workspace(client_socket, id_workspace):
    try: 
        id_length = client_socket.recv(4)                                             # longeur de l'id workspace
        received_id_length = unpack('!I', id_length)[0]                               # traduit de binaire a string
        sleep(1.5)
        logger.info(f'received_id_length "{received_id_length}"')
        id_workspace_bytes = client_socket.recv(received_id_length)                   # le fichier arrive en binaire, normalement sans erreur si il est apres select()        
        id_workspace = id_workspace_bytes.decode('utf-8')                             # on le retransforme en string
        sleep(1)
        logger.info(f'id_workspace "{id_workspace}"')
    except socket.error as e:
        logger.warning('connexion error', e)
        return ''
    except Exception:
        logger.warning('an error has occured, please try again')
        return ''
    return id_workspace  

        
def use_data(client_socket, time_record, id_workspace, path_CLI_local):
    try:
        file_to_receive_bytes = client_socket.recv(4096)            # le fichier arrive en binaire, normalement sans erreur si il est apres select()
        file_to_receive= file_to_receive_bytes.decode('utf-8')          # on le retransforme en string
        if file_to_receive == 'close':     
            logger.info('the client will close now')                                # on arrete le programme
            return False
        logger.info(f'file_to_receive "{file_to_receive}"')
    # ce que le serveur doit faire
        check_existence = Path(file_to_receive)
        logger.info(f'check_existence {check_existence}')
        if not check_existence.exists():                           # On considere que si un seul fichiers n'est pas present sur le pc, le repertoire n existe pas du tout et on ferme ce client
            logger.warning('the CAD file can not be found on this computer. You must be able to access it. This client will close') 
            return False
        
        time_record = import_CAD_file(time_record, id_workspace, path_CLI_local, file_to_receive)
        
    # envoyer les resultats
        time_record_byte = str(time_record).encode()          # on traduit le float en chaine de caractere que l'on met en bytes
        client_socket.send(time_record_byte)
    except KeyboardInterrupt:
        return False
    return True
        

def verif_connexion_to_host(client_socket, adress_host):
    global IDLE_TIME_OUT 
    connected = False
    time_before_disconnecting = 0
    while not connected and time_before_disconnecting < IDLE_TIME_OUT :         # 10 minutes d'attentes max
        try:
            client_socket.connect(adress_host)        # si le serveur est bien connecté   
            logger.info('the client was successfuly connected')
            connected = True 
        except socket.error:
           sleep(5)
           logger.info(f'waiting for a host server, remaining time before disconnection : "{IDLE_TIME_OUT - time_before_disconnecting}"')
           time_before_disconnecting += 5
    if not connected:
        logger.info('Failed to connect to the server after 5 minutes.')
        client_socket.close()  # Fermer le socket si la connexion échoue
        return False
    return True


class cad_importer_client(win32serviceutil.ServiceFramework):
    _svc_name_ = "cad_importer_client"
    _svc_display_name_ = "import your CAD file in a defined XRCenter"
    _svc_description_ = "By connecting with a server, this service takes the path of Cad files and import them"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        logger.info('info')

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        
        # Logique de service
        self.main()

        # Service en arrêt
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)

    def main(self):
        
         # attendre que le programme demarre
         
        sleep(10)
        
        # initialiser les variables
        
        IP_address_host = ''
        id_workspace = ''
        time_record= 0.0
        path_CLI_local = None
        share_path = ''

         
        # variable nécessaires au mapping
        
        mapping_username = ''
        mapping_password = ''
        drive_letter = 'Z'
        
        
        # verifications des variables 
        
        JSON_file = find_config_files_path()  # le path du json 
        
        if JSON_file == '':
            logger.info('Is your config file next to your client program?')
            return
        
        path_CLI_local = get_config_files_datas(path_CLI_local, JSON_file )      # on prend le path CLI
        share_path = more_config_file_datas(share_path, JSON_file)              # on prend le path du partage
        
        # obtenir l'adresse ip 
        
        IP_address_host=  get_IP_address(JSON_file)
        
        # verifier la validité de l'adresse ip
        
        if not verif_IP_address( IP_address_host):
            return 
        
        # pinger le pc host
        
        if not ping_until_answer(IP_address_host):
            return 
        
        # verifier la validité de la CLI et du XRCenter
        
        if verif_CLI(path_CLI_local) == False:
            return
                 
        # se connecter au serveur 
           
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        adress_host= (IP_address_host, 3000)      # l'adresse du serveur host
        
        
        if verif_connexion_to_host(client_socket, adress_host) == False:          # verifier si on est bien connecté sinon attendre
            return 
        
        sleep(10) 
        
        # d'abord on lui transfere le username et le password 
        
        mapping_username = get_mapping_username(client_socket, mapping_username)
        
        mapping_password = get_mapping_password(client_socket, mapping_password)
            
        # mapping du reseau 
        
        if not create_mapping_road(mapping_username, mapping_password ,drive_letter, share_path):
            logger.info("error on mapping")
            return
        
        # en premier lieu, on lui transfere l'ID du workspace
        
        id_workspace = get_ID_workspace(client_socket, id_workspace)
        
        if id_workspace == '':                  # on ferme le serveur si il y a une erreur 
            client_socket.close()
            return 
        
        # effectuer les imports 
        
        logger.info('starting the import program')
        while True:
            try: 
               if not use_data(client_socket, time_record, id_workspace, path_CLI_local):
                   break 
            except KeyboardInterrupt:
                client_socket.close()
            except socket.error as e:
                logger.warning(f'there was a connexion issue "{e}"')
                sleep(2)
                break 
            except Exception:
                logger.warning('unknown issue')
                break          
        
        
        client_socket.close()
        return
    

if len(argv) == 1:
        servicemanager.Initialize()             # ces 3 commandes permettent de lancer le serveur
        servicemanager.PrepareToHostSingle(cad_importer_client)
        servicemanager.StartServiceCtrlDispatcher()
else:
    win32serviceutil.HandleCommandLine(cad_importer_client)        # si il y a un argument, par exemple create ou delete