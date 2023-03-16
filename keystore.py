#!/usr/bin/env python3
import keyring
import argparse
def storepassword(service,username):

 
 
 with open('auth.txt') as fp:
    data=fp.readline()
    data = data.strip() 
 keyring.set_password(service, username, data)
 

def getpassword(service,username):
 password = keyring.get_password(service,username)
 return password