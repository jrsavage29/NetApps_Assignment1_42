#!/usr/bin/env python3
import sys
import socket
import pickle
import wolframalpha
import hashlib
import os
import json
from playsound import playsound

from ClientKeys import tweepyAPI_key
from ClientKeys import tweepySecretAPI_key
from ClientKeys import tweepyAPIConsumer_key
from ClientKeys import tweepySecretAPIConsumer_key

from ClientKeys import ibmTextToSpeech_key
from ClientKeys import ibmTextToSpeech_url

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

def main(argv):
    server_ip = None
    server_port = None
    socket_size = None

    #Take the list of arguments from the command line and parse them
    if len(argv) != 6: 
        #if we are missing arguments then we get an error output the correct usage    
        print("usage: client.py -sip <SERVER_IP> -sp <SERVER_PORT> -z <SOCKET_SIZE>")
        sys.exit(1) 
    #parsing the arguements and putting them into their respective variables
    for argpos in range(len(argv)):
        if argv[argpos]  == '-sip': 
            server_ip = argv[argpos + 1] 
        elif argv[argpos] == '-sp': 
            server_port = argv[argpos + 1]
        elif argv[argpos] == '-z': 
            socket_size = argv[argpos + 1]  
    #Display what was parsed
    print( "Sever IP is " + str(server_ip) + "\nServer Port is " + str(server_port) + "\nSocket Size is " + str(socket_size) ) 

    #setup of IBM authenticators
    api = IAMAuthenticator(ibmTextToSpeech_key)
    text_to_speech = TextToSpeechV1(authenticator = api)
    text_to_speech.set_service_url(ibmTextToSpeech_url)

    #setup twitter authentication
    auth = OAuthHandler(tweepyAPIConsumer_key, tweepySecretAPIConsumer_key)
    auth.set_access_token(tweepyAPI_key, tweepySecretAPI_key)
    

    #setup tweepy api
    class listener(StreamListener):
        def on_data(self, data):
            # print(data)
            tweet_data = json.loads(data)
            parsed_data = tweet_data['text']
            tweet_question = parsed_data.strip("#ECE4564T15")
            question = tweet_question

            print("The tweet I received: ", question)
            #eventually want to parse this data and set the variable question equal to it (e.g. question = parsed twitter data)
            #Setup connection to server
            host = 'localhost'
            port = 50000
            size = 1024
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host,port))

            #Prepare query for wolfram to answer
            #question = input('What is your Question? ')

            s.send(question.encode())
            data = s.recv(size)
            answer = data.decode()
            print('Received from server: ', answer)
            #create answer audio file and play it
            with open("Answer.mp3", "wb") as audiofile:
                audiofile.write(
                    text_to_speech.synthesize(answer, 
                    voice = 'en-US_AllisonV3Voice',
                    accept = 'audio/mp3'
                ).get_result().content)
            playsound('Answer.mp3')
            os.remove('Answer.mp3')
            s.close()

            return True
        def on_error(self, status):
            print(status)

    #create twitter stream
    twitterStream = Stream(auth, listener())
    twitterStream.filter(track=["#ECE4564T15"]) 




if __name__== "__main__":
    main(sys.argv[1:])