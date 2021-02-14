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

from cryptography.fernet import Fernet

def main(argv):
    server_ip = None
    server_port = None
    socket_size = None

    # Take the list of arguments from the command line and parse them
    if len(argv) != 6:
        # if we are missing arguments then we get an error output the correct usage
        print("usage: client.py -sip <SERVER_IP> -sp <SERVER_PORT> -z <SOCKET_SIZE>")
        sys.exit(1)
        # parsing the arguements and putting them into their respective variables
    for argpos in range(len(argv)):
        if argv[argpos] == '-sip':
            server_ip = argv[argpos + 1]
        elif argv[argpos] == '-sp':
            server_port = argv[argpos + 1]
        elif argv[argpos] == '-z':
            socket_size = argv[argpos + 1]
            # Display what was parsed
    print("[Client 01] - Connecting to " + str(server_ip) + " on port " + str(server_port))

    # setup of IBM authenticators
    api = IAMAuthenticator(ibmTextToSpeech_key)
    text_to_speech = TextToSpeechV1(authenticator=api)
    text_to_speech.set_service_url(ibmTextToSpeech_url)

    # setup twitter authentication
    auth = OAuthHandler(tweepyAPIConsumer_key, tweepySecretAPIConsumer_key)
    auth.set_access_token(tweepyAPI_key, tweepySecretAPI_key)

    # setup tweepy api
    class listener(StreamListener):
        def on_data(self, data):
            # print(data)
            tweet_data = json.loads(data)
            parsed_data = tweet_data['text']
            tweet_question = parsed_data.strip("#ECE4564T15")
            question = tweet_question
            # generate the key from fernet
            key = Fernet.generate_key()
            # fernet instance for encoding and decoding
            fernet = Fernet(key)

            print("[Client 03] - New question found: ", question)
            print("[Client 04] - Generated Encryption Key: ", key)
            # eventually want to parse this data and set the variable question equal to it (e.g. question = parsed twitter data)
            # Setup connection to server
            host = server_ip
            port = int(server_port)
            size = int(socket_size)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))

            # encrypt data to send to server
            encrypted_question = fernet.encrypt(question.encode())
            print("[Client 05] - Cipher Text: ", encrypted_question)
            # check sum of question to send
            question_check_sum = hashlib.md5(encrypted_question)
            # tuple payload to send to server
            pickle_tuple = (key, encrypted_question, question_check_sum.hexdigest())
            print("[Client 06] - Question payload: ", pickle_tuple)
            # print("Question:")
            # print("Question: ", question, "\nkey: ", key, "\nEncrypt quest: ", encrypted_question, "\ncheck sum: ", question_check_sum.hexdigest())
            # pickling the data
            pickle_string = pickle.dumps(pickle_tuple)
            print("[Client 07] - Sending question: ", pickle_string)
            # sending the pickle to the server
            s.send(pickle_string)

            # receiving the pickled response from the server
            pickled_data = s.recv(size)
            # print(pickled_data)
            # unpickling data
            data = pickle.loads(pickled_data)
            print("[Client 08] - Received data: ", data)
            answer_key, encrypted_answer, answer_check_sum = data
            print("[Client 09] - Decrypt Key: ", answer_key)
            # print("Answer:")
            # print("key: ", answer_key, "\nEncrypted Answer: ", encrypted_answer, "\nCheck sum", answer_check_sum)
            # check sum to verify with the one received
            verify_check_sum = hashlib.md5(encrypted_answer)
            # print(verify_check_sum.hexdigest())
            if verify_check_sum.hexdigest() == answer_check_sum:
                answer = fernet.decrypt(encrypted_answer).decode()
                print("[Client 10] - Plain Text: ", answer)
                # create answer audio file and play it
                with open("Answer.mp3", "wb") as audiofile:
                    audiofile.write(
                        text_to_speech.synthesize(answer,
                                                  voice='en-US_AllisonV3Voice',
                                                  accept='audio/mp3'
                                                  ).get_result().content)
                print("[Client 11] - Speaking answer: ", answer)
                playsound('Answer.mp3')
                os.remove('Answer.mp3')
                s.close()
                print('[Client 02]- Listening for tweets from Twitter API that contain questions')
                return True

        def on_error(self, status):
            print(status)

    # create twitter stream
    print('[Client 02]- Listening for tweets from Twitter API that contain questions')
    twitterStream = Stream(auth, listener())
    twitterStream.filter(track=["#ECE4564T15"])


if __name__ == "__main__":
    main(sys.argv[1:])