import numpy as np
import pyrr
from OpenGL.GL import *
from renderer.VBO import VertexBuffer
from renderer.IBO import IndexBuffer
from renderer.VAO import VertexArray
from renderer.VBL import VertexBufferLayout
from renderer.Shader import Shader
from renderer.Utils import GLCall

class Renderer:
    def __init__(self):
        pass
    def Draw(self, vao: VertexArray, ibo: IndexBuffer, shader: Shader):
        # Bind Shader, VAO and IBO
        shader.Bind()
        vao.Bind()
        ibo.Bind()
        # Draw the indexed vertices as triangles
        GLCall(glDrawElements, GL_TRIANGLES, ibo.count, GL_UNSIGNED_INT, None)

    def Clear(self, c0: float, c1: float, c2: float, c3: float):
        GLCall(glClearColor, c0, c1, c2, c3)
        GLCall(glClear, GL_COLOR_BUFFER_BIT)