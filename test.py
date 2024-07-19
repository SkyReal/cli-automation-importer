# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 14:23:11 2024

@author: AxelBaillet
"""


# from wakeonlan import send_magic_packet
import json 
from subprocess import run 


def get_informations_on_computer():
    stdout = []            #liste temporaire
    powershell_command = run(["Powershell", "-Command", 'Get-NetAdapter | Where-Object { $_.Name -eq "Ethernet" } | Select-Object MacAddress'], capture_output=True, text=True)             #on prend l'adresse mac liée à l'ethernet
    
    for k in powershell_command.stdout:
        stdout.append(k)
    print(stdout)
    x=0
    for k in stdout:
        if k == '\n':
            x +=1
        if x ==3:
            break 
    
    return

def read_json(fichier_json):        # lit le fichier json et ajoute les adresses ip a celles pretes a travailler
    with open(fichier_json, 'r') as file:
        ip_dictionary = json.load(file)
    return ip_dictionary


def main():
    
     # si on fait le WOL 
     send_magic_packet( '30.9C.23.13.E9.56')             # reveiller l'ordi indiqué
         # on send le message 'awake with WOL
    # else 
        # send awake by yourself 
         
         
         
         
         
        # ip_dictionary = read_json("C:\\Users\\AxelBaillet\\Documents\\cli-automation-importer\\ip.json")
        # print(ip_dictionary)
        # return 
     get_informations_on_computer()
    return


main()



def verif_CLI(path_CLI_local):
    x=0
    commande_CLI_opti1= f'& "{path_CLI_local}" health ping'
    while x < 10:                                                                                           # max 10 essais
        CLI_ope = run(["Powershell", "-Command", commande_CLI_opti1], capture_output=True, text=True)
        logger.info(CLI_ope)
        if 'success' in CLI_ope.stdout.lower():                                                             #le XRCENTER se lance avec le chemin basique 
            logger.info("CLI functional")
            return True 
        else:                                                                                               #on fait l'opération avec les paramètres que l'utilisateur a inséré
            logger.info("Trying to join the XRCenter")
            stdout = CLI_ope.stdout
            logger.info(f"stdout :  {stdout}")
            x += 1                  
    return False

def ping_until_answer(ip_address, ping_result):
    global PING_NUMBER
    x = 0
    while x < PING_NUMBER:
        if ip_address == socket.gethostbyname(socket.gethostname()):
            x  = PING_NUMBER
            ping_result = True 
            return ping_result 
        else:
            powershell_ping_result = run(['ping', '-c', '1', ip_address], capture_output=True, text=True)
            
            if powershell_ping_result.returncode == 0:
                logger.info('the client just reached the host computer ( ping command was successful ) ')
                ping_result = True 
                return ping_result                                      # on a reussi a pinger le server
             
            x += 1                                                      # on passe à l'essai suivant
            sleep(5)                                                    #  laisser le temps entre deux essais
    logger.info('the client was not able to reach the server. It will try again ')
    ping_result =False                                                  # commande a priori inutile mais on ne sait jamais ( le ping result est par defaut False)
    return ping_result 



def verif_connexion_to_host(client_socket, adress_host, ip_address, path_CLI_local):
    connected = False
    ping_result = False 
    while not ping_result or not connected :        # pinger le pc puis voir si il arrive à se connecter
        if not ping_result:
            ping_result = ping_until_answer(ip_address, ping_result)
            if not verif_CLI(path_CLI_local):                   # si la CLI n'est pas bonne, on arrete le programme
            logger.info('Failed to connect') 
                break    
        else:                                                   # on a reussi a pinger, il reste a se connecter
            try:
                client_socket.connect(adress_host)        # si le serveur est bien connecté   
                logger.info('the client was successfuly connected')
                connected = True        # je considere que si il a reussi à etablir la connexion, il arrivera à se connecter au bout d'un moment
            except socket.error:
               sleep(5)
               logger.info(f'waiting for a host server, remaining time before disconnection : "{IDLE_TIME_OUT - time_before_disconnecting}"')
    return False 

    

















