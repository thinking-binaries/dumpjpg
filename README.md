# dumpjpg

Dump a jpeg file into record segments.

This is a simple diagnostic tool that reads and parses a .jpg file, and
dumps it into separate record segments, in order to analyse the content
for the purposes of reliable record transfer over an unreliable link.


# File format

JPG images are encapsulated in a streamed record format, where an FF byte
marks a record segment. The byte after the FF defines the record type.
This is part of the JFIF standard defined [here](https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format)

The full JPEG format, along with encapsulation, is defined [here](https://docs.fileformat.com/image/jpeg/)

JPEG details such as the compression and encoding is well defined [here](https://en.wikipedia.org/wiki/JPEG)

Record segments are not length byte preceeded and many can be variable length,
so a record segment end is detected when another FF nn sequence occurs.

If an FF appears in the data stream, it is byte stuffed to FF 00, and because
there is no 00 record type, this protects the FF. To decode the stream, any
sequence of FF 00 should be compressed back to FF as a data payload byte.

Some record types have a single nibble of data in the low nibble. You can find
the record types defined in the above file format document.

The contents of the record segments are varied, some metadata occurs first,
some coefficients and huffman coding tables occur, and the pixel data is then
sent as an image segment, compressed using huffman coding and biased and
coded in various ways using the previous record matrixes. 

The image data is sent in a diagonal zig-zag from the top left corner to the 
bottom right corner, and thus if you loose the end of a file, you can still
decode and display the top left square that you have received.

Invalid FF nn sequences, and the lack of an FF nn sequence in the first two
bytes will be detected by any decoder as an invalid file.

For details about the exact contents of the huffman and coefficient tables,
see the [wikipedia page](https://en.wikipedia.org/wiki/JPEG)

# Using this tool as-is

The first parameter to the script is the name of the file to decode. 
It sends the decode to stdout, which might be the console screen, or it
can be redirected to a file with the standard redirection operator.

```python
python3 dumpjpg.py myimage.jpg > myimage.decode
```

# Using this tool inside other programs

The real purpose of this tool was first to understand the encapsulation format,
but ultimately to provide a building block for writing a transmit and receive
system that sends JPG data from an ArduCam over a RFM69 433MHz short range
wireless radio system.

In transferring JPG data where you don't have a back-channel (i.e. your
receiver has no way to send a 'please resend' message back), some form
of forward error correction is required, specifically to protect the metadata
at the start of the binary stream; such as sending those records multiple
times in case damage occurs in one or more of them.

If you detect that some of the image data has been lost, the hope is that
there is enough of a data protocol wrapping the transfer such that you
know how many bytes have been lost and you can just insert zeros, and
any JPEG viewer will still be able to make sense of the data. If you don't
know how much data was lost, just ignoring lost data will give you a skewed
image, but we suspect based on initial testing that it will still be mostly
viewable still.

The precise method of how you do that, is up to you.

# Useful notes and ideas

1. In a jpg captured on a Mac, there are multiple RSTn records after every
few bytes. We suspect those are there so that the distance between any
known sync point is kept to a minimum. This might be a useful technique
when transferring image data over a simplex (one way) unreliable link, in
that the transmitter could send any headers multiple times for resilience,
then it could choose to re-packetise data on the boundaries that it wants to
use so that each payload fits inside a single radio packet. 

2. A jpg captured from a Mac vs a jpg captured from an Arducam, follow the
same encapsulation protocol, but the Mac has a lot more application specific
data. If you strip this application specific data, the image is still valid.

3. Arducam sends one huge image segment, but a transmitter could re form that into
packets of 60 bytes each, prepend a header with a sequence number and add
a checksum or crc, then transmit that as a single radio payload. The receiver
would then be able to re-sync on packet loss to a useful boundary. Note you
need to allow enough space in the payload for byte-stuffed FF's, as an FF
in the image data gets stuffed into FF 00. But due to absence of any length
bytes in the protocol, your sender could easily insert RSTn records at any
arbitrary position. Note also there are 8 RSTn types RST0..RST7, so these
could be cycled round 0,1,2,3,4,5,6,7->0,1,... to form a simple sequence
number, perhaps.

# References


[JPEG picture encoding](https://en.wikipedia.org/wiki/JPEG)

[JFIF interchange format](https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format)

[JPEG and encapsulation](https://docs.fileformat.com/image/jpeg/)

David Whale

@whaleygeek

14 Dec 2022




