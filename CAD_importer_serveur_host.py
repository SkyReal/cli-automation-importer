# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 09:44:04 2024

@author: AxelBaillet
"""

        


#serveur host 

import socket 
from threading import Thread
from time import sleep
from select import select
import os 
import sys
import json 
from datetime import datetime
import subprocess
# extensions de fichiers CAD pris en compte par SkyReal

extensions = [".CATPart", ".CATProduct",".CGR","CATProcess",".model","3dxml",".plmxml",".jt", ".prt",".asm",".ifc",".sldprt",".sldasm",".stp", ".step",".stl",".iam",".ipt",".x_t",".dwg"]

## certaines extensions sont en train d'être ajoutées : .fbx , .dgn . 

#   PARTIE SCAN D'UN DOSSIER MIS EN ARGUMENT

# variables nécessaires pour la partie scan et infos

def verif_dossier_a_traiter():   # verifier que notre deuxieme argument est valide
    if len(sys.argv) < 2:
        print( 'The first argument of the function must be the path of your repertory (or file) with the CAD files in it')
        return False
    else:
        if os.path.exists(sys.argv[1]) == False:
            print('The path of your repertory is incorrect')
            return False 
        if os.path.isdir(sys.argv[1]) == False and  os.path.isfile(sys.argv[1]) == False: 
            return False
    print('The repertory will be scanned ')
    return True

def donnees_config_files(path_CLI_local):
    if len(sys.argv) !=3:    #le file n'a pas encore été défini  
        print(' You need as a second argument a json file with informations related to your computer, containing  \n ADRESSE_XRCENTER=')
        return None
    else: 
        config_files = sys.argv[2]
        if config_files.lower().endswith('.json'):          # on vérifie qu'on nous donne un json
            print('Your json file has been properly exploited')     
        else :
            print("Error on the json file")
            return None
        file = open(config_files, 'r')
        config_files_dictionnaire = json.load(file)                                     #on convertit le json en dictionnaire 
        path_CLI_local = config_files_dictionnaire["adresse_cli"] 
        if (path_CLI_local == None): 
            print(' ADRESSE_XRCENTER is missing in the config file.')
            return None
    return path_CLI_local


def verif_CLI(path_CLI_local):
    commande_CLI_opti1= f'& "{path_CLI_local}" health ping'
    CLI_ope = subprocess.run(["Powershell", "-Command", commande_CLI_opti1], capture_output=True, text=True)
    if 'success' in CLI_ope.stdout.lower():                                #le XRCENTER se lance avec le chemin basique 
        print("CLI functional")
    else:                                                                       #on fait l'opération avec les paramètres que l'utilisateur a inséré
        print("Error : Is your CLI functional?")
        return False
    return True


def creation_workspace_deck(save_id_workspace, path_CLI_local):
    workspace_json={}
    print('Un nouveau workspace sera crée pour vos dossiers dans le Deck SkyReal')
    date = datetime.now().strftime("%Y-%m-%d %H:%M")                    ## le nom du workspace correspond à la date de sa création 
    creation_workspace= f'& "{path_CLI_local}" workspace create --name workspace_"{date}"'
    nouveau_workspace= subprocess.run(["Powershell", "-Command", creation_workspace], capture_output=True, text=True)
    workspace_json= json.loads(nouveau_workspace.stdout)
    save_id_workspace= workspace_json["EntityId"]
    if nouveau_workspace.stderr != '':   #on vérifie qu'il n'y a pas d'erreurs, à compléter plus tard
        print('il y a un problème avec le workspace')
        return None
    return save_id_workspace



def chercher_fichiers(liste_fichiers, path_dossier):   # fonction intermediaire
    for path, directory, files in os.walk(f"{path_dossier}"):
       for file_name in files:
            file_path = os.path.join(path, file_name)                   # Obtenir le chemin absolu du fichier
            liste_fichiers.append(file_path)                            # Ajouter le chemin absolu à la liste
    return 


def scan_CAD(liste_fichiers, fichiers_CAD, path_dossier):
    chercher_fichiers(liste_fichiers, path_dossier)
    if liste_fichiers == [] :                                               # Le dossier est vide 
        print('The repertory is empty')
        return False
    else: 
        for k in range(0,len(liste_fichiers)):
            for i in range(0, len(extensions)):                             #on s'arrête s'il n'existe pas de fichers CAD
                if liste_fichiers[k].lower().endswith(extensions[i].lower()) == True :      #c'est un dossier CAD, on regarde son extension en minuscule pour le rendre insensible a la casse
                    fichiers_CAD.append(liste_fichiers[k])
                    break                                                   #on n'a pas besoin de regarder le reste des extensions
    if (fichiers_CAD == []):                                                # il n'y avait pas de fichiers à traiter
        print('There was no CAD files in this repertory')
        return False 
    return True

 
# PARTIE CREATION DU SERVEUR 
def send_workspace_id(client_socket, save_id_workspace):
    save_id_workspace_bytes=  save_id_workspace.encode('utf-8')
    client_socket.send(save_id_workspace_bytes)
    print(' the workspace id was sent')
    return 
    

def handle_clients(client_addresses, client_address, new_client_socket, client_state):
    if client_address[0] not in client_addresses:       # l'adresse ip du client n'est pas présente dans la liste
        client_addresses.add(client_address[0])
        client_state[new_client_socket] = 'ready'      #on initialise le premier client comme prêt a travailler
        print(f'the connexion "{client_address[0]}" started' )
    else:
        print(f'the client "{client_address[0]}" is already connected')
    return
    
def accept_connexions(serversocket, client_addresses, fichiers_CAD, client_state, save_id_workspace) :           # gerera les erreurs plus 
    while len(fichiers_CAD) > 0:           # condition d'arret du thread
        try:
            (new_client_socket, client_address) = serversocket.accept()   #pour accepter la connexion de clients    
            handle_clients(client_addresses, client_address, new_client_socket, client_state)# on les repertorie 
            send_workspace_id(new_client_socket, save_id_workspace)
            sleep(5)
        except socket.error as err:         #gerer les erreurs propres a la connexion des sockets 
            print(f"Socket error: {err}")
        except Exception as e:              # gerer les autres erreurs
            print(f"An unexpected error occurred while getting a new client: {e}")   
    return 
    

def computer_in_work_v2(fichiers_CAD, result_list, working_list, client_state):
    clients_list = client_state.keys()
    while True:
        clients_list_readable, client_list_writeable, client_error = select(clients_list, clients_list, clients_list, 10)    # methode non bloquante qui va gerer automatiquement si le boug nest pas prêt
        if client_error != []:
            for client_socket in client_error:
                print(f'error with "{client_socket}", the client will now close')
                clients_list.remove(client_socket)          #on enleve le socket problematique 
                client_socket.close()       # on ferme le socket
        if client_list_writeable != []:         # ces client sont prêt à recevoir des infos
                for client_sockets in client_list_writeable:
                    if len(fichiers_CAD) >0 :
                        if client_state[client_sockets] == 'ready':
                            file_to_send = fichiers_CAD.pop(0)                 # on prend le nouveau premier element de fichiers cad
                            file_to_send_bytes= file_to_send.encode('utf-8')   # il faut envoyer le fichier en binaire
                            client_sockets.sendall(file_to_send_bytes)         # on envoie le fichier au client dispo 
                            print('sending required datas')
                            client_state[client_sockets] = 'working' # ils ne sont plus pret
                            working_list.append(client_sockets)            
                            sleep(1)
    return 


def reception_v2(working_list, result_list, client_state):
    while True:
        if working_list != []:
            clients_reception_readable, clients_reception_writeable, client_reception_error = select(working_list, working_list, working_list, 5)
            if client_reception_error != []:
                for client_socket in client_reception_error:
                    try:
                        print(f'error with "{client_socket}", the client will now close')
                        del client_state[client_socket]
                    except Exception:           # la cle a disparue?
                        print(f'error with "{client_socket}", the client can not be reach')         
            if clients_reception_readable != []:
                for sleeping_clients in clients_reception_readable:
                    try:            # on peut deja lire leurs contenus avec readable, il faudra juste gerer les erreurs de wifi
                        result_wait_bytes = sleeping_clients.recv(1024)     # on regarde si ils renvoient quelque chose
                        result_wait = result_wait_bytes.decode('utf-8')
                        if result_wait == 'A':      # l'import a reussi 
                            result_wait_int = 1 
                        else:                   # l'import a echoué
                            result_wait_int = 0
                        result_list.append(result_wait_int)
                        client_state[sleeping_clients] = 'ready'
                        working_list.remove(sleeping_clients)
                    except socket.error:
                        print('Error while getting a client response')
    return



def threading_in_progress(serversocket, client_addresses, fichiers_CAD, result_list, working_list, client_state, save_id_workspace):
    
    accept_thread = Thread(target = accept_connexions, args=(serversocket, client_addresses, fichiers_CAD, client_state, save_id_workspace), daemon = True)          #on verifie en permanence si il y a une adresse dispo
    accept_thread.start()
    
    send_thread = Thread(target = computer_in_work_v2, args= (fichiers_CAD, result_list, working_list, client_state), daemon = True )
    send_thread.start()    
    
    reception_thread = Thread(target = reception_v2 , args= (working_list, result_list, client_state), daemon = True )# QUELS ARGUMENTS ?
    reception_thread.start()
    
    return accept_thread,send_thread, reception_thread
    

def closing_thread(accept_thread, send_thread,reception_thread):
    accept_thread.join(0)    
    send_thread.join(0)
    reception_thread.join(0)
    return
    
def closing_clients(client_state):
    for kill_clients in client_state.keys():             # pour fermer tout les clients
        closing_message = 'close'                        
        closing_message_byte= closing_message.encode('utf-8')           #pour pouvoir l'envoyer
        kill_clients.sendall(closing_message_byte)      
    # kill_client_readable, kill_client_writeable, _ = select(client_state.keys(), client_state.keys(), [],10)
    # while kill_client_writeable != []:
    #     sleep(1)
    return
        

def main():  
    
    # vérification sur les arguments de la fonction
    
    if not verif_dossier_a_traiter():
        return
    
    # variables nécessaires pour la partie scan et infos

    path_dossier = sys.argv[1]
    liste_fichiers=[]
    path_CLI_local = None
    save_id_workspace=''     
    
    # initialisation des variables necessaires au serveur 
    
    fichiers_CAD = []
    fichiers_CAD_copy = list(fichiers_CAD) # copie pour la condition
    result_list=[]
    client_addresses=  set()  #ensemble non ordonnées d'elements, on va s'en servir pour être sur qu'un serveur client ne s'enregistre pas 2 fois 
    working_list = []
    client_state = {}
    
    # infos et vérifications sur la CLI 
    
    path_CLI_local=donnees_config_files(path_CLI_local)
    if  path_CLI_local== None:
        print("error while trying to read config file")
        return
    
    if not verif_CLI(path_CLI_local):            # on arrete le programme en cas d'erreur 
        return 
    
    # creation du workspace et vérifications 
    
    save_id_workspace= creation_workspace_deck(save_id_workspace, path_CLI_local)       # on va passer ce workspace aux clients
    
    if save_id_workspace== None  or save_id_workspace== '':                         # mais seulement si il est valable 
        print( 'error in the workspace creation')
        return
    
    
    # scan du dossier 
    
    if not scan_CAD(liste_fichiers, fichiers_CAD, path_dossier) :
        return
    
    
    # creation du serveur
    
    serversocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(( socket.gethostbyname(socket.gethostname()), 3000) )        
    serversocket.listen()
    print('host server is starting')
   
    # il faut au moins un client pour pouvoir demarrer le script 
    
    print('waiting for a first client')
    try:
        (client_socket, client_address) = serversocket.accept()   #on bloque en attendant la premiere connexion
        client_state[client_socket] = 'ready'      #on initialise le premier client comme prêt a travailler
        print(f' client "{client_socket}" was successfuly open')
        send_workspace_id(client_socket, save_id_workspace)         # on envoie en premier lieu l'id du workspace
    except KeyboardInterrupt:
        serversocket.close()
    except socket.error as err:         #gerer les erreurs propres a la connexion des sockets 
        print(f"Socket error: {err}")
    
    # execution du serveur
    
    try:
        accept_thread, send_thread, reception_thread = threading_in_progress( serversocket, client_addresses, fichiers_CAD, result_list, working_list, client_state, save_id_workspace)  
    except KeyboardInterrupt:
        for clients in client_state.keys():
            clients.close()
            serversocket.close()
    finally:
        pass
    
    while len(result_list) < len( fichiers_CAD_copy ):
        sleep(2)
        
    
    closing_thread(accept_thread, send_thread, reception_thread)
        
    closing_clients(client_state)
    
    serversocket.close()
    return 
   
    
main()       









