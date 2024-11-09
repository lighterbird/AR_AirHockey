import numpy as np
from OpenGL.GL import *
from renderer.VBL import LayoutElement, VertexBufferLayout
from renderer.VBO import VertexBuffer
from renderer.Utils import GLCall

class VertexArray:
    def __init__(self):
        self.vao = GLCall(glGenVertexArrays, 1)
        GLCall(glBindVertexArray, self.vao)

    def __del__(self):
        GLCall(glDeleteVertexArrays, 1, (self.vao,))

    def AddBuffer(self, VBO: VertexBuffer, VBL: VertexBufferLayout):
        self.Bind()
        VBO.Bind()
        elements = VBL.GetElements()
        offset = 0
        for i in range(len(elements)):
            element = elements[i]
            GLCall(glEnableVertexAttribArray, i)
            GLCall(glVertexAttribPointer, i, element.count, element.type, element.normalized, ctypes.c_uint(VBL.layoutSize), ctypes.c_void_p(offset))
            offset += element.count * element.typeSize

    def Bind(self):
        GLCall(glBindVertexArray, self.vao)

    def Unbind(self):
        GLCall(glBindVertexArray, 0)
