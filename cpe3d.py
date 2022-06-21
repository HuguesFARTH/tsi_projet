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

        # choix de la couleur de fond
        # GL.glClearColor(0.5, 0.6, 0.9, 1.0)
        GL.glUseProgram(self.program)


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
    def __init__(self, main,entity = None,transformation = Transformation3D(translation=pyrr.Vector3([0, 1, 0], dtype='float32')), projection = pyrr.matrix44.create_perspective_projection(60, 1, 0.01, 400)):
        self.main = main
        self.transformation = transformation
        self.projection = projection
        self.mouse_speed = 0.005
        self.entity = entity

    def update(self):
        if self.main.mouse_catched and self.main.keyIsPressedOne(glfw.KEY_F5):
            self.main.nextCamera()

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
        self.renderProg(prog)

    def renderProg(self, prog):
        GL.glUseProgram(prog)
        loc = GL.glGetUniformLocation(prog, "skyColor")
        if not (loc == -1) :
            GL.glUniform3f(loc, 0.5, 0.6, 0.9)

        loc = GL.glGetUniformLocation(prog, "translation_view")
        if not (loc == -1) :
            translation = -self.transformation.translation
            GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        loc = GL.glGetUniformLocation(prog, "rotation_center_view")
        # Vérifie que la variable existe
        if not (loc == -1) :
            rotation_center = self.transformation.rotation_center
            GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_eulers(-self.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(prog, "rotation_view")
        if not (loc == -1) :
            GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)

        loc = GL.glGetUniformLocation(prog, "projection")
        if not (loc == -1) :
            GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.projection)

class Camera3P(Camera):
    def __init__(self, main, entity, transformation = Transformation3D(translation=pyrr.Vector3([0, 1, 0], dtype='float32')), projection = pyrr.matrix44.create_perspective_projection(60, 1, 0.01, 400)):
        Camera.__init__(self,main,entity=entity,transformation=transformation,projection=projection)
        self.distance = 10.0
        self.max_distance = 100.0
        self.min_distance = 1.0
        self.scroll_speed = 0.5

    def input(self):
        p = self.main.mouse_dY*self.mouse_speed*1
        y = self.main.mouse_dX*self.mouse_speed*1
        roll = self.transformation.rotation_euler[pyrr.euler.index().roll]
        if abs(roll + p) > math.pi/2:
            self.transformation.rotation_euler[pyrr.euler.index().roll] = math.pi*roll/(2*abs(roll))
        else:
            self.transformation.rotation_euler[pyrr.euler.index().roll] += p*0.5
        self.transformation.rotation_euler[pyrr.euler.index().yaw]  += y

        self.distance -= self.main.mouse_yoffset*self.scroll_speed
        if self.distance > self.max_distance:
            self.distance = self.max_distance
        elif self.distance < self.min_distance:
            self.distance = self.min_distance

    def update(self):
        Camera.update(self)
        self.transformation.rotation_center = self.entity.object.transformation.translation + self.entity.object.transformation.rotation_center
        self.transformation.translation = self.entity.object.transformation.translation + \
            pyrr.Vector3([0, 0, self.distance])

class Camera1P(Camera):
    def __init__(self, main, entity, transformation = Transformation3D(translation=pyrr.Vector3([0, 1, 0], dtype='float32')), projection = pyrr.matrix44.create_perspective_projection(60, 1, 0.01, 400)):
        Camera.__init__(self,main,entity=entity,transformation=transformation,projection=projection)
        self.distance = 10.0
        self.max_distance = 100.0
        self.min_distance = 0.0
        self.scroll_speed = 0.5

    def input(self):
        self.distance -= self.main.mouse_yoffset*self.scroll_speed
        if self.distance > self.max_distance:
            self.distance = self.max_distance
        elif self.distance < self.min_distance:
            self.distance = self.min_distance

    def update(self):
        Camera.update(self)
        self.transformation.rotation_center = self.entity.object.transformation.translation + self.entity.object.transformation.rotation_center
        self.transformation.translation = self.entity.object.transformation.translation + \
            pyrr.Vector3([0, 0, self.distance])
