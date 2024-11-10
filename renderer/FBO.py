import numpy as np
from OpenGL.GL import *
from renderer.Utils import GLCall
import cv2

class FrameBuffer:
    def __init__(self, width, height):
        self.w = width
        self.h = height

        # Create framebuffer
        self.fbo = GLCall(glGenFramebuffers, 1)
        GLCall(glBindFramebuffer, GL_FRAMEBUFFER, self.fbo)

        # Create colour buffer
        self.colourBuffer = GLCall(glGenTextures, 1)
        GLCall(glBindTexture, GL_TEXTURE_2D, self.colourBuffer)
        GLCall(glTexImage2D, GL_TEXTURE_2D, 0, GL_RGB, self.w, self.h, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        GLCall(glTexParameteri, GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        GLCall(glTexParameteri, GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        GLCall(glTexParameteri, GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        GLCall(glTexParameteri, GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        GLCall(glBindTexture, GL_TEXTURE_2D, 0)
        GLCall(glFramebufferTexture2D, GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.colourBuffer, 0)

        # Create Depth Stencil buffer
        self.depthStencilBuffer = GLCall(glGenRenderbuffers, 1)
        GLCall(glBindRenderbuffer, GL_RENDERBUFFER, self.depthStencilBuffer)
        GLCall(glRenderbufferStorage, GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.w, self.h)
        GLCall(glBindRenderbuffer, GL_RENDERBUFFER, 0)
        GLCall(glFramebufferRenderbuffer, GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.depthStencilBuffer)

        # Unbind frame buffer
        GLCall(glBindFramebuffer, GL_FRAMEBUFFER, 0)
    def Bind(self):
        GLCall(glBindFramebuffer, GL_FRAMEBUFFER, self.fbo)
    def Unbind(self):
        GLCall(glBindFramebuffer, GL_FRAMEBUFFER, 0)
    def ReadColourBuffer(self):
        self.Bind()

        data = GLCall(glReadPixels, 0, 0, self.w, self.h, GL_RGB, GL_UNSIGNED_BYTE)
        image = np.frombuffer(data, dtype=np.uint8).reshape((self.h, self.w, 3))
        image = np.flipud(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        self.Unbind()

        return image
    def __del__(self):
        GLCall(glDeleteTextures, [self.colourBuffer,])
        GLCall(glDeleteRenderbuffers, [self.depthStencilBuffer,])
        GLCall(glDeleteFramebuffers, [self.fbo,])