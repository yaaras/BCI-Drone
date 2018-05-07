# Imports
import serial, time
import argparse
import math
from pythonosc import dispatcher
from pythonosc import osc_server

# Constants
rightMin = 80
rightMax = 120

port = "COM8"
ser = serial.Serial(port, 9600)

counterr = 0
vals = []

def avg(arr):
    sum1 = 0
    for val in arr:
        sum1 += val
    return sum1 / len(arr)

# Translate from muse signals range to arduino
def translate(value):
    rightSpan = rightMax - rightMin
    return rightMin + (value * rightSpan)

def communicate(val):
    global vals
    global counterr
    counterr += 1
    if counterr % 10 != 0:
        vals.append(val)
        return
    
    print(counterr)
    print("Sending: ", int(avg(vals)))
    try:
        ser.write(bytes(str(int(avg(vals))) + "\n", "ascii"))
    except Exception as ex:
        print(ex)

    vals = []

def eeg_handler1(unused_addr, args, ch1):#, ch2, ch3, ch4):
    # Communicate to Arduino
    val = translate(ch1)
    communicate(val)

if __name__ == "__main__":
    
    # Connect to server
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="127.0.0.1",
                        help="The ip to listen on")
    parser.add_argument("--port",
                        type=int,
                        default=5001,
                        help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/debug", print)
    dispatcher.map("/muse/elements/experimental/mellow", eeg_handler1, "EEG")

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

    

