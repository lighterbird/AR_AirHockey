import numpy as np
from OpenGL.GL import *
from renderer.Utils import GLCall

class IndexBuffer:
    def __init__(self, data: np.ndarray, count: int):
        self.count = count
        self.ibo = GLCall(glGenBuffers, 1)
        GLCall(glBindBuffer, GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        GLCall(glBufferData, GL_ELEMENT_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    def __del__(self):
        GLCall(glDeleteBuffers, 1, (self.ibo,))

    def Bind(self):
        GLCall(glBindBuffer, GL_ELEMENT_ARRAY_BUFFER, self.ibo)

    def Unbind(self):
        GLCall(glBindBuffer, GL_ELEMENT_ARRAY_BUFFER, 0)
