import numpy as np
from OpenGL.GL import *
from renderer.Utils import GLCall

class VertexBuffer:
    def __init__(self, data: np.ndarray):
        self.vbo = GLCall(glGenBuffers, 1)
        GLCall(glBindBuffer, GL_ARRAY_BUFFER, self.vbo)
        GLCall(glBufferData, GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    def __del__(self):
        GLCall(glDeleteBuffers, 1, (self.vbo,))

    def Bind(self):
        GLCall(glBindBuffer, GL_ARRAY_BUFFER, self.vbo)

    def Unbind(self):
        GLCall(glBindBuffer, GL_ARRAY_BUFFER, 0)
