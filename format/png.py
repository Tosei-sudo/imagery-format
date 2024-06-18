# coding: utf-8
import struct
import zlib
import numpy as np
import warnings

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
        self.bit_depth = ord(file.read(1))
        self.color_type = ord(file.read(1))
        self.compression_method = ord(file.read(1))
        self.filter_method = ord(file.read(1))
        self.interlace_method = ord(file.read(1))
        self.crc = struct.unpack('>I', file.read(4))[0]

    def get_bit_per_pixel(self):
        if self.color_type == 0:
            return self.bit_depth
        elif self.color_type == 2:
            return self.bit_depth * 3
        elif self.color_type == 3:
            return self.bit_depth
        elif self.color_type == 4:
            return self.bit_depth * 2
        elif self.color_type == 6:
            return self.bit_depth * 4

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
        
class PLTE:
    def read(self, file):
        self.length = struct.unpack('>I', file.read(4))[0]
        self.type = file.read(4)
        
        self.palette = []
        for i in range(0, self.length / 3):
            self.palette.append(struct.unpack('>BBB', file.read(3)))
        self.palette = np.array(self.palette)
        
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
            elif chunk_type == b'PLTE':
                chunk = PLTE()
                self.plte = chunk
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
    
    def paeth_predictor(self, a, b, c):
        p = a + b - c
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)
        
        if pa <= pb and pa <= pc:
            return a
        elif pb <= pc:
            return b
        else:
            return c
    
    def reverse_filter(self, img_data, bit_per_pixel):
        warnings.simplefilter('ignore')
        
        byte_per_pixel = bit_per_pixel / 8
        filtered_data = np.zeros((img_data.shape[0], img_data.shape[1] - 1), dtype = np.uint8)
        last_scan_data = np.zeros((1, img_data.shape[1] - 1), dtype = np.uint8)
        
        for row in range(0, len(img_data)):
            
            filter_type = img_data[row][0]
            scan_data = img_data[row][1:]
            
            if filter_type == 1:
                # 差分フィルタ
                for (col, data) in enumerate(scan_data):
                    left = scan_data[col - byte_per_pixel] if col >= byte_per_pixel else 0
                    scan_data[col] = data + left
            elif filter_type == 2:
                # 縦フィルタ
                scan_data = scan_data.astype(last_scan_data.dtype) + last_scan_data
            elif filter_type == 3:
                # 平均フィルタ
                for (col, up) in enumerate(last_scan_data):
                    left = scan_data[col - byte_per_pixel] if col > (byte_per_pixel - 1) else 0
                    scan_data[col] += ((up + left) / 2)
            elif filter_type == 4:
                for (col, up) in enumerate(last_scan_data):
                    left = scan_data[col - byte_per_pixel] if col >= byte_per_pixel else 0
                    up_left = last_scan_data[col - byte_per_pixel] if row > 0 and col >= byte_per_pixel else 0
                    scan_data[col] += self.paeth_predictor(up, left, up_left)
            
            scan_data = (scan_data % 256)
            
            last_scan_data = scan_data
            filtered_data[row] = scan_data
        return filtered_data
    
    def decompress(self):
        data = zlib.decompress(''.join(self.data))
        
        bit_per_pixel = self.ihdr.get_bit_per_pixel()
        row_size = 1 + (bit_per_pixel * self.ihdr.width) / 8
        
        data = np.fromstring(data, dtype = np.uint8).reshape(self.ihdr.height, row_size)
        img_data = self.reverse_filter(data, bit_per_pixel)

        if self.ihdr.color_type == 2:
            img_data = img_data.reshape(self.ihdr.height, self.ihdr.width, 3)
        elif self.ihdr.color_type == 3:
            palette = self.plte.palette
            img_data = palette[img_data]
        elif self.ihdr.color_type == 6:
            img_data = img_data.reshape(self.ihdr.height, self.ihdr.width, 4)
        
        import matplotlib.pyplot as plt
        plt.imshow(img_data)
        plt.show()