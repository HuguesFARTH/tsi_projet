from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Object3D, Camera, Transformation3D, Text
import numpy as np
import OpenGL.GL as GL
import pyrr
import math

class Entity():
    def __init__(self,main,obj,texture):
        self.main = main
        self.mesh = Mesh.load_obj(obj)
        self.mesh.normalize()
        self.mesh.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 1]))
        tr = Transformation3D()
        tr.translation.x = 0
        tr.translation.y = 10
        tr.translation.z = -5
        # tr.rotation_center.z = 0.2
        self.max_speed = 5
        self.speed = 0
        self.acceleration = 0.002
        self.de_acceleration = self.acceleration*2
        self.texture = glutils.load_texture(texture)
        self.object = Object3D(self.mesh.load_to_gpu(), self.mesh.get_nb_triangles(), self.main.program3d_id, self.texture, tr)

    def draw(self):
        GL.glUseProgram(self.main.program3d_id)
        self.object.draw()

    def update(self):
        pass

class EntityRafale(Entity):
    def __init__(self,main,obj="rafale_texture/rafale.obj",texture="rafale_texture/Dassault_Rafale_C_P01.png"):
        Entity.__init__(self, main, obj, texture)

    def draw(self):
        Entity.draw(self)

    def update(self):
        Entity.update(self)
        self.object.transformation.rotation_euler[pyrr.euler.index().pitch] %= (2*math.pi)
        pitch = self.object.transformation.rotation_euler[pyrr.euler.index().pitch]
        pas = 0.05
        # print(pitch)
        # if pitch > pas and abs(math.pi-pitch) > pas:
        #     if pitch < math.pi/2 or (pitch < 3*math.pi/2 and pitch > math.pi) :
        #         pass
        #         self.object.transformation.rotation_euler[pyrr.euler.index().pitch] -= pas*0.1
        #     else:
        #         pass
        #         self.object.transformation.rotation_euler[pyrr.euler.index().pitch] += pas*0.1
        # else:
        #     pitch = 0
        self.object.transformation.translation += \
            pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.object.transformation.rotation_euler), pyrr.Vector3([0, 0,self.speed]))
        self.main.player.object.transformation.rotation_euler[pyrr.euler.index().pitch]  %= 2*math.pi


class EntityPlayer(EntityRafale):
    def __init__(self,main):
        EntityRafale.__init__(self,main)

    def draw(self):
        EntityRafale.draw(self)

    def update(self):
        EntityRafale.update(self)
        self.main.viewer.update_camera(self.object.program)
        self.main.rafaleTest.object.transformation.rotation_euler = self.main.player.object.transformation.rotation_euler.copy()
        self.main.rafaleTest.object.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
        # self.main.rafaleTest.object.transformation.rotation_center = self.main.player.object.transformation.rotation_center + self.main.player.object.transformation.translation
        self.main.rafaleTest.object.transformation.translation = self.main.player.object.transformation.translation + pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.main.player.object.transformation.rotation_euler), pyrr.Vector3([0, 0, -6]))
        self.main.text.value = str(self.object.transformation.translation)
        self.main.text2.value = str(self.main.rafaleTest.object.transformation.translation)

    def input(self):
        pass
