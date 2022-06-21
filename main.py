from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Object3D, Camera, Transformation3D, Camera3P,Camera1P
import numpy as np
import OpenGL.GL as GL
import pyrr
import hud as hud
from rafale import Entity,EntityRafale, EntityPlayer, EntityBullet, EntityCube, EntityRing
import time
import glfw
from timerDebug import TimerDebug
import random
import sys
import math
from terrain import Terrain
import multiprocessing as mp
import c_math

class Main:
    def __init__(self):
        self.game_over = False
        self.debug = False # Si True plus rien ne s'affiche dans la console => fichier .log
        if self.debug:
            self.old_stdout = sys.stdout
            self.log_file = open("logs/logs_" + str(int(time.time())) + ".log","w+")
            sys.stdout = self.log_file

        self.last_ticks = 0
        self.last_frames = 0
        # Compte les ticks depuis le début du jeu
        self.ticks_time = 0
        self.timer_debug = TimerDebug(self)

        self.FRAME_CAP = 60.0
        self.TICK_CAP = 70.0
        # Liste des entitées
        self.entities = []
        # TODO ajout de particules
        self.particules = []
        # Liste de huds
        self.huds = []
        # TODO Liste des objects du monde
        self.blocks = []

        
        self.initWindow()
        self.program3d_id = glutils.create_program_from_file('shader.vert', 'shader.frag')
        self.programGUI_id = glutils.create_program_from_file('gui.vert', 'gui.frag')

        # Chargement des models/textures
        self.loadMeshAndTexture()

        self.terrain = Terrain(self,tile_size = 1500,vertex_count = 200)

        self.player = EntityPlayer(self)

        self.player.center()
        self.player.object.transformation.translation += pyrr.Vector3([0,2,0])
        self.player.spawn()

        # Génération de l'anneau de score
        self.points = self.loadPoints()
        random.shuffle(self.points)
        self.check_point = 0
        self.generateRing()

        self.spawnGhost()

        # Création des différentes caméras
        self.cameras = []
        self.camera = Camera1P(self, entity=self.player)
        self.cameras.append(self.camera)
        self.camera = Camera3P(self, entity=self.player)
        self.cameras.append(self.camera)

        self.mouseX_middle, self.mouseY_middle = glfw.get_window_size(self.window)
        self.mouseX_middle = int(self.mouseX_middle/2)
        self.mouseY_middle = int(self.mouseY_middle/2)

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
        self.key_touch_lock = []
        self.button_touch = {}
        self.button_touch_lock = []

        # HUD instance
        # Exemple:
        vao = self.vao_default['hud']
        texture = self.textures['fontB2']

        def altitude(self):
            coord = []
            for i in self.main.player.object.transformation.translation:
                c = round(i,2)
                coord.append(c)
            return "Position: z" + str(coord[0])+" y:"+ str(coord[1])+" z:"+ str(coord[2])

        position = hud.HudPlayerFonction(self, "Altitude: ", altitude, np.array([-0.95, -0.95], np.float32), vao, 2, self.programGUI_id, texture)
        self.huds.append(position)

        def speed(self):
            return "Vitesse: " +str(round(self.main.player.speed,2))
        speed = hud.HudPlayerFonction(self, "Vitesse: 0.00", speed, np.array([-0.95, -0.85], np.float32), vao, 2, self.programGUI_id, texture)
        self.huds.append(speed)

        def fps(self):
            return ("Fps: " + str(round(self.main.last_frames,2)) + ", Ticks: " + str(round(self.main.last_ticks,2)))
        fps = hud.HudPlayerFonction(self, "Fps: 30.00, Ticks: 30.00", fps, np.array([-0.95, -0.75], np.float32), vao, 2, self.programGUI_id, texture)
        self.huds.append(fps)

        def score(self):
            return ("Score: " + str(round(self.main.player.score,2)))
        score = hud.HudPlayerFonction(self, "Score: 0", score, np.array([-0.95, -0.65], np.float32), vao, 2, self.programGUI_id, texture)
        self.huds.append(score)

        def anneauLabel(self):
            dy = self.main.player.object.transformation.translation.y-self.main.ring.object.transformation.translation.y
            if abs(dy) < 5:
                yL = "-"
            elif dy < 0:
                yL = "%"
            else:
                yL = "&"
            return ("Anneau> Dir: "+c_math.getArrow(self.main.player.object.transformation.translation,self.main.player.yaw%(2*math.pi),self.main.ring.object.transformation.translation) + \
            " y: " + (yL))
        anneau_label = hud.HudPlayerFonction(self, "Anneau> Dir: # y: $ % &", anneauLabel, np.array([-0.95, -0.55], np.float32), vao, 2, self.programGUI_id, texture)
        self.huds.append(anneau_label)
        def distanceGhost(self):
            return ("Distance fantome: " + str(round(pyrr.vector3.length(self.main.player.object.transformation.translation-self.main.rafale.object.transformation.translation),2)))
        distance_ghost = hud.HudPlayerFonction(self, "Distance fantome: 0", distanceGhost, np.array([-0.95, -0.45], np.float32), vao, 2, self.programGUI_id, texture)
        self.huds.append(distance_ghost)
    def spawnGhost(self):
        self.rafale = EntityRafale(self)
        self.rafale.center()
        range = 10
        self.rafale.object.transformation.translation += self.player.object.transformation.translation.copy() + pyrr.Vector3([((random.random()*2)-1)*range, ((random.random()*2)-1)*range, ((random.random()*2)-1)*range])
        self.rafale.spawn()

    def generateRing(self):
        if hasattr(self, 'ring'):
            self.ring.destroy()
        self.check_point = (self.check_point+1)%(len(self.points))
        self.ring = EntityRing(self)
        self.ring.object.transformation.translation = pyrr.Vector3(self.points[self.check_point])
        print(self.points[self.check_point])
        self.ring.base_y = self.ring.object.transformation.translation.y
        self.ring.spawn()

    def nextCamera(self):
        self.camera = self.cameras[0]
        self.cameras.remove(self.camera)
        self.cameras.append(self.camera)

    def respawn(self):
        pass

    def playerIsKill(self):
        self.game_over = True
        def gameOver(self):
            return "Game Over"
        game_over = hud.HudPlayerFonction(self,  "Game Over", gameOver, np.array([-0.5, 0], np.float32), self.vao_default['hud'], 2, self.programGUI_id,  self.textures['fontB2'])
        game_over.size = 2
        self.huds.append(game_over)
        def score(self):
            return "Score: " + str(self.main.player.score)
        score = hud.HudPlayerFonction(self,  "Score: 0", score, np.array([-0.5, -0.20], np.float32), self.vao_default['hud'], 2, self.programGUI_id,  self.textures['fontB2'])
        score.size = 2
        self.huds.append(score)
        self.mouseUncatch()

    def loadMeshAndTexture(self):
        self.meshs = {}
        self.meshs['rafale'] = Mesh.load_obj("rafale_texture/rafale.obj")
        self.meshs['cube'] = Mesh.load_obj("rafale_texture/cube.obj")
        self.meshs['bullet'] = Mesh.load_obj("rafale_texture/cube.obj")
        self.meshs['ring'] = Mesh.load_obj("ring.obj")

        for el in self.meshs.values():
            el.normalize()

        self.meshs['bullet'] = self.meshs['bullet'].apply_matrix(pyrr.matrix44.create_from_scale(pyrr.Vector4([1,1,1,1])*0.1))
        self.meshs['ring'] = self.meshs['ring'].apply_matrix(pyrr.matrix44.create_from_scale(pyrr.Vector4([1,1,1,1])*2))

        self.textures = {}
        self.textures['rafale'] = glutils.load_texture("rafale_texture/Dassault_Rafale_C_P01.png")
        self.textures['rafale_ghost'] = glutils.load_texture("rafale_texture/Dassault_Rafale_Ghost.png")
        self.textures['cube'] = glutils.load_texture("rafale_texture/cube.png")
        self.textures['bullet'] = glutils.load_texture("rafale_texture/cube.png")
        self.textures['grass'] = glutils.load_texture("grass.jpg")
        self.textures['fontB2'] = glutils.load_texture('fontB2.png')

        self.vao_default = {}
        self.vao_triangle_default = {}
        self.vao_default['rafale'] = self.meshs['rafale'].load_to_gpu()
        self.vao_triangle_default[self.vao_default['rafale']] = self.meshs['rafale'].get_nb_triangles()
        self.vao_default['cube'] = self.meshs['cube'].load_to_gpu()
        self.vao_triangle_default[self.vao_default['cube']] = self.meshs['cube'].get_nb_triangles()
        self.vao_default['bullet'] = self.meshs['bullet'].load_to_gpu()
        self.vao_triangle_default[self.vao_default['bullet']] = self.meshs['bullet'].get_nb_triangles()
        self.vao_default['hud'] = hud.Hud.initalize_geometry()
        self.vao_triangle_default[self.vao_default['hud']] = 2
        self.vao_default['ring'] = self.meshs['ring'].load_to_gpu()
        self.vao_triangle_default[self.vao_default['ring']] = self.meshs['ring'].get_nb_triangles()

    def initWindow(self):
        glfw.init()
        # paramétrage du context OpenGL
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # création et paramétrage de la fenêtre
        glfw.window_hint(glfw.RESIZABLE, True)
        self.window = glfw.create_window(800, 800, 'Viouuuuuu', None, None)
        glfw.make_context_current(self.window)
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

    def KeyIsPressed(self,key):
        return (key in self.touch and self.touch[key] > 0)

    def keyIsPressedOne(self,key):
        return (key in self.touch and self.touch[key] > 0 and not key in self.key_touch_lock)

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
        self.savePoints()
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
        self.mouseCatching()
        self.timer_debug.start("1sec")
        while self.running:
            if glfw.window_should_close(self.window):
                self.stop()
            if (self.nanoTime() - lastTickTime > tickTime):
                lastTickTime += tickTime
                self.timer_debug.start("update")
                self.update()
                self.timer_debug.end()
                ticks += 1
            elif (self.nanoTime() - lastRenderTime > renderTime):
                lastRenderTime += renderTime
                self.timer_debug.start("render")
                self.render()
                self.timer_debug.end()
                frames += 1
            else:
                pass
            if time.time()*1000.0 - timer > 1000:
                timer += 1000
                self.ticks_time+= ticks
                if True:
                    self.timer_debug.end()
                    # self.timer_debug.print(ticks,frames)
                    self.timer_debug.reset()
                    self.timer_debug.start("1sec")
                self.last_ticks = ticks
                self.last_frames = frames
                ticks = 0
                frames = 0
        self.exit()

    def update(self):
        glfw.poll_events()
        self.mouse_xoffset = self.t_mouse_xoffset
        self.mouse_yoffset = self.t_mouse_yoffset
        self.mouse_dX = self.t_mouse_dX
        self.mouse_dY = self.t_mouse_dY
        if self.mouse_catched:
            self.timer_debug.start("terrainUpdate")
            self.terrain.render()
            self.timer_debug.end()
            self.timer_debug.start("input")
            self.input()
            self.timer_debug.end()
            self.timer_debug.start("entitiesUpdate")
            if not self.rafale.isAlive():
                self.spawnGhost()
            for ent in self.entities:
                ent.update()
                if ent.collidable:
                    ent.collide()
            self.timer_debug.end()
            self.timer_debug.start("cameraUpdate")
            self.camera.update()
            self.timer_debug.end()
            self.timer_debug.start("particulesUpdate")
            for particule in self.particules:
                particule.update()
            self.timer_debug.end()
            self.timer_debug.start("hudUpdate")
            for hud in self.huds:
                hud.update()
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

        for key in self.touch.keys():
            if self.KeyIsPressed(key):
                self.key_touch_lock.append(key)
            elif key in self.key_touch_lock:
                self.key_touch_lock.remove(key)

    def render(self):
        # nettoyage de la fenêtre : fond et profondeur
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.timer_debug.start("terrainRender")
        self.terrain.render()
        self.timer_debug.end()
        self.timer_debug.start("cameraRender")
        self.camera.render()
        self.timer_debug.end()
        self.timer_debug.start("blocksRender")
        for block in self.blocks:
            block.render()
        self.timer_debug.end()
        self.timer_debug.start("entitiesRender")
        for ent in self.entities:
            ent.render()
        self.timer_debug.end()
        self.timer_debug.start("particuleRender")
        for particule in self.particules:
                particule.render()
        self.timer_debug.end()
        self.timer_debug.start("hudRender")
        for hud in self.huds:
            hud.draw()
        self.timer_debug.end()
        glfw.swap_buffers(self.window)

    def mouseCatching(self):
        if not self.mouse_catched and not self.game_over:
            self.mouse_catched = True
            self.mouseX, self.mouseY = glfw.get_window_size(self.window)
            self.mouseX /= 2
            self.mouseY /= 2
            self.mouse_dX, self.mouse_dY = 0,0
            glfw.set_cursor_pos(self.window,self.mouseX,self.mouseY)
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_HIDDEN);
            if (glfw.raw_mouse_motion_supported()):
                glfw.set_input_mode(self.window, glfw.RAW_MOUSE_MOTION, glfw.TRUE);

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
        if self.KeyIsPressed(glfw.KEY_ESCAPE):
            self.mouseUncatch()
        # Player mouvements
        if self.mouse_catched:
            self.player.input()
            self.camera.input()

    def nanoTime(self):
        return time.time()*1000000000.0

    def microTime(self):
        return time.time()*1000000.0

    def msTime(self):
        return time.time()*1000.0

    def savePoints(self):
        with open("points.txt","w+") as f:
            for point in self.points:
                if point == [0,0,0]:
                    continue
                f.write("[")
                for i in range(len(point)):
                    if i != 0:
                        f.write(",")
                    f.write(str(point[i]))
                f.write("],")

    def loadPoints(self):
        try:
            with open('points.txt') as f:
                contents = f.read()
                points = []
                for point_str in contents.split("],["):
                    if point_str == "":
                        continue
                    point_str = point_str.replace("[","")
                    point_str = point_str.replace("]","")
                    point_str_coos = point_str.split(",")
                    points.append([float(point_str_coos[0]),float(point_str_coos[1]),float(point_str_coos[2])])
                if len(points) == 0:
                    points.append([[0,0,0]])
                return points
        except OSError:
            print("Could not open/read file: points.txt")
            return [[0,0,0]]
import c_math
if __name__ == '__main__':
    s1 = pyrr.Vector3([2,1,-1])
    s2 = pyrr.Vector3([0,2,3])
    s3 = pyrr.Vector3([4,1,-2])
    pt = pyrr.Vector3([1,2,-3])
    nb = 4.9
    # print(nb,int(nb)/1.0)
    # exit()
    main = Main()
    main.start()
