import threading
from src.player import Player
import pygame as pg
import numpy as np
from OpenGL.GL import *

from renderer.Object import Object
from renderer.Camera import Camera
from renderer.Shader import Shader
from renderer.Light import Light
from renderer.Utils import GLCall
from renderer.FBO import FrameBuffer
from renderer.Graphics import Graphics

from utils.images_to_video import images_to_video


class Game:
    def __init__(self):
        self.players = {}
        self.game_state = 0

    def UpdateFrame(self, client_id, frame, flags):
        # If new player then add to list of players
        if client_id not in self.players.keys():
            self.players[client_id] = Player(client_id)
        
        # Send current frame to player for updating
        return self.players[client_id].UpdateFrame(frame, flags)
    def RenderThread(self):
        self.graphics = Graphics(500,500)
        self.FrameBuffer = FrameBuffer(300, 400)


        # Scene init
        self.graphics.shaders.append(Shader("renderer/shaders/vertex_phong.glsl", "renderer/shaders/fragment_phong.glsl"))

        # Create and set cameras
        self.graphics.cameras.append(Camera(self.graphics.W, self.graphics.H))  # Scene cam
        self.graphics.cameras.append(Camera(300, 400)) # Player 1
        self.graphics.cameras.append(Camera(300, 400)) # Player 2

        self.graphics.cameras[0].position = np.array([2.0, 0.0, 0.0], dtype=np.float32)

        # Create and set objects

        ## Table
        self.graphics.objects.append(Object("renderer/objects/Table_1.obj", self.graphics.shaders[0]))
        self.graphics.objects[0].scale /= 10
        self.graphics.objects[0].colour = np.array([150/255, 75/255, 0.0, 1.0], dtype=np.float32)
        self.graphics.objects[0].diffuseCoeff = np.array([0.8, 0.8, 0.8], dtype=np.float32)
        self.graphics.objects[0].specularCoeff = np.array([0.3, 0.3, 0.3], dtype=np.float32)
        self.graphics.objects[0].ambientCoeff = np.array([0.1, 0.1, 0.1], dtype=np.float32)
        self.graphics.objects[0].shine = 10

        ## For cam1
        self.graphics.objects.append(Object("renderer/objects/camera.obj", self.graphics.shaders[0]))
        self.graphics.objects[1].position = np.array([1000.0, 1000.0, 1000.0], dtype=np.float32)
        self.graphics.objects[1].colour = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.graphics.objects[1].diffuseCoeff = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.graphics.objects[1].specularCoeff = np.array([0.6, 0.6, 0.6], dtype=np.float32)
        self.graphics.objects[1].ambientCoeff = np.array([0.3, 0.3, 0.3], dtype=np.float32)
        self.graphics.objects[1].shine = 20

        ## for cam2
        self.graphics.objects.append(Object("renderer/objects/camera.obj", self.graphics.shaders[0]))
        self.graphics.objects[2].position = np.array([1000.0, 1000.0, 1000.0], dtype=np.float32)
        self.graphics.objects[2].colour = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.graphics.objects[2].diffuseCoeff = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.graphics.objects[2].specularCoeff = np.array([0.6, 0.6, 0.6], dtype=np.float32)
        self.graphics.objects[2].ambientCoeff = np.array([0.3, 0.3, 0.3], dtype=np.float32)
        self.graphics.objects[2].shine = 20

        # Create and set lights
        self.graphics.lights.append(Light())
        self.graphics.lights[0].position = np.array([0.0, 0.0, 3.0])

        # Main Loop
        running = True
        while (running):
            players = list(self.players.values())
               
            # Get inputs
            keys = pg.key.get_pressed()

            # Update Scene using inputs and states
            self.UpdateSceneCam(keys)
 
            self.UpdatePlayerCams(keys, players)
            
            # Draw scene
            self.FrameBuffer.Unbind()
            running = self.graphics.StartFrame(0.0, 0.0, 0.0, 1)
            #print("ckpt 12")
            self.graphics.cameras[0].Use(self.graphics.shaders)
            self.graphics.lights[0].Use(self.graphics.shaders)
            #print("ckpt 13")
            self.graphics.objects[0].Draw()
            self.graphics.objects[1].Draw(self.graphics.objects[1].modelMatrix)
            self.graphics.objects[2].Draw(self.graphics.objects[2].modelMatrix)
            #print("ckpt 14")
            self.graphics.EndFrame(60)
            #print("ckpt 15")
    def UpdateSceneCam(self, inputs):
        if inputs[pg.K_w]:
            self.graphics.cameras[0].polar_position[1] -= 0.01
        if inputs[pg.K_a]:
            self.graphics.cameras[0].polar_position[2] -= 0.01
        if inputs[pg.K_s]:
            self.graphics.cameras[0].polar_position[1] += 0.01
        if inputs[pg.K_d]:
            self.graphics.cameras[0].polar_position[2] += 0.01
        if inputs[pg.K_SPACE]:
            self.graphics.cameras[0].polar_position[0] += 0.02
        if inputs[pg.K_LCTRL]:
            self.graphics.cameras[0].polar_position[0] -= 0.02
    def UpdatePlayerCams(self, inputs, players):
        # Assign Camera Matrix
        viewMat = None
        if len(players)>0:
            # Update player 1
            with players[0].player_camera_pose_lock:
               viewMat = players[0].player_camera_pose
            self.FrameBuffer.Bind()
            running = self.graphics.StartFrame(0.0, 0.0, 0.0, 1)
            self.graphics.cameras[1].Use(self.graphics.shaders, viewMat, players[0].fy)
            self.graphics.lights[0].Use(self.graphics.shaders)
            self.graphics.objects[0].Draw()
            if viewMat is not None:
                self.graphics.objects[1].Draw(np.linalg.inv(viewMat))
            self.graphics.objects[2].Draw(self.graphics.objects[2].modelMatrix)
            with players[0].virtual_view_lock:
                players[0].virtual_view = self.FrameBuffer.ReadColourBuffer()

            # Update player 2
            if len(players) > 1:
                with players[1].player_camera_pose_lock:
                    viewMat = players[1].player_camera_pose
                self.FrameBuffer.Bind()
                running = self.graphics.StartFrame(0.0, 0.0, 0.0, 1)
                self.graphics.cameras[2].Use(self.graphics.shaders, viewMat)
                self.graphics.lights[0].Use(self.graphics.shaders)
                self.graphics.objects[0].Draw()
                self.graphics.objects[1].Draw(self.graphics.objects[1].modelMatrix)
                if viewMat is not None:
                    self.graphics.objects[2].Draw(np.linalg.inv(viewMat))
                with players[1].virtual_view_lock:
                    players[1].virtual_view = self.FrameBuffer.ReadColourBuffer()
