#!/usr/bin/env python3
import sys
import socket
import pickle
import wolframalpha
import hashlib
import os

from cryptography.fernet import Fernet
from playsound import playsound

from ServerKeys import ibmTextToSpeech_key
from ServerKeys import ibmTextToSpeech_url
from ServerKeys import wolframAPI_key

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def main(argv):
    server_port = None
    socket_size = None

    # Take the list of arguments from the command line and parse them
    if len(argv) != 4:
        # if we are missing arguments then we get an error output the correct usage
        print("usage: server.py -sp <SERVER_PORT> -z <SOCKET_SIZE>")
        sys.exit(1)
        # parsing the arguements and putting them into their respective variables
    for argpos in range(len(argv)):
        if argv[argpos] == '-sp':
            server_port = argv[argpos + 1]
        elif argv[argpos] == '-z':
            socket_size = argv[argpos + 1]
            # Display what was parsed
    print("Server Port is " + str(server_port) + "\nSocket Size is " + str(socket_size))

    # setup of IBM authenticators
    api = IAMAuthenticator(ibmTextToSpeech_key)
    text_to_speech = TextToSpeechV1(authenticator=api)
    text_to_speech.set_service_url(ibmTextToSpeech_url)

    # setup wolfram alpha api key
    clientWolf = wolframalpha.Client(wolframAPI_key)

    # Setup connection to client
    host = ''
    port = int(server_port)
    size = int(socket_size)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("[Server 01] - Created socket at " + str(s.getsockname()[0]) + " on port " + str(server_port))
    s.listen()
    while True:
        print("[Server 02] - Listening for client connections")
        client, address = s.accept()
        client_ip, client_port = address
        print("[Server 03 ] - Accepted client connection from " + str(client_ip) + " on port " + str(client_port))

        # receiving pickled data from client
        pickled_data = client.recv(size)
        # print(pickled_data)
        # unpickling data
        data = pickle.loads(pickled_data)
        print("[Server 04] - Received data: ", data)
        if data:
            # getting data from the tuple payload
            question_key, encrypted_question, question_check_sum = data

            print("[Server 05] - Decrypt Key: ", question_key)
            # print("Question:")
            # print("key: ", question_key, "\nEncrypted question: ", encrypted_question, "\nCheck sum", question_check_sum)
            # check sum to verify with the received one
            verify_check_sum = hashlib.md5(encrypted_question)
            # print(verify_check_sum.hexdigest())
            if verify_check_sum.hexdigest() == question_check_sum:
                # fernet instance for encoding and decoding
                fernet = Fernet(question_key)
                question = fernet.decrypt(encrypted_question).decode()
                print("[Server 06] - Plain Text: ", question)
                # create query audio file and play it
                with open("Question.mp3", "wb") as audiofile:
                    audiofile.write(
                        text_to_speech.synthesize(question,
                                                  voice='en-US_AllisonV3Voice',
                                                  accept='audio/mp3'
                                                  ).get_result().content)
                print("[Server 07] - Speaking Question: ", question)
                playsound('Question.mp3')
                os.remove('Question.mp3')

                # generate response to question through wolfram and display it to the console
                print("[Server 08] - Sending question to Wolframalpha")
                response = clientWolf.query(question)
                answer = next(response.results).text
                print("[Server 09] - Received answer from Wolframalpha: ", answer)

                # encrypt the answer
                answer_key = fernet.generate_key()
                print("[Server 10] - Encryption Key: ", answer_key)
                encrypted_answer = fernet.encrypt(answer.encode())
                print("[Server 11] - Cipher Text: ", encrypted_answer)
                answer_check_sum = hashlib.md5(encrypted_answer)
                print("[Server 12] - Generated MD5 Checksum: ", answer_check_sum)
                # tuple payload to send to server
                pickle_tuple = (answer_key, encrypted_answer, answer_check_sum.hexdigest())
                print("[Server 13] - Answer payload: ", pickle_tuple)

                # print("key: ", answer_key, "\nEncrypted Answer: ", encrypted_answer, "\nCheck sum: ", answer_check_sum.hexdigest())
                # pickling the data
                pickle_string = pickle.dumps(pickle_tuple)
                print("[Server 14] - Sending answer: ", pickle_string)
                # sending the pickle to the server
                client.send(pickle_string)
        client.close()


if __name__ == "__main__":
    main(sys.argv[1:])