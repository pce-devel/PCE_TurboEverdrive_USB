# SendTED <COM port> <filename>
#
# Send file to Turbo Everdrive
#
import sys
import os
import serial

if len(sys.argv) <= 2:
    print()
    print("Bad paramaters entered")
    print("Usage: SendTED <COM port> <filename>")
    exit()

comport = sys.argv[1]
print("Using serial port:", comport)

# try to open serial port
#
try:
    ser = serial.Serial(comport, 9600, timeout=1)
except:
    print("Couldn't open serial port", comport)
    exit(1)

# Grab data from binary file to send
#
f = open(sys.argv[2], "rb") 
data = f.read()
f.close()

# now for Turbo Everdrive protocol:
#

# This seems to query the port for an Everdrive
#
ser.write(b'\x2A') 
ser.write(b'\x74') 
ser.flush()

# Everdrive responds with 0x6B (TurboEverDrive anyway)
#
byte = ser.read(1)
if (byte != b'\x6B'):
    print("Turbo Everdrive not responding")
    ser.close()
    exit()

# Now for the "send file" command:
#
ser.write(b'\x2A') 
ser.write(b'\x67') 
ser.flush()

block_start = 0
file_end = len(data)
blocks_sent = 0

# And the loop for sending data
#
# Note 1: Data is sent in 8KB blocks; must be padded if incomplete
# Note 2: 0x2B means there are more blocks coming; 0x2D 0x2D means "done"
#
while ((file_end - block_start) >= 8192):
    ser.write(data[block_start:block_start+8192])
    block_start += 8192
    blocks_sent += 1
    if ((blocks_sent % 8) == 0):
        print(".",end='',flush=True)
    if (file_end > block_start):
        ser.write(b'\x2B')

if (file_end > block_start):
    data += "\0" * (8192 - (file_end - block_start) )
    ser.write(data[block_start:block_start+8192])

ser.write(b'\x2D') 
ser.write(b'\x2D') 
ser.flush()

ser.close()

