# coding: utf-8
import struct
import numpy as np
import warnings
from scipy.fftpack import dct, idct

class APP0:
    def read(self, file):
        self.marker = struct.unpack('>H', file.read(2))[0]
        self.length = struct.unpack('>H', file.read(2))[0]
        self.identifier = file.read(5)
        self.version = file.read(2)
        self.units = file.read(1)
        self.x_density = struct.unpack('>H', file.read(2))[0]
        self.y_density = struct.unpack('>H', file.read(2))[0]
        self.x_thumbnail = ord(file.read(1))
        self.y_thumbnail = ord(file.read(1))
        
        thumbnail_size = (self.x_thumbnail * self.y_thumbnail) * 3
        if thumbnail_size > 0:
            self.thumbnail = file.read(thumbnail_size)

class APP1:
    def read(self, file):
        self.marker = struct.unpack('>H', file.read(2))[0]
        self.length = struct.unpack('>H', file.read(2))[0]
        self.identifier = file.read(6)
        self.exif = file.read(self.length - 8)

class SOF:
    def read(self, file):
        self.marker = struct.unpack('>H', file.read(2))[0]
        self.length = struct.unpack('>H', file.read(2))[0]
        self.precision = ord(file.read(1))
        self.height = struct.unpack('>H', file.read(2))[0]
        self.width = struct.unpack('>H', file.read(2))[0]
        self.components = ord(file.read(1))
        
        self.component = []
        for i in range(self.components):
            component = {}
            component['id'] = ord(file.read(1))
            component['sampling'] = ord(file.read(1))
            component['table'] = ord(file.read(1))
            self.component.append(component)

class SOS:
    def read(self, file):
        self.marker = struct.unpack('>H', file.read(2))[0]
        self.length = struct.unpack('>H', file.read(2))[0]
        self.components = ord(file.read(1))
        
        self.component = []
        for i in range(self.components):
            component = {}
            component['id'] = ord(file.read(1))
            component['table'] = ord(file.read(1))
            self.component.append(component)
        
        self.start = ord(file.read(1))
        self.end = ord(file.read(1))
        self.ah_al = ord(file.read(1))

class DHT:
    def read(self, file):
        self.marker = struct.unpack('>H', file.read(2))[0]
        self.length = struct.unpack('>H', file.read(2))[0]
        real_length = self.length - 2
        
        self.tables = []
        while real_length > 0:
            table = {}
            first_byte = ord(file.read(1))
            table['Tcn'] = first_byte >> 4
            table['id'] = first_byte & 0x0F
            
            table['count'] = np.frombuffer(file.read(16), dtype = np.uint8)
            
            table['symbol'] = np.empty(16, dtype = np.object)
            for i in range(16):
                if table['count'][i] > 0:
                    table['symbol'][i] = np.frombuffer(file.read(table['count'][i]), dtype = np.uint8)
            
            self.tables.append(table)
            real_length -= 17 + sum(table['count'])

class DQT:
    def read(self, file):
        self.marker = struct.unpack('>H', file.read(2))[0]
        self.length = struct.unpack('>H', file.read(2))[0]
        real_length = self.length - 2
        
        self.tables = []
        while real_length > 0:
            table = {}
            first_byte = ord(file.read(1))
            table['Pq'] = first_byte >> 4
            table['Tq'] = first_byte & 0x0F

            table_size = 64 if table['Pq'] == 0 else 128
            table['table'] = np.frombuffer(file.read(table_size), dtype = np.uint8)
            self.tables.append(table)
            real_length -= table_size + 1

class Segment:
    def read(self, file):
        self.marker = struct.unpack('>H', file.read(2))[0]
        self.length = struct.unpack('>H', file.read(2))[0]
        self.data = file.read(self.length - 2)
        
        if self.marker == 0xFFDD:
            self.name = 'DRI'
        elif self.marker == 0xFFFE:
            self.name = 'COM'
        else:
            self.name = 'Unknown'

class JPGDecoder:
    # 1.ハフマンデコード
    # 2.量子化逆変換
    # 3.逆DCT(逆離散コサイン変換)
    # 4.色空間変換
    
    def __init__(self, jpg):
        self.jpg = jpg
        data = np.frombuffer(jpg.data, dtype = np.uint8)
        print data.shape
        
        data = self.huffman_decode(data)
        data = self.dequantize(data)
        data = self.idct(data)
        data = self.color_space(data)
        return data
    
    def huffman_decode(self, data):
        tables = self.jpg.dht.tables
        print table
        uncompressed_data = []
        
        while len(data) > 0:
            for i in range(16):
                if data[i] > 0:
                    break
            else:
                break
            
            for j in range(1, data[i]+1):
                uncompressed_data.append(data[i+j])
            
            data = data[i+1:]
        
        return uncompressed_data
    
    def dequantize(self, data):
        tables = self.jpg.dqt.tables
        return data
    
    def idct(self, data):
        data = dct(data, axis = 1, norm = 'ortho')
        data = dct(data, axis = 0, norm = 'ortho')
        return data

    def color_space(self, data):
        pass
        
class JPG:
    def read(self, file):
        self.soi = struct.unpack('>H', file.read(2))[0]
        
        self.segments = []
        while True:
            marker = struct.unpack('>H', file.next(2))[0]
            
            if marker == 0xFFE0:
                segment = APP0()
                segment.read(file)
                self.app0 = segment
            elif marker == 0xFFE1:
                segment = APP1()
                segment.read(file)
                self.app1 = segment
            elif marker >= 0xFFC0 and marker <= 0xFFCF and not(marker == 0xFFC4 or marker == 0xFFD8 or marker == 0xFFDC):
                segment = SOF()
                segment.read(file)
                self.sof = segment
            elif marker == 0xFFDA:
                segment = SOS()
                segment.read(file)
                self.sos = segment
            elif marker == 0xFFC4:
                segment = DHT()
                segment.read(file)
                self.dht = segment
            elif marker == 0xFFDB:
                segment = DQT()
                segment.read(file)
                self.dqt = segment
            else:
                segment = Segment()
                segment.read(file)
            
            self.segments.append(segment)
            
            if marker == 0xFFDA:
                break
        
        data_size = len(file.data) - file.pos - 2
        self.data = file.read(data_size)
        
        decoder = JPGDecoder(self)
        print decoder.blocks
        
        self.eoi = file.read(2)