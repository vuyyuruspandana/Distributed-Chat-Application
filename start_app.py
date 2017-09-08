import socket, sys, threading
import json
import signal
import time
import os

def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if input("\nReally quit? (y/n)> ").lower().startswith('y'):
            print("yes")
            server.exit()
            sys.exit(0)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here    
    signal.signal(signal.SIGINT, exit_gracefully)

def run_program():
    while True:
        time.sleep(1)
        print("a")

if __name__ == '__main__':
    sys.tracebacklimit = 0
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)

    print("In my new app")
    os.system("start cmd /c py router_obj.py")
    while True:
        msg = input("Create server(s)/client(c):")
        if msg == 's':
            os.system("start cmd /c py server_obj.py")
        elif msg == 'c':
            os.system("start cmd /c py client_obj.py")
        elif msg == 'q':
            break
        else:
            print("invalid input")

    print("Exiting program")
