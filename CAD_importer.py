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
from time import time 
import json 
import openpyxl

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
    
def donnees_config_files(path_CLI_local):
    if len(sys.argv) !=3:    #le file n'a pas encore été défini  
        print(' il faut le chemin d un fichier json pour configurer les informations propres a votre machine que vous placerez en second argument, contenant \n ADRESSE_XRCENTER= \n ADRESSE_CLI=')
        return None
    else: 
        config_files = sys.argv[2]
        if config_files.lower().endswith('.json'):          # on vérifie qu'on nous donne un json
            print('votre fichier json est bien pris en compte')     
        else :
            print("erreur sur le fichier json en argument")
            return None
        file = open(config_files, 'r')
        config_files_dictionnaire = json.load(file)                                     #on convertit le json en dictionnaire 
        path_CLI_local = config_files_dictionnaire["adresse_cli"] 
        if (path_CLI_local == None): 
            print(' ADRESSE_XRCENTER est manquante dans le fichier de configuration.')
            return None
    return path_CLI_local
        

## verifier que la CLI est opérationnel  

def verif_CLI(path_CLI_local):
    commande_CLI_opti1= f'& "{path_CLI_local}" health ping'
    CLI_ope = subprocess.run(["Powershell", "-Command", commande_CLI_opti1], capture_output=True, text=True)
    if 'success' in CLI_ope.stdout.lower():                                #le XRCENTER se lance avec le chemin basique 
        print("CLI functional")
    else:                                                                       #on fait l'opération avec les paramètres que l'utilisateur a inséré
        print("Error : Is your CLI functional?")
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

def creation_workspace_deck(save_id_workspace, path_CLI_local):
    workspace_json={}
    print('Un nouveau workspace sera crée pour vos dossiers dans le Deck SkyReal')
    date = datetime.now().strftime("%Y-%m-%d %H:%M")                    ## le nom du workspace correspond à la date de sa création 
    creation_workspace= f'& "{path_CLI_local}" workspace create --name workspace_"{date}"'
    nouveau_workspace= subprocess.run(["Powershell", "-Command", creation_workspace], capture_output=True, text=True)
    workspace_json= json.loads(nouveau_workspace.stdout)
    save_id_workspace= workspace_json["EntityId"]
    if nouveau_workspace.stderr != '':   #on vérifie qu'il n'y a pas d'erreurs, à compléter plus tard
        print('il y a un problème avec le workspace')
        return None
    return save_id_workspace


## Chercher les paths des fichiers du dossier passé en argument



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
                if liste_fichiers[k].lower().endswith(extensions[i].lower()) == True :      #c'est un dossier CAD, on regarde son extension en minuscule pour le rendre insensible a la casse
                    fichiers_CAD.append(liste_fichiers[k])
                    break                                                   #on n'a pas besoin de regarder le reste des extensions
    if (fichiers_CAD == []):                                                # il n'y avait pas de fichiers à traiter
        print('Aucun fichier ne devait être traité')
        return False 
    return True


    

# Importer les fichiers scannés dans le CLI     



def import_fichier_CAD(time_record, save_id_workspace, path_CLI_local, fichier):
    start = time()
    commande_fichier_import= f'& "{path_CLI_local}"  cad import "{save_id_workspace}" "{fichier}"' #commande pour importer sur le deck
    import_final = subprocess.run(["Powershell", "-Command", commande_fichier_import], capture_output=True, text=True)
    end = time()
    temps_import= end - start
    if "failed" in import_final.stdout.lower() or "error" in import_final.stdout.lower():
            print(f'Le dossier "{fichier}"ne s est pas mis dans SkyReal')   
            time_record.append('error')
    else: 
        time_record.append(temps_import)                        #on mesure le temps de chaque import
    return
    

# importer le dossier complet
    
def import_dossiers_CAD(fichiers_CAD, save_id_workspace , path_CLI_local, time_record):
    print("vos dossiers vont être ajoutés à SkyReal")
    for k in range(0,len(fichiers_CAD)):
        import_fichier_CAD(time_record, save_id_workspace, path_CLI_local, fichiers_CAD[k])
    return True



def write_in_excel(fichiers_CAD, time_record):  #fichier .xlsx
    data_in_excel = []
    filename = 'resultats_import_CAD'
    filename += '.xlsx'
    for k in range(0, len(fichiers_CAD)):
        data_in_excel.append([fichiers_CAD[k], time_record[k]])
    workbook = openpyxl.Workbook()          # créer un nouveau workbook 
    sheet = workbook.active                 #prendre la sheet actuelle
    for row_index, row_data in enumerate(data_in_excel, start=1):        #on se balade dans les lignes à partir de la première
        for col_index, cell_data in enumerate(row_data, start=1):          #on se balade dans les colonnes à partir de la première
            sheet.cell(row=row_index, column=col_index, value=cell_data)            
    workbook.save(filename)   # on sauvegarde les données
    print(f"les données ont bien été écrites dans votre excel '{filename}'")
    return data_in_excel


   



def main():
    
    
    
    if not verif_dossier_a_traiter():
        return
    
     #path_dossier = "C:\\Users\\AxelBaillet\\Documents\\test2"
     #path_CLI_local = 'C:\\SkyRealSuite\\1.18\\XRCenterCLI\\Skr.XRCenter.Cmd.exe'
     # path_CLI_local ='C:\\SkyRealSuite\\1.18\\XRCenterCLI'
     
    path_dossier = sys.argv[1]
    path_CLI_local = None
    path_CLI_local = None
   
    path_CLI_local=donnees_config_files(path_CLI_local)
    if  path_CLI_local== None:
        print("error while trying to read config file")
        return
    
    if not verif_CLI(path_CLI_local):            # on arrete le programme en cas d'erreur 
        return 

    # if verif_CLI(path_CLI_local) == False:
    #     return
    
    liste_fichiers=[]
    fichiers_CAD = []
    save_id_workspace=''                    
    time_record= []
    
    save_id_workspace= creation_workspace_deck(save_id_workspace, path_CLI_local)
    
    if save_id_workspace== None  or save_id_workspace== '':
        print( 'error in the workspace creation')
        return
    
    if not scan_CAD(liste_fichiers, fichiers_CAD, path_dossier) :
        return
    
    print(fichiers_CAD)
    
    import_dossiers_CAD(liste_fichiers, save_id_workspace, path_CLI_local, time_record)

    data_in_excel=write_in_excel(fichiers_CAD, time_record)
    
    return 
    
main()   ## on execute la fonction 
    
    
    
    
    
    
 




