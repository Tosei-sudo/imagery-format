# coding : utf-8

from format.dummy import File
from format.png import PNG

with open('sample/sample2.png', 'rb') as file:
    data = File(file.read())

instance = PNG()
instance.read(data)

print instance.ihdr.__dict__