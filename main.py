from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Object3D, Camera, Transformation3D, Text
import numpy as np
import OpenGL.GL as GL
import pyrr
from rafale import EntityRafale, EntityPlayer

class Main:
    def __init__(self):
        self.viewer = ViewerGL(self)
        self.viewer.set_camera(Camera())
        self.viewer.cam.transformation.translation.y = 2
        self.viewer.cam.transformation.rotation_center = self.viewer.cam.transformation.translation.copy()
        self.program3d_id = glutils.create_program_from_file('shader.vert', 'shader.frag')
        self.programGUI_id = glutils.create_program_from_file('gui.vert', 'gui.frag')
        self.player = EntityPlayer(self)
        self.rafaleTest = EntityRafale(self,texture="rafale_texture/Dassault_Rafale_C_N.png")
        self.viewer.add_object(self.player)
        self.viewer.add_object(self.rafaleTest)
        # self.viewer.add_object(self.rafalTest)
        m = Mesh()
        size = 10000
        p0, p1, p2, p3 = [-size, 0, -size], [size, 0, -size], [size, 0, size], [-size, 0, size]
        n, c = [0, 1, 0], [1, 1, 1]
        t0, t1, t2, t3 = [0, 0], [1, 0], [1, 1], [0, 1]
        m.vertices = np.array([[p0 + n + c + t0], [p1 + n + c + t1], [p2 + n + c + t2], [p3 + n + c + t3]], np.float32)
        m.faces = np.array([[0, 1, 2], [0, 2, 3]], np.uint32)
        texture = glutils.load_texture('grass.jpg')
        o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), self.program3d_id, texture, Transformation3D())
        self.viewer.add_object(o)

        vao = Text.initalize_geometry()
        texture = glutils.load_texture('fontB.jpg')
        self.text = Text('Bonjour les', np.array([-0.5, 0.5], np.float32), np.array([0.8, 0.8], np.float32), vao, 2, self.programGUI_id, texture)
        self.viewer.add_object(self.text)
        self.text2 = Text('Bonjour les', np.array([-0.5, -0.8], np.float32), np.array([0.8, -0.5], np.float32), vao, 2, self.programGUI_id, texture)
        self.viewer.add_object(self.text2)


        self.viewer.run()


if __name__ == '__main__':
    Main()
