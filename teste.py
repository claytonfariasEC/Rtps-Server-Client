import binascii
import time
import bitstring


HEADER_SIZE = 12

version = 2
padding = 0
extension = 0
cc = 0
marker = 0
pt = 26 # MJPEG type
seqnumber = 1111 #seqnum = frameNbr
ssrc = 0
timestamp = int(time.time())


header = bytearray(HEADER_SIZE)

header = bitstring.BitArray(bytes=HEADER_SIZE)

header[0:2] = version
header[3] = padding
header[4] = extension
header[4:8] = cc
header[9] = marker

header[9:16] = pt
header[16:32] = seqnumber
header[32:64] = timestamp
header[64:96] = ssrc

print(version,padding,extension,cc,marker,pt,seqnumber,timestamp,ssrc)

print("Header : ",header,version)




