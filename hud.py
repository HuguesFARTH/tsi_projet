import glutils
from mesh import Mesh
from cpe3d import Object, Object3D, Camera, Transformation3D, Camera3P,Camera1P
import numpy as np
import OpenGL.GL as GL
import pyrr
from rafale import Entity,EntityRafale, EntityPlayer, EntityBullet, EntityCube
import time
import glfw
from timerDebug import TimerDebug
import sys


class Hud(Object):
    def __init__(self, main, value, bottomLeft, topRight, vao, nb_triangle, program, texture):
        self.main = main
        self.value = value
        self.base_value = value
        self.bottomLeft = bottomLeft
        self.topRight = topRight
        self.bottomLeft_base = bottomLeft.copy()
        self.topRight_base = topRight.copy()
        super().__init__(vao, nb_triangle, program, texture)

    def updateByBase(self):
        base = abs(self.bottomLeft_base[0] - self.topRight_base[0])
        rationB = len(self.value)/len(self.base_value)
        #self.bottomLeft[0] = self.bottomLeft_base[0] * rationB
        self.topRight[0] = self.topRight_base[0] * 1/rationB

    def draw(self):
        GL.glUseProgram(self.program)
        GL.glDisable(GL.GL_DEPTH_TEST)
        size = self.topRight-self.bottomLeft
        size[0] /= len(self.value)
        loc = GL.glGetUniformLocation(self.program, "size")
        if (loc == -1) :
            print("Pas de variable uniforme : size")
        GL.glUniform2f(loc, size[0], size[1])
        GL.glBindVertexArray(self.vao)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        for idx, c in enumerate(self.value):
            loc = GL.glGetUniformLocation(self.program, "start")
            if (loc == -1) :
                print("Pas de variable uniforme : start")
            GL.glUniform2f(loc, self.bottomLeft[0]+idx*size[0], self.bottomLeft[1])

            loc = GL.glGetUniformLocation(self.program, "c")
            if (loc == -1) :
                print("Pas de variable uniforme : c")
            GL.glUniform1i(loc, np.array(ord(c), np.int32))

            GL.glDrawElements(GL.GL_TRIANGLES, 3*2, GL.GL_UNSIGNED_INT, None)
        GL.glEnable(GL.GL_DEPTH_TEST)

    @staticmethod
    def initalize_geometry():
        p0, p1, p2, p3 = [0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]
        geometrie = np.array([p0+p1+p2+p3], np.float32)
        index = np.array([[0, 1, 2]+[0, 2, 3]], np.uint32)
        vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao)
        vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, geometrie, GL.GL_STATIC_DRAW)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        vboi = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER,vboi)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,index,GL.GL_STATIC_DRAW)
        return vao

    def update(self):
        self.updateByBase()


class HudPosition(Hud):
    def __init__(self, main, value, bottomLeft, topRight, vao, nb_triangle, program, texture):
        super().__init__(main, value, bottomLeft, topRight, vao, nb_triangle, program, texture)

    def update(self):
        super().update()
        coord = []
        for i in self.main.player.object.transformation.translation:
            c = round(i,2)
            coord.append(c)
        self.value = "position: " + str(coord[1])

class HudSpeed(Hud):
    def __init__(self, main, value, bottomLeft, topRight, vao, nb_triangle, program, texture):
        super().__init__(main, value, bottomLeft, topRight, vao, nb_triangle, program, texture)

    def update(self):
        speed = round(self.main.player.speed,2)
        self.value = "vitesse " +str(speed)
        super().update()