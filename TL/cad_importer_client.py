    # -*- coding: utf-8 -*-

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
from json import dump
from ipaddress import ip_address, AddressValueError
import logging
from sys import argv
from struct import unpack
from struct import pack
import re
from common import *


IDLE_TIME_OUT = 1000     # seconds
PING_NUMBER = 20 

# on va repertorier les erreurs dans un journal

log_directory = r'C:/ProgramData/cli_automation_importer'
log_file_path = os.path.join(log_directory, 'report.log')

if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    level=logging.INFO,                                     # on affichera les messages de gravite minimale 'info'
    format='%(asctime)s - %(levelname)s - %(message)s',     # le format des messages affiches 
    handlers=[logging.FileHandler(log_file_path, mode = 'w'), logging.StreamHandler()]   # le path du fichier ou seront ecrites les erreurs de debogage
)

logger = logging.getLogger('logger')        #initialisation du logger



def copy_file( source, destination):
    with open(source, 'r') as source_file:
        content = source_file.read()
        
    with open(destination, 'w') as destination_file:
        destination_file.write(content)
    return

# prendre les données 

def stop_program(wake_on_lan_activated):
    if wake_on_lan_activated:
        os.system("shutdown /s /t 60")
    return 

def clear_XRCENTER_config_file(base_address):
    xrcenter_config_file = "C:\\ProgramData\\Skydea\\xrcenter-cmd\\xrcenter-cmd.json"           # propre a skyreal
    with open(xrcenter_config_file, 'r') as xrcenter_file:
        xrcenter_dictionary = load(xrcenter_file)
    xrcenter_file.close()
    with open(xrcenter_config_file, 'w') as xrcenter_file_reopened:
        xrcenter_dictionary["XRCenter"]["BaseAddress"] = base_address
        dump(xrcenter_dictionary, xrcenter_file_reopened, indent=4)
    xrcenter_file_reopened.close()
    return


def verif_CLI(path_CLI_local):
    x=0
    commande_CLI_opti1= f'& "{path_CLI_local}" health ping'
    while x < 10:                                                                                           # max 10 essais
        CLI_ope = run(["pwsh", "-Command", commande_CLI_opti1], capture_output=True, text=True, encoding='utf-8', errors='replace')
        if 'success' in CLI_ope.stdout.lower():                                                             #le XRCENTER se lance avec le chemin basique 
            logger.info("CLI functional")
            return True 
        else:                                                                                               #on fait l'opération avec les paramètres que l'utilisateur a inséré
            logger.info("Trying to join the XRCenter")
            sleep(12)
            x += 1                  
    return False

def import_CAD_file(time_record, save_id_workspace, path_CLI_local, file):
    logger.info(f'Importing "{file}"')
    commande_fichier_import= f'& "{path_CLI_local}"  cad import "{save_id_workspace}" "{file}" --disable-3d-engine-visualization' #commande pour importer sur le deck
    start = time()
    import_final = run(["pwsh", "-Command", commande_fichier_import], capture_output=True, text=True, encoding='utf-8', errors='replace')
    end = time()
    time_record= end - start                                                                                                        # on mesure le temps de chaque import
    if "failed" in import_final.stdout.lower() or "error" in import_final.stdout.lower() or import_final.returncode != 0 :
            logger.info(f' \n Import failed "{file}"\n')
            print(import_final.stdout)
            time_record= -1                                                                                                         # l'import a echoue
            product_component_ID = ''                                                                                               #  on capture la sortie qui est le product component ID      (pas sur de moi ici)        
    else:
        logger.info(f'Imported successfully "{file}"')        
        product_component_ID = import_final.stdout                                                                                    # on capture la sortie qui est le product component ID      (pas sur de moi ici)        
    return time_record, product_component_ID

