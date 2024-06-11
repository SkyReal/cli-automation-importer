# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 09:44:04 2024

@author: AxelBaillet
"""

#on considere quel'accese est autorise et que tout fonctionne

#on suppose qu'on a une liste 'machines' contenant les adresse ip des autres pc

        
      #si une machine est dispo, elle prend un fichier à traiter en plus 
      # on accede a une machine (fonction à part)
      # on lui fait faire son opération 
      # on check si nimporte laquelle des machines a fini 
      #si elle n'a pas fini on retchekera 1 minutes plus tard 
      # si elle a fini on lui donne un nouveau file a traiter
      #on s'arrete quand la liste est finie
      
        


#serveur host 
import socket 
from threading import Thread
from pickle import dumps

nombres de machines = sys.argv(3)

def servor(fichiers_CAD):     
    serversocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((socket.gethostname(), 80))           # creation du serveur 
    serversocket.listen(5)  # A MODIFIER 
    
    
    while fichiers_CAD:                                 #rester connecté en permanence jusu'a ce que la liste soit vide 
        client_socket, _ = serversocket.accept()   #pour accepter la connexion de clients et passer a cote de son adresse ip (irrelevant)
        client_thread= Thread(target= distribute_CAD_files, args(client_socket, fichiers_CAD))         #distribute_CAD_files fonction a créer, cette ligne
                        # sert à envoyer les arguments clientssocket et fichier cad  à la fonction distribute_CAD_files, qui s'executera en meme temps que la fonction principal
        client_thread.start()           # demarre le thread
    
           
    serversocket.close() 
    
    
def distribute_CAD_files(client_socket, fichiers_CAD):
    
    while True:         #envoyer une tache au client
        try:
            fichier_a_traiter = fichiers_CAD.pop(0) if fichiers_CAD else None  #on traite le premier element de la liste 
            client_socket.send(pickle.dumps(fichier_a_traiter))
            if fichier_a_traiter == None:
                break
    #il manque la confirmartion de taches au client et la gestion des erreurs
          