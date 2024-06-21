# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 15:25:03 2024

@author: AxelBaillet
"""


from pathlib import Path
import argparse
import socket 
from time import time 
from time import sleep
from subprocess import run 
from json import load
from ipaddress import ip_address, AddressValueError

IDLE_TIME_OUT = 300     # temps en secondes pour lequel le programme s'arrete


# COTE IMPORT DANS LE DECK 

def get_config_files_datas(path_CLI_local, JSON_file ):
    if JSON_file.lower().endswith('.json'):          # on vérifie qu'on nous donne un json
        print('Your json file has been properly exploited')     
    else :
        print("This is not a json file")
        return None
    file = open(JSON_file, 'r')
    config_files_dictionnaire = load(file)                                     #on convertit le json en dictionnaire 
    path_CLI_local = config_files_dictionnaire["adresse_cli"] 
    if (path_CLI_local == None): 
        print(' ADRESSE_XRCENTER is missing in the config file.')
        return None
    return path_CLI_local
        


def verif_CLI(path_CLI_local):
    commande_CLI_opti1= f'& "{path_CLI_local}" health ping'
    CLI_ope = run(["Powershell", "-Command", commande_CLI_opti1], capture_output=True, text=True)
    if 'success' in CLI_ope.stdout.lower():                                #le XRCENTER se lance avec le chemin basique 
        print("CLI functional")
    else:                                                                       #on fait l'opération avec les paramètres que l'utilisateur a inséré
        print("Error : Is your CLI functional?")
        return False
    return True



def import_CAD_file(time_record, save_id_workspace, path_CLI_local, file):
    print(f'your file "{file}" is send in SkyReal')
    commande_fichier_import= f'& "{path_CLI_local}"  cad import "{save_id_workspace}" "{file}"' #commande pour importer sur le deck
    start = time()
    import_final = run(["Powershell", "-Command", commande_fichier_import], capture_output=True, text=True)
    print('import_final', import_final)
    end = time()
    time_record= end - start                                                                           # on mesure le temps de chaque import
    if "failed" in import_final.stdout.lower() or "error" in import_final.stdout.lower():
            print(f' \n the file "{file}" cant be put in SkyReal \n ')   
            time_record= -1             # l'import a echoue
    else:
        print(f'your file "{file}" is in SkyReal')
    return time_record


##  COTE SERVEUR CLIENT

def verif_IP_adress(ip_address_host):               # verifier la validite de l'adresse ip du host
    try:
       ip_address(ip_address_host)
       print('Warning : make sure to verify that the IP adress in the json file is the one of your host computer')
       return True
    except AddressValueError:
        print('your ipadress is not valid')
        return False
    
    
    
def get_IP_adress(JSON_file):
        file = open(JSON_file, 'r')
        config_files_dictionnaire = load(file)     
        IP_adress = config_files_dictionnaire["adresse_ip"] 
        if IP_adress == '':
            print('Did you put the right IP_adress in the config file ?')
        return IP_adress
        
        
        
def get_ID_workspace(client_socket, id_workspace):
    try: 
        id_workspace_bytes = client_socket.recv(4096)            # le fichier arrive en binaire, normalement sans erreur si il est apres select()
        id_workspace = id_workspace_bytes.decode('utf-8')          # on le retransforme en string
        print('id_workspace imported', id_workspace )
    except socket.error as e:
        print('connexion error', e)
        return ''
    except Exception:
        print('an error as occured, please try again')
        return ''
    return id_workspace
   
    
   
def use_data(client_socket, time_record, id_workspace, path_CLI_local):
    try:
        file_to_receive_bytes = client_socket.recv(4096)            # le fichier arrive en binaire, normalement sans erreur si il est apres select()
        file_to_receive= file_to_receive_bytes.decode('utf-8')          # on le retransforme en string
        if file_to_receive == 'close':     
            print('the client will close now')                                # on arrete le programme
            return False
   
    # ce que le serveur doit faire
        check_existence = Path(file_to_receive)
        if not check_existence.exists():                           # On considere que si un seul fichiers n'est pas present sur le pc, le repertoire n existe pas du tout et on ferme ce client
            print('the CAD file can not be found on this computer. You must be able to access it. This client will close') 
            
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
    time_before_unconnecting = 0
    while not connected and time_before_unconnecting < 300 :         # 10 minutes d'attentes max
        try:
            client_socket.connect(adress_host)        # si le serveur est bien connecté   
            print('the client was successfuly connected')
            connected = True 
        except socket.error:
           sleep(5)
           print('waiting for a host server, remaining time before disconnexion =', IDLE_TIME_OUT - time_before_unconnecting)
           time_before_unconnecting += 5
    if not connected:
        print('Failed to connect to the server after 5 minutes.')
        client_socket.close()  # Fermer le socket si la connexion échoue
        return False
    return True
    
def main():
    
    
    # initialiser les arguments 
    
    parser = argparse.ArgumentParser(description = 'Process the three arguments')                     # va gerer les differents arguments
    parser.add_argument('--json', type = str, help = 'name of your json containing the informations required to make the program work.', required= True)
    args = parser.parse_args()  # parcourir les differents arguments
    JSON_file = args.json 
    
    
    # initialiser les variables
    ip_adress_host = ''
    id_workspace = ''
    time_record= 0.0
    path_CLI_local = None
    
    path_CLI_local = get_config_files_datas(path_CLI_local, JSON_file )      # on prend le path CLI
    
    if verif_CLI(path_CLI_local) == False:
        return
    
    
    
    # obtenir l'adresse ip 
    
    ip_adress_host=  get_IP_adress(JSON_file)
    
    # verifier la validité de l'adresse ip
    
    verif_IP_adress( ip_adress_host)
    
    # se connecter au serveur 
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    adress_host= (ip_adress_host, 3000)      # l'adresse du serveur host
    
    
    if verif_connexion_to_host(client_socket, adress_host) == False:          # verifier si on est bien connecte sinon attendre
        return 
    
    
    # en premier lieu, on lui transfere l'ID du workspace
    
    id_workspace = get_ID_workspace(client_socket, id_workspace)
    
    if id_workspace == '':                  # on ferme le serveur si il y a une erreur 
        client_socket.close()
        return 
    
    # effectuer les imports 
    
    print('starting the import program')
    while True:
        try: 
           if not use_data(client_socket, time_record, id_workspace, path_CLI_local):
               break 
        except KeyboardInterrupt:
            client_socket.close()
        except socket.error:
            print('there was a connexion issue')
            sleep(2)
            break 
        except Exception:
            print('unknown issue')
            break
            
    
    
    client_socket.close()
    return

main()