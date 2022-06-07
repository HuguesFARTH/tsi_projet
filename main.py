from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Object3D, Camera, Transformation3D, Text, Camera3P,Camera1P
import numpy as np
import OpenGL.GL as GL
import pyrr
from rafale import Entity,EntityRafale, EntityPlayer, EntityBullet, EntityCube
import time
import glfw
from timerDebug import TimerDebug
import sys

class Main:
    def __init__(self):
        self.debug = False
        if self.debug:
            self.old_stdout = sys.stdout
            self.log_file = open("logs/logs_" + str(int(time.time())) + ".log","w+")
            sys.stdout = self.log_file

        # Compte les ticks depuis le début du jeu
        self.ticks_time = 0
        self.timer_debug = TimerDebug(self)

        self.FRAME_CAP = 60.0
        self.TICK_CAP = 60.0
        self.entities = []
        self.initWindow()
        self.program3d_id = glutils.create_program_from_file('shader.vert', 'shader.frag')
        self.programGUI_id = glutils.create_program_from_file('gui.vert', 'gui.frag')

        # Chargement des models/textures
        self.loadMeshAndTexture()

        self.player = EntityPlayer(self)
        self.player.spawn()
        self.camera = Camera(self, entity=self.player)
        self.camera.transformation.translation.y = 2

        # centreEnt = EntityCube(self,obj_size = 0.1)
        # centreEnt.object.transformation.translation = pyrr.Vector3([0,0,0])
        # centreEnt.spawn()

        self.mouseX_middle, self.mouseY_middle = glfw.get_window_size(self.window)
        self.mouseX_middle = int(self.mouseX_middle/2)
        self.mouseY_middle = int(self.mouseY_middle/2)

        self.blocks = []
        m = Mesh()
        size = 100
        p0, p1, p2, p3 = [-size, 0, -size], [size, 0, -size], [size, 0, size], [-size, 0, size]
        n, c = [0, 1, 0], [1, 1, 1]
        t0, t1, t2, t3 = [0, 0], [1, 0], [1, 1], [0, 1]
        m.vertices = np.array([[p0 + n + c + t0], [p1 + n + c + t1], [p2 + n + c + t2], [p3 + n + c + t3]], np.float32)
        m.faces = np.array([[0, 1, 2], [0, 2, 3]], np.uint32)
        texture = glutils.load_texture('grass.jpg')
        o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), self.program3d_id, texture, Transformation3D())
        self.blocks.append(o)
        # paramétrage de la fonction de gestion des évènements
        glfw.set_key_callback(self.window, self.keyCallback)
        glfw.set_mouse_button_callback(self.window, self.mouseCallback)

        self.t_mouse_dX = 0
        self.t_mouse_dY = 0

        glfw.set_cursor_pos_callback(self.window,self.cursorPosCallback)

        # xoffset temporaire
        self.t_mouse_xoffset = 0
        self.t_mouse_yoffset = 0

        glfw.set_scroll_callback(self.window, self.scrollCallback)
        self.mouse_xoffset = 0
        self.mouse_yoffset = 0
        self.touch = {}
        self.button_touch = {}
        self.button_touch_lock = []

    def loadMeshAndTexture(self):
        self.meshs = {}
        self.meshs['rafale'] = Mesh.load_obj("rafale_texture/rafale.obj")
        self.meshs['cube'] = Mesh.load_obj("rafale_texture/cube.obj")
        self.meshs['bullet'] = Mesh.load_obj("rafale_texture/bullet2.obj")

        self.textures = {}
        self.textures['rafale'] = glutils.load_texture("rafale_texture/Dassault_Rafale_C_P01.png")
        self.textures['cube'] = glutils.load_texture("rafale_texture/cube.png")
        self.textures['bullet'] = glutils.load_texture("rafale_texture/cube.png")
        for el in self.meshs.values():
            el.normalize()

    def initWindow(self):
        glfw.init()
        # paramétrage du context OpenGL
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # création et paramétrage de la fenêtre
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(800, 800, 'Viouuuuuu', None, None)

        # activation du context OpenGL pour la fenêtre
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        # activation de la gestion de la profondeur
        GL.glEnable(GL.GL_DEPTH_TEST)
        # choix de la couleur de fond
        GL.glClearColor(0.5, 0.6, 0.9, 1.0)
        print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")

    def keyCallback(self, window, key, scancode, action, mods):
        self.touch[key] = action

    def mouseCallback(self, window, button, action, mods):
        self.button_touch[button] = action


    def scrollCallback(self,window, xoffset, yoffset):
        self.t_mouse_xoffset += xoffset
        self.t_mouse_yoffset += yoffset

    def cursorPosCallback(self, window, xpos, ypos):
        if self.mouse_catched and not xpos == self.mouseX_middle and not ypos == self.mouseY_middle:
            self.mouseX, self.mouseY = xpos,ypos
            self.t_mouse_dX = self.mouseX - self.mouseX_middle
            self.t_mouse_dY = self.mouseY - self.mouseY_middle
            glfw.set_cursor_pos(self.window,self.mouseX_middle,self.mouseY_middle)

    def keyIsPressed(self,key):
        return (key in self.touch and self.touch[key] > 0)

    def MouseIsPressed(self,button):
        return (button in self.button_touch and self.button_touch[button] > 0)

    def MouseIsPressedOne(self,button):
        return (button in self.button_touch and self.button_touch[button] > 0 and not button in self.button_touch_lock)

    def start(self):
        self.running = True
        self.loop()

    def stop(self):
        self.running = False

    def exit(self):
        glfw.set_window_should_close(self.window, glfw.TRUE)
        if self.debug:
            sys.stdout = self.old_stdout
            self.log_file.close()
        exit(0)

    def loop(self):
        lastTickTime = self.nanoTime()
        lastRenderTime = self.nanoTime()

        tickTime = 1000000000.0 / self.TICK_CAP
        renderTime = 1000000000.0 / self.FRAME_CAP

        ticks = 0
        frames = 0

        timer = time.time()*1000.0;
        self.mouse_catched = False
        self.timer_debug.start("1sec")
        while self.running:
            if glfw.window_should_close(self.window):
                self.stop()
            if (self.nanoTime() - lastTickTime > tickTime):
                lastTickTime += tickTime
                self.timer_debug.start("update")
                self.update()
                self.timer_debug.end()
                # print("Pos ",self.player.object.transformation.translation)
                # print("CameraPos ",self.camera.transformation.translation)
                # print("CameraPosEuler ",self.camera.transformation.rotation_euler)
                ticks += 1
            elif (self.nanoTime() - lastRenderTime > renderTime):
                lastRenderTime += renderTime
                self.timer_debug.start("render")
                self.render()
                self.timer_debug.end()
                frames += 1
            else:
                pass# time.sleep(0.0001)
            if time.time()*1000.0 - timer > 1000:
                timer += 1000
                print(ticks," ticks, ",frames," fps")
                print("Nbr entitiées: ",len(self.entities))
                self.ticks_time+= ticks
                ticks = 0
                frames = 0
                self.timer_debug.end()
                self.timer_debug.print()
                self.timer_debug.reset()
                self.timer_debug.start("1sec")

        self.exit()

    def update(self):
        self.mouse_xoffset = self.t_mouse_xoffset
        self.mouse_yoffset = self.t_mouse_yoffset
        self.mouse_dX = self.t_mouse_dX
        self.mouse_dY = self.t_mouse_dY
        if self.mouse_catched:

            self.timer_debug.start("input")
            self.input()
            self.timer_debug.end()
            self.timer_debug.start("cameraUpdate")
            self.camera.update()
            self.timer_debug.end()
            self.timer_debug.start("entitiesUpdate")
            for ent in self.entities:
                ent.update()
            self.timer_debug.end()
        self.t_mouse_xoffset = 0
        self.t_mouse_yoffset = 0
        self.t_mouse_dX = 0
        self.t_mouse_dY = 0

        if not self.mouse_catched and self.MouseIsPressed(glfw.MOUSE_BUTTON_LEFT):
            self.mouseCatching()
        for button in self.button_touch.keys():
            if self.MouseIsPressed(button):
                self.button_touch_lock.append(button)
            elif button in self.button_touch_lock:
                self.button_touch_lock.remove(button)
        # self.game.update();

    def render(self):
		# if (Display.wasResized()) {
		# 	glViewport(0, 0, Display.getWidth(), Display.getHeight());
		# }
        # nettoyage de la fenêtre : fond et profondeur
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.timer_debug.start("cameraRender")
        self.camera.render()
        self.timer_debug.end()
        self.timer_debug.start("blocksRender")
        for block in self.blocks:
            block.render()
        self.timer_debug.end()
        self.timer_debug.start("entitiesRender")

        GL.glUseProgram(self.program3d_id)
        for ent in self.entities:
            ent.render()
        self.timer_debug.end()
        glfw.swap_buffers(self.window)
        # gestion des évènements
        glfw.poll_events()
        # self.game.render();



    def mouseCatching(self):
        if not self.mouse_catched:
            self.mouse_catched = True
            self.mouseX, self.mouseY = glfw.get_window_size(self.window)
            self.mouseX /= 2
            self.mouseY /= 2
            self.mouse_dX, self.mouse_dY = 0,0
            glfw.set_cursor_pos(self.window,self.mouseX,self.mouseY)
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_HIDDEN);

    def mouseUncatch(self):
        if self.mouse_catched:
            self.mouse_catched = False
            self.mouseX, self.mouseY = glfw.get_window_size(self.window)
            self.mouseX /= 2
            self.mouseY /= 2
            self.mouse_dX, self.mouse_dY = 0,0
            glfw.set_cursor_pos(self.window,self.mouseX,self.mouseY)
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL);

    def input(self):
        # self.updateMouse()
        if self.keyIsPressed(glfw.KEY_ESCAPE):
            self.mouseUncatch()
        # Player mouvements
        if self.mouse_catched:
            self.camera.input()
            self.player.input()

    def nanoTime(self):
        return time.time()*1000000000.0

    def microTime(self):
        return time.time()*1000000.0

    def msTime(self):
        return time.time()*1000.0

if __name__ == '__main__':
    main = Main()
    main.start()
