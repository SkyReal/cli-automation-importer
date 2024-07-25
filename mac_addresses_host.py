# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 11:40:02 2024

@author: AxelBaillet
"""

import socket 
from struct import unpack
from time import sleep
from threading import Thread
import json 
import os

def get_mac_address(client_socket, mac_address):
    try: 
        mac_length = client_socket.recv(4)                                             # longeur de l'id workspace
        received_length = unpack('!I', mac_length)[0]                               # traduit de binaire a string
        sleep(3)
        mac_address_bytes = client_socket.recv(received_length)                   # le fichier arrive en binaire, normalement sans erreur si il est apres select()        
        mac_address =mac_address_bytes.decode('utf-8')                             # on le retransforme en string
        sleep(3)
    except socket.error as e:
        print('connexion error', e)
        return ''
    except Exception:
        print('an error has occured, please try again')
        return ''
    return mac_address  

def get_computer_name(client_socket, computer_name):
    try: 
        name_length = client_socket.recv(4)                                             # longeur de l'id workspace
        received_length = unpack('!I', name_length)[0]                               # traduit de binaire a string
        sleep(3)
        name_bytes = client_socket.recv(received_length)                   # le fichier arrive en binaire, normalement sans erreur si il est apres select()        
        computer_name =name_bytes.decode('utf-8')                             # on le retransforme en string
        sleep(3)
    except socket.error as e:
        print('connexion error', e)
        return ''
    except Exception:
        print('an error has occured, please try again')
        return ''
    return computer_name  

def accept_connexions(serversocket, mac_address, mac_dictionary, computer_name):
    while True:
        try:
            (client_socket, client_address) = serversocket.accept()   #pour accepter la connexion de clients  
            print(' Connecting with a new client')
            sleep(1)
            computer_name = get_computer_name(client_socket, computer_name)
            mac_dictionary[computer_name] = 0
            sleep(2)
            mac_element = get_mac_address(client_socket, mac_address)
            mac_dictionary[computer_name] = mac_element
            sleep(2)
            format_json(mac_dictionary)
            sleep(2)
        except socket.error as err:         #gerer les erreurs propres a la connexion des sockets 
            print(f"Socket error: {err}")
            sleep(5)
    
        except KeyboardInterrupt:         #gerer les erreurs propres a la connexion des sockets 
            return  
        except Exception as e:              # gerer les autres erreurs
            print(f"An unexpected error occurred while getting a new client: {e}")   
    return


def format_json(dictionary):
    
    json_filename = r"C:\ProgramData\cli_automation_importer\mac_addresses.json"
    
    if os.path.exists(json_filename):
        with open(json_filename, 'r') as json_file:
            existing_data = json.load(json_file)
    else:
        # Si le fichier n'existe pas, initialiser avec un dictionnaire vide
        existing_data = {}
    existing_data.update(dictionary)
    dictionary_json = json.dumps(existing_data, indent=4)
    print(dictionary_json)
    with open(json_filename, 'w') as json_file:
        json_file.write(dictionary_json)
    return

    
def main():
    
    computer_name= ""
    mac_address = ""
    mac_dictionary = {}
    timer =  0
    
    # creer le serveur 
    
    serversocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(( socket.gethostbyname(socket.gethostname()), 3000) )        
    serversocket.listen()
    
    accept_thread = Thread(target = accept_connexions, args=(serversocket, mac_address, mac_dictionary, computer_name), daemon = True)          #on verifie en permanence si il y a une adresse dispo
    accept_thread.start()
    
    
    while timer < 200:
        try: 
            print("scanning and sending the datas :", 200 - timer, ' seconds left' )
            sleep(5)
            timer +=5 
        except KeyboardInterrupt:
            timer = 210 
    
    print('The program is ending ')
    return 

main()