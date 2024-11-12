import numpy as np
import pyrr
from OpenGL.GL import *
from renderer.VBO import VertexBuffer
from renderer.IBO import IndexBuffer
from renderer.VAO import VertexArray
from renderer.VBL import VertexBufferLayout
from renderer.Shader import Shader
from renderer.Utils import GLCall
from renderer.FBO import FrameBuffer
import pygame as pg

class Graphics:
    def __init__(self, W, H):
        self.H = H
        self.W = W

        # Initialize scene Attributes
        self.objects = []
        self.shaders = []
        self.cameras = []
        self.lights = []

        # OpenGL init
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.W, self.H), pg.OPENGL|pg.DOUBLEBUF)

        self.clock = pg.time.Clock()
        
        GLCall(glClearColor, 0.0, 0.0, 0.0, 1)
        
        # Enable depth test
        GLCall(glEnable, GL_DEPTH_TEST)
        GLCall(glDepthFunc, GL_LESS)
    
    def __del__(self):
        pg.quit()

    def StartFrame(self, c0: float, c1: float, c2: float, c3: float):
        #check events
        running = True
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                running = False

        #refresh screen
        GLCall(glClearColor, c0, c1, c2, c3)
        GLCall(glClear, GL_COLOR_BUFFER_BIT)
        GLCall(glClear, GL_DEPTH_BUFFER_BIT)
        return running
    def EndFrame(self, fps):
        pg.display.flip()
        self.clock.tick(fps)

        