import OpenGL.GL as GL
import pyrr
import math
import numpy as np
import glfw
import time

class Transformation3D:
    def __init__(self, euler = pyrr.euler.create(), center = pyrr.Vector3(), translation = pyrr.Vector3()):
        self.rotation_euler = euler.copy()
        self.rotation_center = center.copy()
        self.translation = translation.copy()

    def copy(self):
        return Transformation3D(euler = self.rotation_euler, center = self.rotation_center, translation = self.translation)

class Object:
    def __init__(self, vao, nb_triangle, program, texture):
        self.vao = vao
        self.nb_triangle = nb_triangle
        self.program = program
        self.texture = texture
        self.visible = True
        self.render_mode = 0

    def render(self):
        if self.visible :
            GL.glBindVertexArray(self.vao)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            if self.render_mode == 0:
                GL.glDrawElements(GL.GL_TRIANGLES, 3*self.nb_triangle, GL.GL_UNSIGNED_INT, None)
            else:
                GL.glDrawElements(GL.GL_LINE_LOOP, 3*self.nb_triangle, GL.GL_UNSIGNED_INT, None)

class Object3D(Object):
    def __init__(self, vao, nb_triangle, program, texture, transformation):
        super().__init__(vao, nb_triangle, program, texture)
        self.transformation = transformation

    def render(self):
        # GL.glUseProgram(self.program)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(self.program, "translation_model")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : translation_model")
        # Modifie la variable pour le programme courant
        translation = self.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(self.program, "rotation_center_model")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_center_model")
        # Modifie la variable pour le programme courant
        rotation_center = self.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_eulers(self.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(self.program, "rotation_model")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_model")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)
        super().render()

class Camera:
    def __init__(self, main,entity = None,transformation = Transformation3D(translation=pyrr.Vector3([0, 1, 0], dtype='float32')), projection = pyrr.matrix44.create_perspective_projection(60, 1, 0.01, 200)):
        self.main = main
        self.transformation = transformation
        self.projection = projection
        self.mouse_speed = 0.005
        self.entity = entity

    def update(self):
        pass

    def input(self):
        self.transformation.rotation_center = self.transformation.translation
        # print(self.mouse_dX,"|",self.mouse_dY)
        p = self.main.mouse_dX*self.mouse_speed
        y = self.main.mouse_dY*self.mouse_speed
        roll = self.transformation.rotation_euler[pyrr.euler.index().roll]
        if abs(roll + y) > math.pi/2:
            self.transformation.rotation_euler[pyrr.euler.index().roll] = math.pi*roll/(2*abs(roll))
        else:
            self.transformation.rotation_euler[pyrr.euler.index().roll] += y
        self.transformation.rotation_euler[pyrr.euler.index().yaw] += p
        self.transformation.rotation_euler[pyrr.euler.index().yaw] %= 2*math.pi

    def render(self):
        prog = self.main.program3d_id
        GL.glUseProgram(prog)
        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "translation_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : translation_view")
        # Modifie la variable pour le programme courant
        translation = -self.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "rotation_center_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_center_view")
        # Modifie la variable pour le programme courant
        rotation_center = self.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_eulers(-self.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(prog, "rotation_view")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_view")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)

        loc = GL.glGetUniformLocation(prog, "projection")
        if (loc == -1) :
            print("Pas de variable uniforme : projection")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.projection)

class Camera1P(Camera):
    def __init__(self, main, entity, transformation = Transformation3D(translation=pyrr.Vector3([0, 1, 0], dtype='float32')), projection = pyrr.matrix44.create_perspective_projection(60, 1, 0.01, 200)):
        Camera.__init__(self,main,entity=entity,transformation=transformation,projection=projection)
        self.t_roll = 0
        self.t_yaw = math.pi

    def input(self):
        p = self.main.mouse_dY*self.mouse_speed
        y = self.main.mouse_dX*self.mouse_speed
        roll = self.t_roll#self.transformation.rotation_euler[pyrr.euler.index().roll]
        if abs(roll + p) > math.pi/2:
            self.t_roll = math.pi*roll/(2*abs(roll))
        else:
            self.t_roll += p

        self.t_yaw -= y

    def update(self):
        self.transformation.translation = self.entity.object.transformation.translation + pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.transformation.rotation_euler), pyrr.Vector3([0, 0,1]))
        self.transformation.rotation_center = self.transformation.translation
        self.transformation.rotation_euler[pyrr.euler.index().yaw] = self.entity.object.transformation.rotation_euler[pyrr.euler.index().yaw] + self.t_yaw
        self.transformation.rotation_euler[pyrr.euler.index().roll] = self.t_roll# self.entity.object.transformation.rotation_euler[pyrr.euler.index().roll] + self.t_roll


