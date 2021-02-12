#!/usr/bin/env python3
import sys
import socket
import pickle
import wolframalpha
import hashlib
import os
from playsound import playsound

from ServerKeys import ibmTextToSpeech_key
from ServerKeys import ibmTextToSpeech_url
from ServerKeys import wolframAPI_key

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def main(argv):
    server_port = None
    socket_size = None

    #Take the list of arguments from the command line and parse them
    if len(argv) != 4: 
        #if we are missing arguments then we get an error output the correct usage    
        print("usage: server.py -sp <SERVER_PORT> -z <SOCKET_SIZE>")
        sys.exit(1) 
    #parsing the arguements and putting them into their respective variables
    for argpos in range(len(argv)):
        if argv[argpos] == '-sp': 
            server_port = argv[argpos + 1]
        elif argv[argpos] == '-z': 
            socket_size = argv[argpos + 1]  
    #Display what was parsed
    print("Server Port is " + str(server_port) + "\nSocket Size is " + str(socket_size) ) 

    #setup of IBM authenticators
    api = IAMAuthenticator(ibmTextToSpeech_key)
    text_to_speech = TextToSpeechV1(authenticator = api)
    text_to_speech.set_service_url(ibmTextToSpeech_url)

    #setup wolfram alpha api key
    clientWolf = wolframalpha.Client(wolframAPI_key)

    #Setup connection to client
    host = 'localhost'
    port = 50000
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen()
    while True:
        print("Server waiting for connection...")
        client, address = s.accept()
        print("Client connected from", address)
        
        data = client.recv(size)
        print (b'Received from client: ' + data)
        if data:
            question = data.decode()
            
            #create query audio file and play it
            with open("Question.mp3", "wb") as audiofile:
                audiofile.write(
                    text_to_speech.synthesize(question, 
                    voice = 'en-US_AllisonV3Voice',
                    accept = 'audio/mp3'
                ).get_result().content)
            playsound('Question.mp3')
            os.remove('Question.mp3')

            #generate response to question through wolfram and display it to the console
            response = clientWolf.query(question)
            answer = next(response.results).text
            # print(answer)

            client.send(str(answer).encode())
        client.close()


if __name__== "__main__":
    main(sys.argv[1:])