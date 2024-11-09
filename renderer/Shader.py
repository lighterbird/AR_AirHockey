from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from renderer.Utils import GLCall

class Shader:
    def __init__(self, vertexFilePath, fragmentFilePath):
        self.ID = self.createShader(vertexFilePath, fragmentFilePath)
        self.Bind()
        self.uniformLocationCache = {}

    def __del__(self):
        GLCall(glDeleteProgram, (self.ID,))

    def createShader(self, vertexFilePath, fragmentFilePath):
        try:
            with open(vertexFilePath, 'r') as f:
                vertex_src = f.readlines()
            with open(fragmentFilePath, 'r') as f:
                fragment_src = f.readlines()
            shader = GLCall(compileProgram, compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
            return shader
        except Exception as e:
            print("Error: ", e)

    def Bind(self):
        GLCall(glUseProgram, self.ID)

    def Unbind(self):
        GLCall(glUseProgram, 0)

    def GetUniformLocation(self, uname: str):
        if uname in self.uniformLocationCache.keys():
            return self.uniformLocationCache[uname]
        else:
            loc = GLCall(glGetUniformLocation, self.ID, uname.encode('utf-8'))
            if loc == -1:
                print(f"Uniform {uname} doesn't exist")
            self.uniformLocationCache[uname] = loc
            return loc

    def SetUniform1f(self, uname: str, v0):
        GLCall(glUniform1f, self.GetUniformLocation(uname), v0)

    def SetUniform3f(self, uname: str, v0, v1, v2):
        GLCall(glUniform3f, self.GetUniformLocation(uname), v0, v1, v2)

    def SetUniform4f(self, uname: str, v0, v1, v2, v3):
        GLCall(glUniform4f, self.GetUniformLocation(uname), v0, v1, v2, v3)

    def SetUniformMatrix4fv(self, uname, mat):
        GLCall(glUniformMatrix4fv, self.GetUniformLocation(uname), 1, GL_TRUE, mat)
