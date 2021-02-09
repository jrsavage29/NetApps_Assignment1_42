#!/usr/bin/env python3
import sys

from ServerKeys import ibmTextToSpeech_key
from ServerKeys import ibmTextToSpeech_url
from ServerKeys import wolframAPI_key

from ibm_watson import TextToSpeechV1
#Not currently sure if we need this but I included it just in case
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def main(argv):
    server_port = None
    socket_size = None

    #Take the list of arguments from the command line and parse them
    if len(argv) != 4: 
        #if we are missing arguments then we get an error output the correct usage    
        print("usage: client.py -sp <SERVER_PORT> -z <SOCKET_SIZE>")
        sys.exit(1) 
    #parsing the arguements and putting them into their respective variables
    for argpos in range(len(argv)):
        if argv[argpos] == '-sp': 
            server_port = argv[argpos + 1]
        elif argv[argpos] == '-z': 
            socket_size = argv[argpos + 1]  
    #Display what was parsed
    print("Server Port is " + str(server_port) + "\nSocket Size is " + str(socket_size) ) 



if __name__== "__main__":
    main(sys.argv[1:])