class Camera3P(Camera):
    def __init__(self, main, entity, transformation = Transformation3D(translation=pyrr.Vector3([0, 1, 0], dtype='float32')), projection = pyrr.matrix44.create_perspective_projection(60, 1, 0.01, 200)):
        Camera.__init__(self,main,entity=entity,transformation=transformation,projection=projection)
        self.distance = 10.0
        self.max_distance = 20.0
        self.min_distance = 3.0
        self.scroll_speed = 0.5
        self.angle_around_entity = 0
        self.t = 0
    def input(self):
        # Camera.input(self)

        self.transformation.rotation_center = self.transformation.translation
        # self.transformation.rotation_center = self.entity.object.transformation.translation
        # print(self.mouse_dX,"|",self.mouse_dY)
        p = self.main.mouse_dY*self.mouse_speed
        y = self.main.mouse_dX*self.mouse_speed
        roll = self.transformation.rotation_euler[pyrr.euler.index().roll]
        if abs(roll + p) > math.pi/2:
            self.transformation.rotation_euler[pyrr.euler.index().roll] = math.pi*roll/(2*abs(roll))
        else:
            self.transformation.rotation_euler[pyrr.euler.index().roll] += p

        self.angle_around_entity -= y

        self.distance -= self.main.mouse_yoffset*self.scroll_speed
        if self.distance > self.max_distance:
            self.distance = self.max_distance
        elif self.distance < self.min_distance:
            self.distance = self.min_distance

    def update(self):
        Camera.update(self)
        h_distance = self.distance*math.cos(self.transformation.rotation_euler[pyrr.euler.index().roll])
        # self.t -= self.mouse_speed
        # theta = self.t
        theta = self.entity.object.transformation.rotation_euler[pyrr.euler.index().yaw]+self.angle_around_entity
        offsetX = h_distance*math.cos(theta)
        offsetZ = h_distance*math.sin(theta)
        # self.transformation.rotation_euler[pyrr.euler.index().yaw] = math.pi - self.angle_around_entity
        # offsetX = offsetZ = 0
        # self.transformation.rotation_euler[pyrr.euler.index().roll] = 0
        # self.transformation.rotation_euler[pyrr.euler.index().yaw] = self.angle_around_entity
        self.transformation.translation = self.entity.object.transformation.translation + \
        pyrr.Vector3([offsetX,self.distance*math.sin(self.transformation.rotation_euler[pyrr.euler.index().roll]),offsetZ])

        dir = self.entity.object.transformation.rotation_center+self.entity.object.transformation.translation - self.transformation.translation
        dir.y = 0
        dir.normalize()
        roll = self.transformation.rotation_euler[pyrr.euler.index().roll]%(2*math.pi)
        if roll == math.pi/2:
            yaw = 0
        else:
            roll = roll if not roll==math.pi else -1
            if dir[0] < 0:
                yaw = math.pi - math.acos(dir[2])
            else:
                yaw = math.acos(dir[2]) + math.pi
            # yaw = yaw = math.acos(dir[0]) - math.pi/2
            yaw %= 2*math.pi
            yaw = - yaw

        self.transformation.rotation_euler[pyrr.euler.index().yaw]  = yaw#self.angle_around_entity
        # print(dir)
        # print("offsetX: ",round(offsetX,3)," offsetZ: ",round(offsetZ,3)," angle: ", round(self.angle_around_entity,3), " yaw: ", round(yaw ,3))

class Text(Object):
    def __init__(self, value, bottomLeft, topRight, vao, nb_triangle, program, texture):
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
        self.bottomLeft[0] = self.bottomLeft_base[0] * rationB/2
        self.topRight[0] = self.topRight_base[0] * rationB/2

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
