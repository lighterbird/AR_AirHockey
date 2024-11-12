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
    def RemovePlayer(self, player_id):
        self.players.pop(player_id)
    def UpdateFrame(self, client_id, frame, flags):
        # If new player then add to list of players
        if client_id not in self.players.keys():
            self.players[client_id] = Player(client_id)
        
        # Send current frame to player for updating
        return self.players[client_id].UpdateFrame(frame, flags)

    def RenderThread(self):
        self.InitializeGameGraphics()
        self.InitGame()

        # Main Loop
        running = True
        while (running):
            running = self.graphics.StartFrame(0.0, 0.0, 0.0, 1)
            self.UpdateGameState()
            self.DrawGameElements()
            self.graphics.EndFrame(60)

        self.graphics.ExitPyGame()
    def InitializeGameGraphics(self):
        self.graphics = Graphics(500,500)
        self.FrameBuffer = FrameBuffer(300, 400)

        # Scene init
        self.graphics.shaders.append(Shader("renderer/shaders/vertex_phong.glsl", "renderer/shaders/fragment_phong.glsl"))

        # Create and set cameras
        self.graphics.cameras.append(Camera(self.graphics.W, self.graphics.H))  # Scene cam
        self.graphics.cameras.append(Camera(300, 400)) # Player 1
        self.graphics.cameras.append(Camera(300, 400)) # Player 2

        self.graphics.objects.append(Object("renderer/objects/Table_1.obj", self.graphics.shaders[0]))
        self.graphics.objects.append(Object("renderer/objects/camera.obj", self.graphics.shaders[0]))
        self.graphics.objects.append(Object("renderer/objects/camera.obj", self.graphics.shaders[0]))
        self.graphics.objects.append(Object("renderer/objects/puck.obj", self.graphics.shaders[0]))
        self.graphics.objects.append(Object("renderer/objects/striker.obj", self.graphics.shaders[0]))
        self.graphics.objects.append(Object("renderer/objects/striker.obj", self.graphics.shaders[0]))
        
        # Create and set lights
        self.graphics.lights.append(Light())
        
    def InitGame(self):
        self.graphics.lights[0].position = np.array([0.0, 0.0, 3.0])
        self.graphics.cameras[0].polar_position = np.array([2.0, np.pi/4, np.pi/4], dtype=np.float32)

        self.graphics.objects[0].scale /= 10
        self.graphics.objects[0].colour = np.array([150/255, 75/255, 0.0, 1.0], dtype=np.float32)
        self.graphics.objects[0].diffuseCoeff = np.array([0.8, 0.8, 0.8], dtype=np.float32)
        self.graphics.objects[0].specularCoeff = np.array([0.3, 0.3, 0.3], dtype=np.float32)
        self.graphics.objects[0].ambientCoeff = np.array([0.1, 0.1, 0.1], dtype=np.float32)
        self.graphics.objects[0].shine = 10

        self.graphics.objects[1].position = np.array([1000.0, 1000.0, 1000.0], dtype=np.float32)
        self.graphics.objects[1].colour = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.graphics.objects[1].diffuseCoeff = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.graphics.objects[1].specularCoeff = np.array([0.6, 0.6, 0.6], dtype=np.float32)
        self.graphics.objects[1].ambientCoeff = np.array([0.3, 0.3, 0.3], dtype=np.float32)
        self.graphics.objects[1].shine = 20

        self.graphics.objects[2].position = np.array([1000.0, 1000.0, 1000.0], dtype=np.float32)
        self.graphics.objects[2].colour = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.graphics.objects[2].diffuseCoeff = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.graphics.objects[2].specularCoeff = np.array([0.6, 0.6, 0.6], dtype=np.float32)
        self.graphics.objects[2].ambientCoeff = np.array([0.3, 0.3, 0.3], dtype=np.float32)
        self.graphics.objects[2].shine = 20

        self.graphics.objects[3].position = np.array([0.0, 0.0, 0.01], dtype=np.float32)
        self.graphics.objects[3].scale /= 30
        self.graphics.objects[3].colour = np.array([0.1, 0.1, 0.1, 1.0], dtype=np.float32)
        self.graphics.objects[3].diffuseCoeff = np.array([0.7, 0.7, 0.7], dtype=np.float32)
        self.graphics.objects[3].specularCoeff = np.array([0.9, 0.9, 0.9], dtype=np.float32)
        self.graphics.objects[3].ambientCoeff = np.array([0.3, 0.3, 0.3], dtype=np.float32)
        self.graphics.objects[3].shine = 30

        self.graphics.objects[4].scale /= 30
        self.graphics.objects[4].position = np.array([self.graphics.objects[0].objMin[0] * self.graphics.objects[0].scale[0] + abs(self.graphics.objects[4].objMin[0]) * self.graphics.objects[4].scale[0], 0.0, 0.01], dtype=np.float32)
        self.graphics.objects[4].colour = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.graphics.objects[4].diffuseCoeff = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.graphics.objects[4].specularCoeff = np.array([0.9, 0.9, 0.9], dtype=np.float32)
        self.graphics.objects[4].ambientCoeff = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.graphics.objects[4].shine = 30

        self.graphics.objects[5].scale /= 30
        self.graphics.objects[5].position = np.array([self.graphics.objects[0].objMax[0] * self.graphics.objects[0].scale[0] - abs(self.graphics.objects[5].objMax[0]) * self.graphics.objects[5].scale[0], 0.0, 0.01], dtype=np.float32)
        self.graphics.objects[5].colour = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.graphics.objects[5].diffuseCoeff = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.graphics.objects[5].specularCoeff = np.array([0.9, 0.9, 0.9], dtype=np.float32)
        self.graphics.objects[5].ambientCoeff = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.graphics.objects[5].shine = 30

    def UpdateGameState(self):
        players = list(self.players.values())
        if len(players) == 0:
            self.game_state = 0
        elif len(players) == 1:
            self.game_state = 1
        else:
            self.game_state = 2   
        
        keys = pg.key.get_pressed()
        self.UpdateSceneCam(keys)
        self.UpdatePlayerCams(keys, players)

        if self.game_state == 1: # Handle scaling
            if players[0].flags['scaleXPlus']:
                self.graphics.objects[0].scale[0] += 0.1 * (1/60)
            if players[0].flags['scaleXMinus']:
                self.graphics.objects[0].scale[0] -= 0.1 * (1/60)
            if players[0].flags['scaleYPlus']:
                self.graphics.objects[0].scale[1] += 0.1 * (1/60)
                self.graphics.objects[3].scale += 0.1 * (1/60)
                self.graphics.objects[4].scale += 0.1 * (1/60)
                self.graphics.objects[5].scale += 0.1 * (1/60)
            if players[0].flags['scaleYMinus']:
                self.graphics.objects[0].scale[1] -= 0.1 * (1/60)
                self.graphics.objects[3].scale -= 0.1 * (1/60)
                self.graphics.objects[4].scale -= 0.1 * (1/60)
                self.graphics.objects[5].scale -= 0.1 * (1/60)
            
            self.graphics.objects[4].position = np.array([self.graphics.objects[0].objMin[0] * self.graphics.objects[0].scale[0] + abs(self.graphics.objects[4].objMin[0]) * self.graphics.objects[4].scale[0], 0.0, 0.01], dtype=np.float32)
            self.graphics.objects[5].position = np.array([self.graphics.objects[0].objMax[0] * self.graphics.objects[0].scale[0] - abs(self.graphics.objects[5].objMax[0]) * self.graphics.objects[5].scale[0], 0.0, 0.01], dtype=np.float32)
        if self.game_state == 2:
            if players[0].flags['up']:
                self.graphics.objects[4].velocity[0] = 1
            elif players[0].flags['down']:
                self.graphics.objects[4].velocity[0] = -1
            else:
                self.graphics.objects[4].velocity[0] = 0
            
            if players[0].flags['left']:
                self.graphics.objects[4].velocity[1] = 1
            elif players[0].flags['right']:
                self.graphics.objects[4].velocity[1] = -1
            else:
                self.graphics.objects[4].velocity[1] = 0

            self.graphics.objects[4].position += self.graphics.objects[4].velocity * (1/60)
            
            
        
        

    def DrawGameElements(self):
        self.FrameBuffer.Unbind()
        running = self.graphics.StartFrame(0.0, 0.0, 0.0, 1)

        self.graphics.cameras[0].Use(self.graphics.shaders)
        self.graphics.lights[0].Use(self.graphics.shaders)

        self.graphics.objects[0].Draw()
        self.graphics.objects[1].Draw(self.graphics.objects[1].modelMatrix)
        self.graphics.objects[2].Draw(self.graphics.objects[2].modelMatrix)
        self.graphics.objects[3].Draw()
        self.graphics.objects[4].Draw()
        self.graphics.objects[5].Draw()

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
        if self.game_state > 0:
            # Update player 1
            with players[0].player_camera_pose_lock:
               viewMat = players[0].player_camera_pose
            self.FrameBuffer.Bind()
            running = self.graphics.StartFrame(0.0, 0.0, 0.0, 1)
            self.graphics.cameras[1].Use(self.graphics.shaders, viewMat, players[0].fy)
            self.graphics.lights[0].Use(self.graphics.shaders)
            self.graphics.objects[0].Draw()
            self.graphics.objects[3].Draw()
            self.graphics.objects[4].Draw()
            self.graphics.objects[5].Draw()
            # if viewMat is not None:
            #     self.graphics.objects[1].Draw(np.linalg.inv(viewMat))
            # self.graphics.objects[2].Draw(self.graphics.objects[2].modelMatrix)
            with players[0].virtual_view_lock:
                players[0].virtual_view = self.FrameBuffer.ReadColourBuffer()

            # Update player 2
            if self.game_state > 1:
                with players[1].player_camera_pose_lock:
                    viewMat = players[1].player_camera_pose
                self.FrameBuffer.Bind()
                running = self.graphics.StartFrame(0.0, 0.0, 0.0, 1)
                self.graphics.cameras[2].Use(self.graphics.shaders, viewMat, players[0].fy)
                self.graphics.lights[0].Use(self.graphics.shaders)
                self.graphics.objects[0].Draw()
                self.graphics.objects[3].Draw()
                self.graphics.objects[4].Draw()
                self.graphics.objects[5].Draw()
                # if viewMat is not None:
                #     self.graphics.objects[1].Draw(np.linalg.inv(viewMat))
                # self.graphics.objects[2].Draw(self.graphics.objects[2].modelMatrix)
                with players[1].virtual_view_lock:
                    players[1].virtual_view = self.FrameBuffer.ReadColourBuffer()
