from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Object3D, Camera, Transformation3D, Text
import numpy as np
import OpenGL.GL as GL
import pyrr

class EntityRafale:
    def __init__(self,main):
        self.main = main
        self.mesh = Mesh.load_obj('rafale_texture/rafale.obj')
        self.mesh.normalize()
        self.mesh.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 1]))
        tr = Transformation3D()
        tr.translation.y = -np.amin(self.mesh.vertices, axis=0)[1]
        tr.translation.z = -5
        tr.rotation_center.z = 0.2
        self.max_speed = 5
        self.speed = 0
        self.acceleration = 0.002
        self.de_acceleration = self.acceleration*2
        self.texture = glutils.load_texture('rafale_texture/Dassault_Rafale_C_N.png')
        self.object = Object3D(self.mesh.load_to_gpu(), self.mesh.get_nb_triangles(), self.main.program3d_id, self.texture, tr)

    def draw(self):
        self.object.draw()

class EntityPlayer(EntityRafale):
    def __init__(self,main):
        EntityRafale.__init__(self,main)

    def update(self):
        pass

    def input(self):
        pass
