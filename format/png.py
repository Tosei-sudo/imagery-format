# coding : utf-8
import struct
import zlib
import numpy as np

class FileHeader:
    def read(self, file):
        self.high_bit = file.read(1)
        self.format = file.read(3)
        self.not_convert_unix = file.read(2)
        
        self.dummy_end_of_line = file.read(1)
        self.not_convert_ms_dos = file.read(1)

class IHDR:
    def read(self, file):
        self.length = struct.unpack('>I', file.read(4))[0]
        self.type = file.read(4)
        self.width = struct.unpack('>I', file.read(4))[0]
        self.height = struct.unpack('>I', file.read(4))[0]
        self.bit_depth = file.read(1)
        self.color_type = file.read(1)
        self.compression_method = ord(file.read(1))
        self.filter_method = ord(file.read(1))
        self.interlace_method = ord(file.read(1))
        self.crc = struct.unpack('>I', file.read(4))[0]

class gAMA:
    def read(self, file):
        self.length = struct.unpack('>I', file.read(4))[0]
        self.type = file.read(4)
        self.gamma = struct.unpack('>I', file.read(4))[0]
        self.crc = struct.unpack('>I', file.read(4))[0]

class cHRM:
    def read(self, file):
        self.length = struct.unpack('>I', file.read(4))[0]
        self.type = file.read(4)
        self.white_point_x = struct.unpack('>I', file.read(4))[0]
        self.white_point_y = struct.unpack('>I', file.read(4))[0]
        self.red_x = struct.unpack('>I', file.read(4))[0]
        self.red_y = struct.unpack('>I', file.read(4))[0]
        self.green_x = struct.unpack('>I', file.read(4))[0]
        self.green_y = struct.unpack('>I', file.read(4))[0]
        self.blue_x = struct.unpack('>I', file.read(4))[0]
        self.blue_y = struct.unpack('>I', file.read(4))[0]
        self.crc = struct.unpack('>I', file.read(4))[0]

class bKGD:
    def read(self, file):
        self.length = struct.unpack('>I', file.read(4))[0]
        self.type = file.read(4)
        if self.length == 1:
            self.index = struct.unpack('>B', file.read(1))[0]
        elif self.length == 2:
            self.index = struct.unpack('>H', file.read(2))[0]
        elif self.length == 6:
            self.red = struct.unpack('>H', file.read(2))[0]
            self.green = struct.unpack('>H', file.read(2))[0]
            self.blue = struct.unpack('>H', file.read(2))[0]
        self.crc = struct.unpack('>I', file.read(4))[0]

class tIME:
    def read(self, file):
        self.length = struct.unpack('>I', file.read(4))[0]
        self.type = file.read(4)
        self.year = struct.unpack('>H', file.read(2))[0]
        self.month = struct.unpack('>B', file.read(1))[0]
        self.day = struct.unpack('>B', file.read(1))[0]
        self.hour = struct.unpack('>B', file.read(1))[0]
        self.minute = struct.unpack('>B', file.read(1))[0]
        self.second = struct.unpack('>B', file.read(1))[0]
        self.crc = struct.unpack('>I', file.read(4))[0]

class tEXt:
    def read(self, file):
        self.length = struct.unpack('>I', file.read(4))[0]
        self.type = file.read(4)
        data = file.read(self.length).split('\x00')
        self.keyword = data[0]
        self.text = data[1]
        self.crc = struct.unpack('>I', file.read(4))[0]

class IDAT:
    def read(self, file):
        self.length = struct.unpack('>I', file.read(4))[0]
        self.type = file.read(4)
        self.data = file.read(self.length)
        self.crc = struct.unpack('>I', file.read(4))[0]
        
class Chunk:
    def read(self, file):
        self.length = struct.unpack('>I', file.read(4))[0]
        self.type = file.read(4)
        self.data = file.read(self.length)
        self.crc = struct.unpack('>I', file.read(4))[0]
        
class PNG:
    def read(self, file):
        self.header = FileHeader()
        self.header.read(file)
        
        self.data = []
        
        self.chunks = []
        while True:
            chunk_type = file.next(4, 4)
            
            if chunk_type == b'IHDR':
                chunk = IHDR()
                self.ihdr = chunk
            elif chunk_type == b'gAMA':
                chunk = gAMA()
                self.gAMA = chunk
            elif chunk_type == b'cHRM':
                chunk = cHRM()
                self.cHRM = chunk
            elif chunk_type == b'bKGD':
                chunk = bKGD()
                self.bKGD = chunk
            elif chunk_type == b'tIME':
                chunk = tIME()
                self.tIME = chunk
            elif chunk_type == b'tEXt':
                chunk = tEXt()
            elif chunk_type == b'IDAT':
                chunk = IDAT()
            else:
                chunk = Chunk()
            chunk.read(file)

            if chunk_type == b'IDAT':
                self.data.extend(chunk.data)
            
            self.chunks.append(chunk)
            
            if chunk.type == b'IEND':
                break
        
        self.decompress()
    
    def decompress(self):
        data = zlib.decompress(''.join(self.data))
        data = np.fromstring(data, dtype = np.uint8)
        data = data.reshape(self.ihdr.height, (self.ihdr.width * 4) + 1)
        
        data = data[:, 1:]
        data = data.reshape(self.ihdr.height, self.ihdr.width, 4)
        print data.shape
        
        # convert to RGBA
        img_data = np.zeros((self.ihdr.height, self.ihdr.width, 3), dtype = np.uint8)
        img_data[:, :, 0] = data[:, :, 0]
        img_data[:, :, 1] = data[:, :, 1]
        img_data[:, :, 2] = data[:, :, 2]
        
        
        import matplotlib.pyplot as plt
        plt.imshow(img_data)
        plt.show()