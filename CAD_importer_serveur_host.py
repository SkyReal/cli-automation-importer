# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 09:44:04 2024

@author: AxelBaillet
"""

        


#serveur host 

import socket 
from threading import Thread
from time import sleep
 
 
 
 
 
 
 
 
# PARTIE CREATION DU SERVEUR 

def handle_clients(clients_list, client_addresses, client_address, client_socket):
    if client_address[0] not in client_addresses:       # l'adresse ip du client n'est pas présente dans la liste
        client_addresses.add(client_address[0])
        clients_list.append(client_socket)
    return
    
def accept_connexions(clients_list, serversocket, client_addresses) :           # gerere les erreurs plus 
    while fichiers_CAD != []:           # condition d'arret du thread
        (client_socket, client_address) = serversocket.accept()   #pour accepter la connexion de clients    
        handle_thread = Thread(target = handle_clients, args= (clients_list, client_addresses, client_address, client_socket))          #on tchek en permanence si il y a une adresse dispo
        handle_thread.start()
        sleep(5)
    return 
    


def computer_in_work(clients_list , fichiers_CAD):
    while len(fichiers_CAD) > 0 :           # condition d'arret du thread
        try: 
            for k in range(0, len(clients_list)):
                clients_list[k].sendall(b'ready?')            # as tu finis ton import ?   
                if clients_list[k].recv(1024) == b'i am ready':           # si oui
                    file_to_send = fichiers_CAD.pop(0)              # on prend le nouveau premier element de fichiers cad 
                      clients_list[k].sendall(file_to_send)         # on envoie le fichier au client dispo 
        finally:
            sleep(5)
    return 
            

    
def threading_in_progress(clients_list, serversocket, client_addresses, fichiers_CAD):
    accept_thread = Thread(target = accept_connexions, args=(clients_list, serversocket, client_addresses))          #on tchek en permanence si il y a une adresse dispo
    accept_thread.start()
    
    verif_thread = Thread(target = computer_in_work, args= ( clients_list , fichiers_CAD ) )
    verif_thread.start()    
    return  

def close_clients(clients_list):
    for k in range(0, len(clients_list)):
        clients_list[k].sendall(b'close')            # as tu finis ton import ?   
    return
    
    


def main():  
    
    # initialisation des variables
    
    FICHIER_TEST = [1,2,3]
    
    clients_list= []
    client_addresses=  set()  #ensemble non ordonnées d'elements, on va s'en servir pour être sur qu'un serveur client n'apparait pas 2 fois 
    
    # creation du serveur
    
    serversocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(( socket.gethostbyname(socket.gethostname()), 3000) )        
    serversocket.listen()
    print('le serveur est démarré')
   
    
    try:
        threading_in_progress(clients_list, serversocket, client_addresses, FICHIER_TEST)  # A CHANGER!
            
    while len(FICHIER_TEST) > 0 :
        
    
    close_clients(clients_list)     # on ferme les serveurs clients
    serversocket.close()
    return 
   
    
main()       