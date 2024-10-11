# -*- coding: utf-8 -*-

# CAD AutoImporter lib

from subprocess import run
import json
import os

def create_smb_mapping(username, password, drive_letter, remote_path):
    
    powershell_identification_orders= f"""
    $user = "{username}"
    $securePassword = ConvertTo-SecureString "{password}" -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential ($user, $securePassword)
    New-SMBGlobalMapping -RemotePath "{remote_path}" -Credential $credential -LocalPath "{drive_letter}:"
    """

    print("pwsh \n", powershell_identification_orders)
    try:
        powershell_command_1 = run([ "pwsh", "-Command",  powershell_identification_orders], capture_output=True, text=True)
        print('This program mapped the repertory you asked for on the letter', drive_letter)
    except Exception as e:
        print("error :", e)
        print(powershell_command_1.stderr)
        return False
    print(powershell_command_1.stderr)
    print(powershell_command_1.stdout)
    return True

def remove_smb_mapping(drive_letter):
    
    pwsh_rmv = f"""
    Remove-SmbGlobalMapping -LocalPath {drive_letter}: -Force
    """
    try:
        powershell_remove_command = run(["pwsh", "-Command", pwsh_rmv], capture_output=True, text=True)
        print('Removed global mapping on the letter ', drive_letter)
    except Exception as e:
        print("error :", e)
        print(powershell_remove_command.stderr)
        return False
    print(powershell_remove_command.stdout)
    print(powershell_remove_command.stderr)
    print(pwsh_rmv)
    return True

def correct_mapping_letter(drive_letter):
    possible_letters = ['Z', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
    for letter in possible_letters:
        powershell_verification_orders = "Get-PSDrive -PSProvider FileSystem | Select-Object -ExpandProperty Name"
        powershell_command_verif = run([ "pwsh", "-Command",  powershell_verification_orders], capture_output=True, text=True)
        if letter not in powershell_command_verif.stdout:
            drive_letter = letter
    return  drive_letter

def load_credentials_file(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            credentials = json.load(file)
        
        # Extraction des champs 'login' et 'password'
        login = credentials.get("login")
        password = credentials.get("password")

        # Vérification des valeurs
        if login is None or password is None:
            raise ValueError("Le fichier JSON doit contenir les champs 'login' et 'password'.")

        return login, password

    except Exception as e:
        print(f"Erreur lors du chargement du fichier JSON : {e}")
        return None, None

def autocreate_mapping(file_path, remote_path):
    login, password = load_credentials_file(file_path)
    create_smb_mapping(login, password, "Z", remote_path)

def test():
    autocreate_mapping("creds.json", "\\\\192.168.0.2\\CAD Source")

def rpp(path1, path2, replacement):
    # Normaliser les chemins pour éviter les différences dues aux séparateurs
    path1 = os.path.normpath(path1)
    path2 = os.path.normpath(path2)

    # Vérifier si path1 est un préfixe de path2
    if path2.startswith(path1):
        # Remplacer la partie de path2 qui correspond à path1 par replacement
        new_path = path2.replace(path1, replacement, 1)
        return new_path
    else:
        return path2  # Retourner path2 sans modification si path1 n'est pas trouvé


def load_config_file(JSON_file):
    try:
        with open(JSON_file, 'r') as file:
            config_files_dictionnaire = json.load(file)

        # Extraire les données du fichier JSON
        path_CLI_local = config_files_dictionnaire.get("path_cli")
        if path_CLI_local is None:
            print('path_cli is missing in the config file.')
            path_CLI_local = None

        new_XRCENTER_address = config_files_dictionnaire.get("XRCENTER", '')

        extensions_available = config_files_dictionnaire.get("extensions", [])
        if not extensions_available:
            print('You have to put some extensions in the config files')
        else:
            for ext in extensions_available:
                if not ext.startswith('.'):
                    extensions_available = []  # Invalidate if any extension is invalid
                    break

        share_path = config_files_dictionnaire.get("share_path", '')
        if share_path == '' or share_path == 'value_to_fill':
            print('The share path must be \\\\IP_address\\share_name. Don\'t forget to double your backslashes as you are working with a JSON.')

        # Manipulation du fichier xrcenter_config_file pour obtenir l'ancienne base address
        base_address = ''
        xrcenter_config_file = "C:\\ProgramData\\Skydea\\xrcenter-cmd\\xrcenter-cmd.json"
        try:
            with open(xrcenter_config_file, 'r') as xrcenter_file:
                xrcenter_dictionary = json.load(xrcenter_file)
                base_address = xrcenter_dictionary.get("XRCenter", {}).get("BaseAddress", '')

            # Mise à jour de la nouvelle base address
            with open(xrcenter_config_file, 'w') as xrcenter_file_reopened:
                xrcenter_dictionary["XRCenter"]["BaseAddress"] = new_XRCENTER_address
                json.dump(xrcenter_dictionary, xrcenter_file_reopened, indent=4)
        except Exception as e:
            print(e)
            base_address = ''  # Si erreur, retourner une chaîne vide

    except Exception as e:
        print(e)
        return None, '', [], '', ''  # Valeurs par défaut en cas d'échec

    # Retourner les résultats sous forme de tuple
    return path_CLI_local, new_XRCENTER_address, extensions_available, base_address, share_path
