# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 16:06:18 2024

@author: AxelBaillet
"""

from wakeonlan import send_magic_packet
import os 

# wake on lan


#pour un seul pc 


# attention, seulement si le pc est eteint 
def wake_pc(ip_address):
    send_magic_packet('', ip_address=ip_address)
    return

def find_client_path(program):
    if os.path.exists(program):
        return os.path.abspath(program)
    else:
        print('Error, the client program is not on this computer')
        return None

def main():
    return