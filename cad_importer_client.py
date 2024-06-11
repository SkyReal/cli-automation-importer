# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 15:25:03 2024

@author: AxelBaillet
"""

 # CODE pour serveur client
 #il faurdra decomposer les fichiers 

import socket 
import pickle 

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_connect('je ne sais psa quoi mettre', 12345 )# lire plus de docs
    
    while True:
       task_data = client_socket.recv(4096)         # pour recevoir les donées du serveur ( pas  accurate pour le moment)
       task = pickle.loads(task_data)
       if task is None:
           break

       process_task(task)

       # Envoyer une confirmation de traitement au serveur
       client_socket.send("Task completed")

   client_socket.close()

        