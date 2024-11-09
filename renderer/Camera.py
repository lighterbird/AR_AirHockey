from OpenGL.GL import *
import numpy as np
import ctypes
import pyrr


class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.position = np.array([0,0,1], dtype = np.float32)
        self.polar_position = np.array([3.0, 0.0, 0.0])
        self.targetPoint = np.array([0,0,0], dtype = np.float32)
        self.up = np.array([0,0,1], dtype = np.float32)
        self.fovy = 45
        self.nearPlane = 0.01
        self.farPlane = 10.0
    def spherical_to_cartesian(self, polar):
        r = polar[0]
        theta = polar[1]
        phi = polar[2]

        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)

        return np.array([x, y, z])
    def Use(self, shaders: list, viewMat = None):
        # Set camera pos
        self.position = self.spherical_to_cartesian(self.polar_position)

        # Setting Camera View Matrix
        if viewMat is not None:
            viewmatrix = viewMat
        else:
            viewmatrix = pyrr.matrix44.create_look_at(
                eye = self.position, target = self.targetPoint,
                up = self.up, dtype=np.float32).T
            
        # Setting Projection matrix
        projectionmatrix = pyrr.matrix44.create_perspective_projection(
            fovy = self.fovy, aspect = self.width / self.height, 
            near = self.nearPlane, far = self.farPlane, dtype = np.float32).T

        # print(f"View: {viewmatrix}\nview[3,2] = {viewmatrix[3,2]}\nProjection: {projectionmatrix}")
        
        # Setting Camera Matrix
        camMat = pyrr.matrix44.multiply(m1 = projectionmatrix, m2 = viewmatrix)

        # Setting Uniforms
        for shader in shaders:
            shader.Bind()
            shader.SetUniformMatrix4fv("cameraMatrix", camMat)
            shader.SetUniform3f("cameraPosition", self.position[0], self.position[1], self.position[2])
            