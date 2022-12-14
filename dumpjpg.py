#! /usr/bin/env python3

# dumpjpg.py  14/12/2022  D.J.Whale

FILENAME = "photo13.png"

FLAGS = {
    "D8": "SOI: Start of image",                # no payload
    "C0": "SOF0: Start of frame",               # variable size
    "C2": "SOF2: Start of frame",               # variable size
    "C4": "DHT: define huffman tables",         # variable size
    "D9": "EOI: End Of Image",                  # no payload
    "DB": "DQT: Define Quantization Table(s)",  # variable size
    "DD": "DRI: Define Restart Interval",       # 4 bytes
    "DA": "SOS: Start Of Scan",                 # variable size
    "D*": "RSTn: Restart",                      # no data, n=0..7
    "E*": "APPn: Application specific",         # variable size n=0..F
    "FE": "COM: Comment",                       # variable size
}

def get_byte(f) -> int:
    b = f.read(1)
    if len(b) == 0: exit(0)  # EOF
    b = b[0]
    return b

def marker_flag(flag:int) -> None:
    global payload_len
    payload_len = 0
    hexstr = "%02X" % flag
    try:
        # lookup specific marker flag
        print("\nsegment: FF %02X %s" % (flag, FLAGS[hexstr]))
    except KeyError:
        # lookup wildcarded marker flag
        hexstr = hexstr[0] + '*'
        try:
            print("\nsegment: FF %02X %s" % (flag, FLAGS[hexstr]))
        except KeyError:
            print("\nsegment UNKNOWN: FF %02X" % flag)

payload_len = 0
PAYLOAD_MAX = 32

def payload(data:int) -> None:
    global payload_len
    print("%02X " %data, end="")
    payload_len = (payload_len + 1) % PAYLOAD_MAX
    if payload_len == 0:
        print()

def decode(filename:str) -> None:
    with open(filename, "rb") as f:
        # make sure we are in sync with JPEG segment structure

        # decode marker and flag
        ff = get_byte(f)
        # expect FF nn as a segment
        if ff != 0xFF:
            exit("not a JPEG file, no FF segment marker")
        # segment type
        flag = get_byte(f)
        marker_flag(flag)

        # we are now in sync
        while True:
            # decode variable length data, or no data
            data = get_byte(f)
            # if not FF, it is definitely data
            if data != 0xFF:
                payload(data)
            else:
                # it might be stuffed FF, or real FF
                data2 = get_byte(f)
                if data2 == 0x00:
                    # stuffed data
                    payload(data2)
                else:
                    # real FF marker, resync
                    marker_flag(data2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 0:
        exit("usage: dumpjpg.py <filename.jpeg>")
    decode(sys.argv[1])

# END
