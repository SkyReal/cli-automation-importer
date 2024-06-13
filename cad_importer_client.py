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

#use_data(client_socket, time_record, save_id_workspace, path_XRCENTER_local, fichier))
def use_data(client_socket):
    file_to_receive_bytes = client_socket.recv(4096)            # le fichier arrive en binaire, normalement sans erreur si il est apres select()
    file_to_receive= file_to_receive_bytes.decode('utf-8')          # on le retransforme en string
    
    # ce que le serveur doit faire
    
    print('fichier a recevoir test', file_to_receive)
   
    
    # envoyer les resultats
    x=b'A'   # pour dire que l'import a reussi     
    client_socket.send(x)
    return
    
    
    
    
def main():
    
    # se connecter au serveur 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    adress_host= ('192.168.0.7', 3000)
    if client_socket.connect(adress_host) ==  None:        # si le serveur est bien connecté   
        print('good')    

    use_data(client_socket)
   
    
    client_socket.close()
    return

main()