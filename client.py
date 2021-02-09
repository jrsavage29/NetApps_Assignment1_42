#!/usr/bin/env python3
import sys
import getopt

from ClientKeys import tweepyAPI_key

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



if __name__== "__main__":
    main(sys.argv[1:])