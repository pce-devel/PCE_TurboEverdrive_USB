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
inpdata = f.read()
f.close()

# flags for mappers for special games
#
sf2 = 0
populous = 0
pop_off = 0x1f26
pop_chk = bytes("POPULOUS", 'utf-8')

# Remove header if needed
#
block_start = 0
if (len(inpdata) % 8192) == 0:
    data = inpdata
else:
    if (len(inpdata) % 8192) == 512:
        data = inpdata[512:]
        print("Removing header")
    else:
        print("This is an odd size for a ROM file... are you sure it's OK ?")

# Make 3Mbit games into linear address space if needed
#
if (len(data) == 393216):
    tempdata = data
    data = tempdata[0:262144] + tempdata[0:262144] + tempdata[262144:]

# Set mapper flag for SF2 game
#
if (len(data) == 2621440):
    sf2 = 1

# Set mapper flag for Populous game
#
if (data[pop_off:pop_off+8] == pop_chk):
    populous = 1

# Now for Turbo Everdrive protocol:
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
    print("file end = ", file_end, ", block_start = ", block_start)
    data += b'\0' * (8192 - (file_end - block_start) )
    ser.write(data[block_start:block_start+8192])

# No banks of data to follow
#
ser.write(b'\x2D') 

print()
# Enable mappers (if any)
#
if (sf2 == 1):
    ser.write(b'\x73')
else:
    if (populous == 1):
        ser.write(b'\x70')

# End transmission
#
ser.write(b'\x2D') 
ser.flush()

ser.close()

