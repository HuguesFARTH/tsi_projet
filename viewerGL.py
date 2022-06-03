#!/usr/bin/env python3
import OpenGL.GL as GL
import glfw
import pyrr
import numpy as np
from cpe3d import Object3D,Object
import math
import OpenGL.GLU as GLU

class ViewerGL:
    def __init__(self,main):
        # initialisation de la librairie GLFW
        self.main = main
        glfw.init()
        # paramétrage du context OpenGL
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # création et paramétrage de la fenêtre
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(800, 800, 'Viouuuuuu', None, None)
        # capture de la souris
        # self.mouse_catching()
        # paramétrage de la fonction de gestion des évènements
        glfw.set_key_callback(self.window, self.key_callback)
        # activation du context OpenGL pour la fenêtre
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        # activation de la gestion de la profondeur
        GL.glEnable(GL.GL_DEPTH_TEST)
        # choix de la couleur de fond
        GL.glClearColor(0.5, 0.6, 0.9, 1.0)
        print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")

        self.entities = []
        self.touch = {}

    def run(self):
        # boucle d'affichage
        while not glfw.window_should_close(self.window):
            # nettoyage de la fenêtre : fond et profondeur
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            self.update()
            self.drawEntitites()
            # changement de buffer d'affichage pour éviter un effet de scintillement
            glfw.swap_buffers(self.window)
            # gestion des évènements
            glfw.poll_events()

    def mouse_catching(self):
        self.mouseX, self.mouseY = glfw.get_window_size(self.window)
        self.mouseX /= 2
        self.mouseY /= 2
        glfw.set_cursor_pos(self.window,self.mouseX,self.mouseY)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_HIDDEN);

    def key_callback(self, win, key, scancode, action, mods):
        # sortie du programme si appui sur la touche 'échappement'
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, glfw.TRUE)
        self.touch[key] = action

    def add_object(self, obj):
        self.entities.append(obj)

    def set_camera(self, cam):
        self.cam = cam

    def update_entities(self):
        for entity in self.entities:
            if isinstance(entity, Object):
                    GL.glUseProgram(entity.program)
            elif not entity.object == None and isinstance(entity.object, Object3D):
                    entity.update()

    def update(self):
        # self.update_mouse()
        self.update_key()
        self.update_entities()

    def drawEntitites(self):
        for entity in self.entities:
            entity.draw()

    def update_mouse(self):
        mouseX, mouseY = glfw.get_window_size(self.window)
        self.mouse_dX = self.mouseX - mouseX
        self.mouse_dY = self.mouseY - mouseY
        # print(self.mouse_dX," ",self.mouse_dY)
        self.mouseX = mouseX
        self.mouseY = mouseY
        self.mouseX /= 2
        self.mouseY /= 2
        glfw.set_cursor_pos(self.window,self.mouseX,self.mouseY)

    def update_camera(self, prog):
        self.cam.transformation.translation = self.main.player.object.transformation.translation + pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.main.player.object.transformation.rotation_euler), pyrr.Vector3([0, 0, -10]))
        # self.cam.transformation.rotation_euler = self.main.player.object.transformation.rotation_euler.copy()
        # self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
        # self.cam.transformation.rotation_euler[pyrr.euler.index().roll] *= -1
        # self.cam.transformation.rotation_euler[pyrr.euler.index().pitch] *= -1
        self.cam.transformation.rotation_center = self.main.player.object.transformation.rotation_center + self.main.player.object.transformation.translation
        # self.cam.transformation.translation = self.main.player.object.transformation.translation + pyrr.Vector3([0, 4, 0]) #pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.main.player.object.transformation.rotation_euler), pyrr.Vector3([0, 0, 6]))
        GL.glUseProgram(prog)
        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "translation_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : translation_view")
        # Modifie la variable pour le programme courant
        translation = -self.cam.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "rotation_center_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_center_view")
        # Modifie la variable pour le programme courant
        rotation_center = self.cam.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_eulers(-self.cam.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(prog, "rotation_view")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_view")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)

        loc = GL.glGetUniformLocation(prog, "projection")
        if (loc == -1) :
            print("Pas de variable uniforme : projection")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.cam.projection)

    def update_key(self):
        player = self.main.player

        if glfw.KEY_UP in self.touch and self.touch[glfw.KEY_UP] > 0:
            if glfw.KEY_V in self.touch and self.touch[glfw.KEY_V] > 0:
                self.cam.transformation.rotation_euler[pyrr.euler.index().roll] += 0.1
            else:
                player.object.transformation.rotation_euler[pyrr.euler.index().roll] += 0.1

        if glfw.KEY_DOWN in self.touch and self.touch[glfw.KEY_DOWN] > 0:
            if glfw.KEY_V in self.touch and self.touch[glfw.KEY_V] > 0:
                self.cam.transformation.rotation_euler[pyrr.euler.index().roll] -= 0.1
            else:
                player.object.transformation.rotation_euler[pyrr.euler.index().roll] -= 0.1

        if glfw.KEY_LEFT in self.touch and self.touch[glfw.KEY_LEFT] > 0:
            if glfw.KEY_V in self.touch and self.touch[glfw.KEY_V] > 0:
                self.cam.transformation.rotation_euler[pyrr.euler.index().pitch] += 0.1
            else:
                if True or self.main.player.object.transformation.rotation_euler[pyrr.euler.index().pitch] < math.pi/3 or player.object.transformation.rotation_euler[pyrr.euler.index().pitch] > 5*math.pi/3:
                    player.object.transformation.rotation_euler[pyrr.euler.index().pitch] += 0.1

        if glfw.KEY_RIGHT in self.touch and self.touch[glfw.KEY_RIGHT] > 0:
            if glfw.KEY_V in self.touch and self.touch[glfw.KEY_V] > 0:
                self.cam.transformation.rotation_euler[pyrr.euler.index().pitch] -= 0.1
            else:
                if True or player.object.transformation.rotation_euler[pyrr.euler.index().pitch] > 5*math.pi/3 or player.object.transformation.rotation_euler[pyrr.euler.index().pitch] < math.pi/3:
                    player.object.transformation.rotation_euler[pyrr.euler.index().pitch] -= 0.1


        if glfw.KEY_SPACE in self.touch and self.touch[glfw.KEY_SPACE] > 0:
            if player.speed < player.max_speed:
                player.speed += player.acceleration
            else:
                player.speed = player.max_speed
        else:
            if player.speed > 0:
                player.speed -= player.de_acceleration
            else:
                player.speed = 0

        # if glfw.KEY_BACKSPACE in self.touch and self.touch[glfw.KEY_BACKSPACE] > 0:
        #     if -self.main.player.speed < self.main.player.max_speed:
        #         self.main.player.speed -= self.main.player.acceleration
        #     else:
        #         self.main.player.speed = -self.main.player.max_speed
        # else:
        #     if -self.main.player.speed > 0:
        #         self.main.player.speed += self.main.player.de_acceleration
        #     else:
        #         self.main.player.speed = 0
