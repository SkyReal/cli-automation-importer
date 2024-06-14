# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 15:25:03 2024

@author: AxelBaillet
"""

 # CODE pour serveur client
#on suppose qu'on a deja la liste CAD pour le moment 
import socket 


# COTE IMPORT DANS LE DECK 
##  COTE SERVEUR CLIENT


def get_ID_workspace(client_socket, id_workspace):
    try: 
        id_workspace_bytes = client_socket.recv(4096)            # le fichier arrive en binaire, normalement sans erreur si il est apres select()
        id_workspace = id_workspace_bytes.decode('utf-8')          # on le retransforme en string
        print('id_workspace imported')
    except socket.error as e:
        print('connexion error', e)
        return
    return id_workspace
   
    
#use_data(client_socket, time_record, save_id_workspace, path_XRCENTER_local, fichier))
def use_data(client_socket):
    try:
        file_to_receive_bytes = client_socket.recv(4096)            # le fichier arrive en binaire, normalement sans erreur si il est apres select()
        file_to_receive= file_to_receive_bytes.decode('utf-8')          # on le retransforme en string
        if file_to_receive == 'close':     
            print('the client will close now')                                # on arrete le programme
            return False
    # ce que le serveur doit faire
    
        print('fichier a recevoir test', file_to_receive)
   
    
    # envoyer les resultats
        x=b'A'   # pour dire que l'import a reussi     
        client_socket.send(x)
    except KeyboardInterrupt:
        return False
    return True
        
    
    
def main():
    
    # initialiser les variables
    id_workspace = ''
    
    # se connecter au serveur 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    adress_host= ('192.168.0.7', 3000)      # l'adresse du serveur host
    if client_socket.connect(adress_host) ==  None:        # si le serveur est bien connecté   
        print('the client was successfuly connected')    
    
    # en premier lieu, on lui transfere l'ID du workspace
    
    id_workspace = get_ID_workspace(client_socket, id_workspace)
    
    
    print('starting the import program')
    while True:
        try: 
           if not use_data(client_socket):
               break 
        except KeyboardInterrupt:
            client_socket.close()
    
    client_socket.close()
    return

main()