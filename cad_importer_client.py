# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 15:25:03 2024

@author: AxelBaillet
"""

 # CODE pour serveur client
#on suppose qu' on a deja la liste CAD pour le momen t 
import socket 
from time import time 



# COTE IMPORT DANS LE DECK 

# def import_fichier_CAD(time_record, save_id_workspace, path_XRCENTER_local, fichier):
#     x=0
#     start = time()
#     commande_fichier_import= f'& "{path_XRCENTER_local}"  cad import "{save_id_workspace}" "{fichier}"' #commande pour importer sur le deck
#     import_final = subprocess.run(["Powershell", "-Command", commande_fichier_import], capture_output=True, text=True)
#     end = time()
#     temps_import= end - start
#     if "failed" in import_final.stdout.lower() or "error" in import_final.stdout.lower():
#             print(f'Le fichier "{fichier}"ne s est pas mis dans SkyReal')   
#             time_record.append('error')
#     else: 
#         time_record.append(temps_import)                        #on mesure le temps de chaque import
#         print(f'le fichier "{fichier}" est dans SkyReal')
#         x = 1
#     return x 
    
    

##  COTE SERVEUR CLIENT

#use_data(client_socket, time_record, save_id_workspace, path_XRCENTER_local, fichier))
def use_data(client_socket):
    client_socket.sendall(b'i am ready')
    file_to_receive = client_socket.recv(1024)
#   x = import_fichier_CAD(time_record, save_id_workspace, path_XRCENTER_local, file_to_receive)
#   client_socket.sendall(x)
    
    return
    
    
        
    
    
def main():
    
    # se connecter au serveur 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    adress_host= ('192.168.0.7', 3000)
    if client_socket.connect( adress_host) ==  None:   
        print('good')    

    condition = True;           # pour faire arreter le serveur client
    
    while condition: 
        use_data(client_socket)
        if client_socket.recv(1024) == B'close':             # condition de fermeture des serverus clients
            condition = False
    
    client_socket.close()
    return

main()