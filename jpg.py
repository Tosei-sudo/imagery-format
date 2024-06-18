# coding : utf-8

from format.dummy import File
from format.jpg import JPG

with open('sample/sample3.jpg', 'rb') as file:
    data = File(file.read())

instance = JPG()
instance.read(data)