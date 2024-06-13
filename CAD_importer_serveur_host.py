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
 
 
 
 
 
 
# PARTIE CREATION DU SERVEUR 

def handle_clients(clients_list, client_addresses, client_address, client_socket):
    if client_address[0] not in client_addresses:       # l'adresse ip du client n'est pas présente dans la liste
        client_addresses.add(client_address[0])
        clients_list.append(client_socket)
        print(f'la connexion avec "{client_address[0]}" a aboutie')
    else:
        print(f'le client "{client_address[0]}" est deja connecté')
    return
    
def accept_connexions(clients_list, serversocket, client_addresses, fichiers_CAD) :           # gerere les erreurs plus 
    while len(fichiers_CAD) > 0:           # condition d'arret du thread
        (client_socket, client_address) = serversocket.accept()   #pour accepter la connexion de clients    
        handle_clients(clients_list, client_addresses, client_address, client_socket)# on les repertorie 
        sleep(5)
    return 
    


# def computer_in_work(clients_list , fichiers_CAD, serversocket):
#     while len(fichiers_CAD) > 0 :           # condition d'arret du thread
#         try: 
#             for k in range(0, len(clients_list)):
#                 clients_list[k].sendall(b'ready?')            # as tu finis ton import ?   
#                 try:
#                     if clients_list[k].recv(1024) == b'i am ready':           # si oui
#                         file_to_send = fichiers_CAD.pop(0)              # on prend le nouveau premier element de fichiers cad 
#                         file_to_send_bytes= file_to_send.encode('utf-8')# il faut envoyer le fichier en binaire
#                         clients_list[k].sendall(file_to_send_bytes)         # on envoie le fichier au client dispo 
#                         print('envoi des données')
#                 except error_found:                                                 # si il y a une erreur dans l'envoi du fichier 
#                     print('erreur trouvée', error_found)
#                     serversocket.close()                #cette condition est amenée à etre changée
                        
#         finally:
#             sleep(5)
#     return 

def computer_in_work_v2(clients_list, fichiers_CAD, result_list, fichiers_CAD_copy, waiting_list, client_state):
    
    
    
    clients_list_readable, _, client_error = select(clients_list, [], clients_list)    # methode non bloquante qui va gerer automatiquement si le boug nest pas prêt
    
    if client_error != []:
        for client_socket in client_error:
            print('error with "{client_error[k]}", the client will now be close')
            clients_list.remove(client_socket)
            client_socket.close()       # on ferme le socket
            
    if clients_list_readable != []:         # ces client sont prêt à recevoir des infos
            for client_sockets in clients_list_readable:
                if client_state[client_sockets] == 'ready':
                    file_to_send = fichiers_CAD.pop(0)                 # on prend le nouveau premier element de fichiers cad
                    file_to_send_bytes= file_to_send.encode('utf-8')   # il faut envoyer le fichier en binaire
                    client_sockets.sendall(file_to_send_bytes)         # on envoie le fichier au client dispo 
                    print('envoi des données')
                    client_state[client_sockets] = 'waiting' # ils ne sont plus pret
                    waiting_list.append(client_sockets)          
    sleep(5)
    # on veut lire le message qu'ils renvoient a la fin
    return 
           
def reception(waiting_list, result_list, client_state):       # cela doit etre un thread
    
    if waiting_list != []:                      #♦ si des clients travaillent
        for waiting_clients in waiting_list:
            try:
                result_wait_bytes = waiting_clients.recv(1024)# on regarde si ils renvoient quelque chose
                result_wait = result_wait_bytes.decode('utf-8')
                if result_wait == 'A':      # l'import a reussi 
                    result_wait_int = int(result_wait)
                    result_wait_int = 1 
                else:                   # l'import a echoué
                    result_wait_int = int(result_wait)
                    result_wait_int = 0
                result_list.append(result_wait_int)
                client_state[waiting_clients] = 'ready'
            except socket.error:
                print(' il y a une erreur dans la reception de donnees de votre client')
    return
            
        


def threading_in_progress(clients_list, serversocket, client_addresses, fichiers_CAD, result_list, waiting_list, client_state, fichiers_CAD_copy):
    accept_thread = Thread(target = accept_connexions, args=(clients_list, serversocket, client_addresses, fichiers_CAD), daemon = True)          #on tchek en permanence si il y a une adresse dispo
    accept_thread.start()
    
    send_thread = Thread(target = computer_in_work_v2, args= (clients_list, fichiers_CAD, result_list, fichiers_CAD_copy, waiting_list, client_state), daemon = True )
    send_thread.start()    
    
    reception_thread = Thread(target = reception, args= (waiting_list, result_list, client_state), daemon = True )# QUELS ARGUMENTS ?
    reception_thread.start()
    return  

# def close_clients(clients_list):
#     for k in range(0, len(clients_list)):
#         clients_list[k].sendall(b'close')            # as tu finis ton import ?   
#     return
    
    


def main():  
    
    # initialisation des variables
    
    FICHIER_TEST = [1,2,3]
    FICHIER_TEST1 = FICHIER_TEST # copie pour la condition
    result_list=[]
    clients_list= []
    client_addresses=  set()  #ensemble non ordonnées d'elements, on va s'en servir pour être sur qu'un serveur client n'apparait pas 2 fois 
    client_state = { client : 'ready' for client in clients_list}       # on regarde si ils sont pret
    waiting_list = []
    # creation du serveur
    
    serversocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(( socket.gethostbyname(socket.gethostname()), 3000) )        
    serversocket.listen()
    print('le serveur est démarré')
   
    # il faut au moins un client pour pouvoir demarrer le script 
    print('waiting for a first client')
    try:
        (client_socket, client_address) = serversocket.accept()   #on bloque en attendant la premiere connexion
        clients_list.append(client_socket)
        print(' le client "{client_socket}" est connecte avec succes')
    except KeyboardInterrupt:
        serversocket.close()
    
    # execution du serveur
    
    try:
        threading_in_progress(clients_list, serversocket, client_addresses, FICHIER_TEST, result_list, waiting_list, client_state, FICHIER_TEST1)  # A CHANGER!
    except KeyboardInterrupt:
        for clients in clients_list:
            clients.close()
        serversocket.close()
    finally:
        pass
    
    while len(result_list) < len( FICHIER_TEST1 ):
        sleep(2)
        
    
    # while len(result_list) < len(FICHIER_TEST1) :            # a modifier 
    # computer_in_work_v2(clients_list, FICHIER_TEST, result_list, FICHIER_TEST1)      
    #     sleep(1)
        
    print(result_list)
    
    close_clients(clients_list)     # on ferme les serveurs clients
    serversocket.close()
    return 
   
    
main()       










