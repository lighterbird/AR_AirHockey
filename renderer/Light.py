from OpenGL.GL import *
import numpy as np
import ctypes
import pyrr

class Light:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0])
        self.colour = np.array([1.0, 1.0, 1.0])
    def Use(self, shaders: list):
        # Setting Uniforms
        for shader in shaders:
            shader.Bind()
            shader.SetUniform3f("lightPosition", self.position[0], self.position[1], self.position[2])