def get_polygons_number(path_CLI_local, save_id_workspace, product_component_ID):

    command_get_polygons = f'& "{path_CLI_local}" cad get-infos "{save_id_workspace}" "{product_component_ID}"'  # as t on besoin de & ?
    polygons_and_instances = run(["pwsh", "-Command", command_get_polygons], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if polygons_and_instances.returncode != 0:          # verifier que la commande s'est bien run
        return 0,0
    
    pattern = r'{"polygonCount":(\d+),"instanceCount":(\d+)}'     # Chercher le motif spécifique dans la chaîne de caractères
    match = re.search(pattern, polygons_and_instances.stdout)
    
    if match:
        polygon_count = int(match.group(1))     
        instance_count = int(match.group(2))
        return polygon_count, instance_count
    else:
        return 0, 0

def prepare_CAD_visualization(path_CLI_local, save_id_workspace, product_component_ID):
    
    command_prepare_visualization = f'& "{path_CLI_local}" cad preparevisualization "{save_id_workspace}" "{product_component_ID}" ' #commande pour preparer la visualisation
    
    start = time()
    prepare_visualization = run(["pwsh", "-Command", command_prepare_visualization], capture_output=True, text=True, encoding='utf-8', errors='replace')
    end = time()
    time_record= end - start   

    
    print("preparevisualization code ", str(prepare_visualization.returncode))
    if prepare_visualization.returncode != 0:          # verifier que la commande s'est bien run
        return -1
    else: 
        return time_record

def check_CLI_version(path_CLI_local, CLI_version):
    powershell_command_cli_version = f'''
    & '{path_CLI_local}' --version
    '''
    powershell_check_CLI = run(["pwsh", "-Command", powershell_command_cli_version], capture_output=True, text=True, encoding='utf-8', errors='replace')
    for caracters in powershell_check_CLI.stdout:
        if caracters == '-':
            break
        else: 
            CLI_version += caracters
    return CLI_version

def get_server_CLI_version(client_socket, server_CLI_version ):
    try: 
        id_length = client_socket.recv(4)                                             # longeur de l'id workspace
        received_id_length = unpack('!I', id_length)[0]                               # traduit de binaire a string
        sleep(3)
        server_CLI_version_bytes = client_socket.recv(received_id_length)                   # le fichier arrive en binaire, normalement sans erreur si il est apres select()        
        server_CLI_version = server_CLI_version_bytes.decode('utf-8')                             # on le retransforme en string
        sleep(3)
    except socket.error as e:
        logger.warning('connexion error', e)
        return ''
    except Exception:
        logger.warning('an error has occured, please try again')
        return ''
    return server_CLI_version

def is_wake_on_lan_activated(wake_on_lan):
    if wake_on_lan == 'activated':
        return True 
    elif wake_on_lan == "desactivated":
        return False
    else:
        print('error while getting datas, please try again')
        return 
    
    
##  COTE SERVEUR CLIENT

## on va d'abord pinger le serveur jusqu'a avoir une reponse 

def ping_until_answer(ip_address, ping_result):
    global PING_NUMBER
    x = 0
    while x < PING_NUMBER:
        if ip_address == socket.gethostbyname(socket.gethostname()):
            x  = PING_NUMBER
            ping_result = True 
            return ping_result 
        else:
            powershell_ping_result = run(['ping', '-n', '1', ip_address], capture_output=True, text=True, encoding='utf-8', errors='replace')
            if powershell_ping_result.returncode == 0:
                logger.info('the client just reached the host computer ( ping command was successful ) ')
                ping_result = True 
                return ping_result                                      # on a reussi a pinger le server
             
            x += 1                                                      # on passe à l'essai suivant
            sleep(5)                                                    #  laisser le temps entre deux essais
    logger.info('the client was not able to reach the server. It will try again ')
    ping_result =False                                                  # commande a priori inutile mais on ne sait jamais ( le ping result est par defaut False)
    return ping_result 



def send_informations(client_socket, informations):
    informations_bytes=  str(informations).encode('utf-8')              # parce qu'on travaille avec des nombres
    message_length = pack('!I', len(informations_bytes))
    client_socket.sendall(message_length + informations_bytes)
    return 


def verif_IP_address(ip_address_host):               # verifier la validite de l'adresse ip du host
    try:
       ip_address(ip_address_host)
       logger.info('Warning : make sure to verify that the IP adress in the json file is the one of your host computer, or the program wont work')
       return True
    except AddressValueError:
        logger.warning('your ip address is not valid')
        return False
    
    
def get_IP_address(JSON_file):
        file = open(JSON_file, 'r')
        config_files_dictionnaire = load(file)     
        IP_address = config_files_dictionnaire["ip_address_server"] 
        if IP_address == '' or IP_address == None:
            logger.warning('Did you put the right IP address in the config file ?')
            return False
        return IP_address
    
    
def get_wake_on_lan(client_socket, wake_on_lan):
    try: 
        id_length = client_socket.recv(4)                                             # longeur de l'id workspace
        received_id_length = unpack('!I', id_length)[0]                               # traduit de binaire a string
        sleep(3)
        wake_on_lan_bytes = client_socket.recv(received_id_length)                   # le fichier arrive en binaire, normalement sans erreur si il est apres select()        
        wake_on_lan =wake_on_lan_bytes.decode('utf-8')                             # on le retransforme en string
        logger.info(f' wake_on_lan "{wake_on_lan}"')
        sleep(3)
    except socket.error as e:
        logger.warning('connexion error', e)
        return ''
    except Exception:
        logger.warning('an error has occured, please try again')
        return ''
    return wake_on_lan  
 
    
def get_mapping_username(client_socket, mapping_username):
    try: 
        id_length = client_socket.recv(4)                                             # longeur de l'id workspace
        received_id_length = unpack('!I', id_length)[0]                               # traduit de binaire a string
        sleep(3)
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
        mapping_password_bytes = client_socket.recv(received_id_length)                   # le fichier arrive en binaire, normalement sans erreur si il est apres select()        
        mapping_password = mapping_password_bytes.decode('utf-8')                             # on le retransforme en string
        sleep(3)
        logger.info('The mapping password was received')
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
    product_component_ID = ''
    try:
        file_to_receive_bytes = client_socket.recv(4096)            # le fichier arrive en binaire, normalement sans erreur si il est apres select()
        file_to_receive= file_to_receive_bytes.decode('utf-8')          # on le retransforme en string
        if file_to_receive == 'close':     
            logger.info('the client will close now')                                # on arrete le programme
            return False
        logger.info(f'receiving "{file_to_receive}"')
    # ce que le serveur doit faire
        check_existence = Path(file_to_receive)
        if not check_existence.exists():                           # On considere que si un seul fichiers n'est pas present sur le pc, le repertoire n existe pas du tout et on ferme ce client
            logger.warning('the CAD file can not be found (do you have the access?') 
            time_record= -2 
        else:
            time_record, product_component_ID = import_CAD_file(time_record, id_workspace, path_CLI_local, file_to_receive)
            if product_component_ID != '':
                polygon_count, instance_count = get_polygons_number(path_CLI_local, id_workspace, product_component_ID)
            else:
                polygon_count, instance_count = -1 , -1                        # signaler un probleme 
                
            result_prep = prepare_CAD_visualization(path_CLI_local, id_workspace, product_component_ID)
                
        
    # envoyer les resultats
        
        send_informations(client_socket, time_record )
        
        sleep(1)
        
        send_informations(client_socket, polygon_count )
        
        sleep(1)
        
        send_informations(client_socket, instance_count )
        
        sleep(1)
        
        send_informations(client_socket, result_prep )
        
    except KeyboardInterrupt:
        return False
    return True
        


def verif_connexion_to_host(client_socket, address_host, IP_address_host, path_CLI_local, JSON_file):
    connected = False
    ping_result = False 
    while not ping_result or not connected :        # pinger le pc puis voir si il arrive à se connecter
        if not ping_result:
            ping_result = ping_until_answer(IP_address_host, ping_result)   
        else:
            if not verif_CLI(path_CLI_local):                                                   # on a reussi a pinger, il reste a se connecter
                path_CLI_local = get_config_files_datas(path_CLI_local, JSON_file )
                sleep(10)
            else:  
                try:
                    print("Server address :", address_host)
                    client_socket.connect(address_host)        # si le serveur est bien connecté   
                    logger.info('Connected!')
                    connected = True        # je considere que si il a reussi à etablir la connexion, il arrivera à se connecter au bout d'un moment
                except OSError as e:
                    # Log l'erreur avec le code d'erreur et le message
                    print(f"OSError: {e.errno} - {e.strerror}")
                    print("waiting for a host server")
                except socket.error:
                   sleep(5)
                   print(socket.error)
                   logger.info('waiting for a host server')
    return  



class cad_importer_client(win32serviceutil.ServiceFramework):
    _svc_name_ = "cad_importer_client_service"
    _svc_display_name_ = "import your CAD file in a defined XRCenter"
    _svc_description_ = "By connecting with a server, this service takes the path of Cad files and import them"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        logger.info('service waking up...')
        
    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        logger.info("initializing main")
        # Logique de service
        main()

        # Service en arrêt
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)

