# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 15:25:03 2024

@author: AxelBaillet
"""

 # CODE pour serveur client
#on suppose qu'on a deja la liste CAD pour le moment 
import socket 
from time import time 
from subprocess import run 
import sys
from json import load
# COTE IMPORT DANS LE DECK 

# pour avoir le path de la CLI

def donnees_config_files(path_CLI_local):
    if len(sys.argv) !=2:    #le file n'a pas encore été défini  
        print(' il faut le chemin d un fichier json pour configurer les informations propres a votre machine que vous placerez en premier argument, contenant \n adresse_cli=')
        return None
    else: 
        config_files = sys.argv[1]
        if config_files.lower().endswith('.json'):          # on vérifie qu'on nous donne un json
            print('votre fichier json est bien pris en compte')     
        else :
            print("erreur sur le fichier json en argument")
            return None
        file = open(config_files, 'r')
        config_files_dictionnaire = load(file)                                     #on convertit le json en dictionnaire 
        path_CLI_local = config_files_dictionnaire["adresse_cli"] 
        if (path_CLI_local == None): 
            print(' l adresse de la CLI est manquante dans le fichier de configuration.')
            return None
    return path_CLI_local
        


def import_fichier_CAD(time_record, save_id_workspace, path_CLI_local, fichier):
    print(f'votre fichier "{fichier}" va etre ajouté a SkyReal')
    commande_fichier_import= f'& "{path_CLI_local}"  cad import "{save_id_workspace}" "{fichier}"' #commande pour importer sur le deck
    start = time()
    import_final = run(["Powershell", "-Command", commande_fichier_import], capture_output=True, text=True)
    end = time()
    print('import', import_final)
    time_record= end - start                                                                           # on mesure le temps de chaque import
    if "failed" in import_final.stdout.lower() or "error" in import_final.stdout.lower():
            print(f'Le dossier "{fichier}"ne s est pas mis dans SkyReal')   
            time_record= -1             # l'import a echoue
    return time_record
    

##  COTE SERVEUR CLIENT


def get_ID_workspace(client_socket, id_workspace):
    try: 
        id_workspace_bytes = client_socket.recv(4096)            # le fichier arrive en binaire, normalement sans erreur si il est apres select()
        id_workspace = id_workspace_bytes.decode('utf-8')          # on le retransforme en string
        print('id_workspace imported')
    except socket.error as e:
        print('connexion error', e)
        return
    except Exception:
        print('an error as occured, please try again')
        return
    return id_workspace
   
    
   
def use_data(client_socket, time_record, id_workspace, path_CLI_local):
    try:
        file_to_receive_bytes = client_socket.recv(4096)            # le fichier arrive en binaire, normalement sans erreur si il est apres select()
        file_to_receive= file_to_receive_bytes.decode('utf-8')          # on le retransforme en string
        if file_to_receive == 'close':     
            print('the client will close now')                                # on arrete le programme
            return False
   
    # ce que le serveur doit faire
        
        time_record = import_fichier_CAD(time_record, id_workspace, path_CLI_local, file_to_receive)
        
    # envoyer les resultats
        time_record_byte = str(time_record).encode()          # on traduit le float en chaine de caractere que l'on met en bytes
        client_socket.send(time_record_byte)
        
        
    except KeyboardInterrupt:
        return False
    return True
        
    
    
def main():
    
    # initialiser les variables
    id_workspace = ''
    time_record= 0.0
    path_CLI_local = None
    
    path_CLI_local = donnees_config_files(path_CLI_local)       # on prend le path CLI
    
    if path_CLI_local == None:
        return
    
    
    
    # se connecter au serveur 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    adress_host= ('192.168.0.7', 3000)      # l'adresse du serveur host
    if client_socket.connect(adress_host) ==  None:        # si le serveur est bien connecté   
        print('the client was successfuly connected')    
    
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
    
    client_socket.close()
    return

main()