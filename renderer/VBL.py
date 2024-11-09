import numpy as np
import ctypes
from OpenGL.GL import *

class LayoutElement:
    def __init__(self, type, count, normalized, typeSize):
        self.type = type
        self.count = count
        self.normalized = normalized
        self.typeSize = typeSize

class VertexBufferLayout:
    def __init__(self):
        self.elements = []
        self.layoutSize = 0
    def Push(self, elementType, count):
        if elementType == "float":
            self.elements.append(LayoutElement(GL_FLOAT, count, GL_FALSE, ctypes.sizeof(ctypes.c_float)))
            self.layoutSize += count * ctypes.sizeof(ctypes.c_float)
        elif elementType == "int":
            self.elements.append(LayoutElement(GL_INT, count, GL_FALSE, ctypes.sizeof(ctypes.c_int)))
            self.layoutSize += count * ctypes.sizeof(ctypes.c_int)
        elif elementType == "u_int":
            self.elements.append(LayoutElement(GL_UNSIGNED_INT, count, GL_FALSE, ctypes.sizeof(ctypes.c_uint)))
            self.layoutSize += count * ctypes.sizeof(ctypes.c_uint)
    def GetElements(self):
        return self.elements
    def GetStride(self):
        return self.layoutSize