def main():
        
        # attendre un lancement propre du systeme
    logger.info("starting main")
    #sleep(30)
        
    # initialiser les variables
        
    IP_address_host = ''
    id_workspace = ''
    time_record= 0.0
    path_CLI_local = None
    share_path = ''
    server_CLI_version = ''
    CLI_version = ''
    wake_on_lan = ''
    wake_on_lan_activated = False
        
    # variable nécessaires au mapping
        
    mapping_username = ''
    mapping_password = ''
    drive_letter = "Z"
        
        
    # verifications des variables 
        
    JSON_file = "C:\ProgramData\cli_automation_importer\cad_importer_config_file.json"  # le path du json 
  
    path_CLI_local, XRCENTER_initial_address, _, _ , share_path = load_config_file(JSON_file)          

    # verifier qu'on s'est bien positionné sur le bon XRCenter
        
    if XRCENTER_initial_address == '':
        return 
        
    # verifier que les versions de la CLI sont compatibles 
        
    CLI_version = check_CLI_version(path_CLI_local, CLI_version)

    # obtenir l'adresse ip 
        
    IP_address_host=  get_IP_address(JSON_file)
        
    # verifier la validité de l'adresse ip
        
    if not verif_IP_address( IP_address_host):
        return 
        
    # verifier la validité de la CLI et du XRCenter
        
    if verif_CLI(path_CLI_local) == False:
        return
        
    # se connecter au serveur 
    logger.info("connecting to server")
        
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address_host= (IP_address_host, 3000)      # l'adresse du serveur host
        
        
    verif_connexion_to_host(client_socket, address_host, IP_address_host, path_CLI_local, JSON_file)         # verifier si on est bien connecté sinon attendre
        
        
    sleep(5) 
        
    # en premier lieu, on regarde si le wake_on_lan est actif
        
    wake_on_lan = get_wake_on_lan(client_socket, wake_on_lan)
                
    wake_on_lan_activated  = is_wake_on_lan_activated(wake_on_lan)          # on verifie si le wake on lan est activé
        
    # On regarde les versions
        
    server_CLI_version = get_server_CLI_version(client_socket, server_CLI_version)
        
    if server_CLI_version != CLI_version:
        logger.info('Warning : your server and your current computer dont have the same CLI version. It can be a source of error')
            
    sleep(3)
        
    #Ensuite, on lui transfere le username et le password 
        
    mapping_username = get_mapping_username(client_socket, mapping_username)
        
    mapping_password = get_mapping_password(client_socket, mapping_password)
            
    # mapping du reseau 
        
    if not create_smb_mapping(mapping_username, mapping_password ,drive_letter, share_path):
        logger.info("error on mapping")
        stop_program(wake_on_lan_activated)
        return
        
    # ensuite, on lui transfere l'ID du workspace
        
    id_workspace = get_ID_workspace(client_socket, id_workspace)
        
    if id_workspace == '':                  # on ferme le serveur si il y a une erreur 
        client_socket.close()
        stop_program(wake_on_lan_activated)
        return 
        
    # effectuer les imports 
        
    logger.info('starting the import program')
        
    while True:
        try: 
            if not use_data(client_socket, time_record, id_workspace, path_CLI_local):
                break 
        except socket.error as e:
            logger.warning(f'there was a connexion issue "{e}"')
            sleep(2)
            break 
        except Exception:
            logger.warning('unknown issue')
            break          
        
    remove_smb_mapping(drive_letter)

    clear_XRCENTER_config_file(XRCENTER_initial_address)
        
    client_socket.close()
        
        
    stop_program(wake_on_lan_activated)
        
    return
    

if len(argv) == 1:
        servicemanager.Initialize()             # ces 3 commandes permettent de lancer le serveur
        servicemanager.PrepareToHostSingle(cad_importer_client)
        servicemanager.StartServiceCtrlDispatcher()
else:
    if 'run' in argv:  # Ajout d'une commande 'run' pour exécuter comme un programme autonome
        main()
    else:
        win32serviceutil.HandleCommandLine(cad_importer_client)
