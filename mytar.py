import sys
import os
from buf import BufferedFdWriter, BufferedFdReader
        
class Framer:
    def __init__(self, writeFd):
        self.writeFd = writeFd

    def frame(self, byteArray):
        byteWriter = BufferedFdWriter(self.writeFd)
        for b in byteArray:
            byteWriter.writeByte(b)
        byteWriter.flush()
            

class UnFramer:
    def __init__(self, readFd):
        self.readFd = readFd

    def unFrame(self):
        byteReader = BufferedFdReader(self.readFd)
        bArray = bytearray()
        while not (retb := byteReader.readByte()) == None:
            bArray.append(retb)
        if not bArray:
            return None
        return bArray

class TarWriter:
    def __init__(self, writerFd):
        self.writerFd = writerFd

    def storeFile(self, fileName):
        fr = Framer(self.writerFd)

        f = open(fileName, "rb")
        contents = f.read()
        
        fr.frame(fileName.encode())
        
        fr.frame(contents)

class TarReader:
    def __init__(self, readFd):
        self.readFd = readFd

    def unTar(self):
        ufr = UnFramer(self.readFd)
        fileName = "default"
        byteAs = (ufr.unFrame()).split(b"\e")
        byteAs = byteAs[:-1]
        for i in range(0, len(byteAs), 2):
            fileName = byteAs[i].decode()
            contents = byteAs[i+1]
            f = open(fileName, "wb")
            f.write(contents)
        f.close

#main

command = sys.argv[1]

if command == "c":
    tw = TarWriter(os.O_WRONLY)
    filenames = sys.argv[2:]
    for filen in filenames:
        tw.storeFile(filen)
if command == "x":
    archive = open("archive", "wb")
    oDirContents = sys.stdin.buffer.read()
    archive.write(oDirContents)
    archive.close()
    fd = os.open("archive", 0)
    tr = TarReader(fd)
    tr.unTar()