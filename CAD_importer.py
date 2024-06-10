# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 11:55:57 2024

@author: AxelBaillet
"""

## penser a  lancer python en ADMIN 
##cela ne marchera qu'en local pour le moment 
# les paths CLI par défaut sont ils vbraiment ceux par défaut?
## bibliothèques

import sys
import os 
import subprocess
from datetime import datetime
import json 
 
extensions = [".CATPart", ".CATProduct",".CGR","CATProcess",".model","3dxml",".plmxml",".jt", ".prt",".asm",".ifc",".sldprt",".sldasm",".stp", ".step",".stl",".iam",".ipt",".x_t",".dwg"]
## certaines extensions sont en train d'être ajoutées : .fbx , .dgn . 


 ## Il faut un config files pour faire marcher le programme


def verif_dossier_a_traiter():   # verifier que notre deuxieme argument est valide
    if len(sys.argv)<2:
        print( 'vous devez mettre en premier argument le chemin du dossier ou du fichier à traiter')
        return False
    else:
        if os.path.exists(sys.argv[1]) == False:
            print('le chemin n est pas valable')
            return False 
        if os.path.isdir(sys.argv[1]) == False and  os.path.isfile(sys.argv[1]) == False: 
            return False
    return True
    
def donnees_config_files( path_CLI_local , path_XRCENTER_local ):
    if len(sys.argv) !=3:    #le file n'a pas encore été défini  
        print(' il faut le chemin d un fichier json pour configurer les informations propres a votre machine que vous placerez en second argument, contenant \n ADRESSE_XRCENTER= \n ADRESSE_CLI=')
        return None
    else: 
        config_files = sys.argv[2]
        if config_files.lower().endswith('.json'):          # on vérifie qu'on nous donne un json
            print('votre fichier est bien pris en compte')     
        else :
            print("le fichier n est pas pris en compte")
            return None
        file = open(config_files, 'r')
        print("file ", file)
#        with open(config_files, 'r') as file:                                               #on ouvre le fichier annexe
        config_files_dictionnaire = json.load(file)                                     #on convertit le json en dictionnaire 
        print(config_files_dictionnaire)
    #  config_files_dictionnaire = {key.lower(): value for key, value in config_files_dictionnaire.items()}            #on met tout en minuscule au cas ou le client ne respecte pas la police a la lettre
        path_XRCENTER_local = config_files_dictionnaire["adresse_xrcenter"] 
        print( "path_XRCENTER_local", path_XRCENTER_local)
        path_CLI_local =  config_files_dictionnaire["adresse_cli"]
        if (path_XRCENTER_local == None) or (path_CLI_local == None): 
            print('Les clés ADRESSE_XRCENTER ou ADRESSE_CLI sont manquantes dans le fichier de configuration.')
            return None
    return path_XRCENTER_local
        

## verifier que le XRcenter est opérationnel  

def verif_XRCENTER(path_XRCENTER_local):
    commande_XRCENTER_opti1= f'& "{path_XRCENTER_local}" health ping'
    print("commande xrcenter ", commande_XRCENTER_opti1)
    XRCENTER_ope = subprocess.run(["Powershell", "-Command", commande_XRCENTER_opti1], capture_output=True, text=True)
    if 'success' in XRCENTER_ope.stdout.lower():                                #le XRCENTER se lance avec le chemin basique 
        print("XRCenter opérationnel")
    else:                                                                       #on fait l'opération avec les paramètres que l'utilisateur a inséré
        print("Erreur : veuillez lancer votre XRCenter avant de démarrer ce programme")
        return False
    return True

## les adresses doivent être mises avec des double backslash, est ce un problème?


## verifier que le CLI  est opérationnel  

# def verif_CLI(path_CLI_local): 
#     commande_CLI_opti1= f'cd "{path_CLI_local}"'                              #pour généraliser le programme pour tout emplacement de CLI        
#     CLI_ope = subprocess.run(["Powershell", "-Command", commande_CLI_opti1], capture_output=True, text=True)
#     if CLI_ope.stderr == "":
#         print("CLI opérationnel")
#         path_CLI_local = path_CLI1                                  ## on prend l'adresse par défaut
#     else:
#         print("Erreur sur la CLI : veuillez relancer le programme")
#         return False
#     return True

## créer un nouveau workspace

def creation_workspace_deck(save_id_workspace, path_XRCENTER_local):
    workspace_json={}
    print('Un nouveau workspace sera crée pour vos dossiers dans le Deck SkyReal')
    print("path_XRCENTER_local", path_XRCENTER_local)
    date = datetime.now().strftime("%Y-%m-%d %H:%M")                    ## le nom du workspace correspond à la date de sa création 
    creation_workspace= f'& "{path_XRCENTER_local}" workspace create --name workspace_"{date}"'
    nouveau_workspace= subprocess.run(["Powershell", "-Command", creation_workspace], capture_output=True, text=True)
    workspace_json= json.loads(nouveau_workspace.stdout)
    save_id_workspace= workspace_json["EntityId"]
    if nouveau_workspace.stderr != '':   #on vérifie qu'il n'y a pas d'erreurs, à compléter plus tard
        print('il y a un problème avec le workspace')
        return False
    return save_id_workspace


## Chercher les paths des fichiers du dossier passé en argument

liste_fichiers = []

def chercher_fichiers(liste_fichiers, path_dossier): 
    for path, directory, files in os.walk(f"{path_dossier}"):
       for file_name in files:
            file_path = os.path.join(path, file_name)                   # Obtenir le chemin absolu du fichier
            liste_fichiers.append(file_path)                            # Ajouter le chemin absolu à la liste
    return 

## scanner ces dossiers voir si il existe des fichiers cad 


def scan_CAD(liste_fichiers, fichiers_CAD, path_dossier):
    chercher_fichiers(liste_fichiers, path_dossier)
    if liste_fichiers == [] :                                               # Le dossier est vide 
        print('Le dossier est vide')
        return False
    else: 
        for k in range(0,len(liste_fichiers)):
            for i in range(0, len(extensions)):                             #on s'arrête s'il n'existe pas de fichers CAD
                if liste_fichiers[k].endswith(extensions[i]) == True :      #c'est un dossier CAD
                    fichiers_CAD.append(liste_fichiers[k])
                    break                                                   #on n'a pas besoin de regarder le reste des extensions
    if (fichiers_CAD == []):                                                # il n'y avait pas de fichiers à traiter
        print('Aucun fichier ne devait être traité')
        return False 
    return True

# Importer les fichiers scannés dans le CLI 


def import_dossiers_CAD(liste_fichiers, save_id_workspace , path_XRCENTER_local):
    print("vos dossiers vont être ajoutés à SkyReal")
    for k in range(0,len(liste_fichiers)):
        commande_fichier_import= f'& "{path_XRCENTER_local}"  cad import "{save_id_workspace}" "{liste_fichiers[k]}"' #commande pour importer sur le deck
        import_total = subprocess.run(["Powershell", "-Command", commande_fichier_import], capture_output=True, text=True)
    if "failed" in import_total.stdout.lower():
        print('Vos dossiers ne se sont pas mis dans SkyReal')   
        return False
    else:
        print('vos dossiers sont dans SkyReal')
    return True


      


def main():
    
    
    if not verif_dossier_a_traiter():
        return
    
     #path_dossier = "C:\\Users\\AxelBaillet\\Documents\\test2"
     #path_XRCENTER_local = 'C:\\SkyRealSuite\\1.18\\XRCenterCLI\\Skr.XRCenter.Cmd.exe'
     # path_CLI_local ='C:\\SkyRealSuite\\1.18\\XRCenterCLI'
     
    path_dossier = sys.argv[1]
    path_XRCENTER_local = None
    path_CLI_local = None
   
    path_XRCENTER_local=donnees_config_files(path_CLI_local , path_XRCENTER_local)
    if  path_XRCENTER_local== None:
        print("error while trying to read config file")
        return
    
    if not verif_XRCENTER(path_XRCENTER_local):            # on arrete le programme en cas d'erreur 
        return 

    # if verif_CLI(path_CLI_local) == False:
    #     return
    
    liste_fichiers=[]
    fichiers_CAD = []
    save_id_workspace=''                    
    
    if not creation_workspace_deck(save_id_workspace, path_XRCENTER_local):
        return
    
    if not scan_CAD(liste_fichiers, fichiers_CAD, path_dossier) :
        return
    
    print(fichiers_CAD)
    
    
    if not import_dossiers_CAD(liste_fichiers, save_id_workspace, path_XRCENTER_local):
        return
    
    return 
    
main()   ## on execute la fonction 
    
    
    
    
    
    





