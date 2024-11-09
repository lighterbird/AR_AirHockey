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
from renderer.Graphics import Graphics


class Game:
    def __init__(self):
        self.players = {}

    def UpdateFrame(self, client_id, frame):
        # If new player then add to list of players
        if client_id not in self.players.keys():
            self.players[client_id] = Player(client_id)
        
        # Send current frame to player for updating
        return self.players[client_id].UpdateFrame(frame)
    def RenderThread(self):
        self.graphics = Graphics(640,480)
        # Scene init
        self.graphics.shaders.append(Shader("renderer/shaders/vertex_phong.glsl", "renderer/shaders/fragment_phong.glsl"))
        self.graphics.cameras.append(Camera(self.graphics.W, self.graphics.H))
        self.graphics.objects.append(Object("renderer/objects/Table_1.obj", self.graphics.shaders[0]))
        self.graphics.objects[0].scale /= 3
        self.graphics.lights.append(Light())
        self.graphics.lights[0].position = np.array([0.0, 0.0, 3.0])

        # Main Loop
        running = True
        while (running):
            running = self.graphics.StartFrame(0.0, 0.0, 0.0, 1)
            # print(keys)
            # Update scene

            keys = pg.key.get_pressed()

            if keys[pg.K_w]:
                self.graphics.cameras[0].polar_position[1] -= 0.01
            if keys[pg.K_a]:
                self.graphics.cameras[0].polar_position[2] -= 0.01
            if keys[pg.K_s]:
                self.graphics.cameras[0].polar_position[1] += 0.01
            if keys[pg.K_d]:
                self.graphics.cameras[0].polar_position[2] += 0.01
            if keys[pg.K_SPACE]:
                self.graphics.cameras[0].polar_position[0] += 0.02
            if keys[pg.K_LCTRL]:
                self.graphics.cameras[0].polar_position[0] -= 0.02

            viewMat = None
            if len(self.players.keys())>0:
                players = list(self.players.values())
                with players[0].player_camera_pose_lock:
                    viewMat = players[0].player_camera_pose
                # print("viewMat: ", viewMat)
            # self.graphics.objects[0].rotation[2] += 1
            # if self.graphics.objects[0].rotation[2] >= 360:
            #     self.graphics.objects[0].rotation[2] = 0


            
            
            # Draw scene
            self.graphics.cameras[0].Use(self.graphics.shaders, viewMat)
            self.graphics.lights[0].Use(self.graphics.shaders)
            for obj in self.graphics.objects:
                obj.Draw()

            self.graphics.EndFrame(60)

