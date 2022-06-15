from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Object3D, Camera, Transformation3D, Camera3P
import numpy as np
import OpenGL.GL as GL
import pyrr
import math
import glfw

class BoundingBox:
    def __init__(self, main, size = 1, offset = pyrr.Vector3([0,0,0])):
        self.size = size
        self.main = main
        self.offset = offset
        self.position = offset.copy()
        self.ent = EntityCube(main,obj_size = size, no_bounding_box = True)
        self.ent.object.render_mode = 1
        # Ici on sauvegarde les objets déjà testé au tick afin de gagner du temps et ne pas calculer plusieurs fois la même collision
        self.save = {}

    def intersect(self,position):
        st = "p."+str(position)
        if st in self.save.keys():
            self.main.timer_debug.start("time save")
            self.main.timer_debug.end()
            return self.save[st]
        self.save[st] = pyrr.vector3.squared_length(self.position-position) < self.size**2
        return self.save[st]

    # intersection avec une droite
    def intersectD(self,vecteur,position, max_len = 1):
        p = position-self.position
        a = vecteur[0]**2+vecteur[1]**2+vecteur[2]**2
        b = 2*(vecteur[0]*p[0]+vecteur[1]*p[1]+vecteur[2]*p[2])
        c = p[0]**2+p[1]**2+p[2]**2-self.size**2
        delta = b**2 - 4*a*c
        if delta >= 0:
            sqr_l = pyrr.vector3.squared_length(position-self.position)
            return sqr_l < pyrr.vector3.squared_length(position+vecteur-self.position) and sqr_l < (max_len+self.size)**2
        return False

    def intersectDPoint(self,vecteur,position):
        p = position-self.position
        a = vecteur[0]**2+vecteur[1]**2+vecteur[2]**2
        b = 2*(vecteur[0]*p[0]+vecteur[1]*p[1]+vecteur[2]*p[2])
        c = p[0]**2+p[1]**2+p[2]**2-self.size**2
        delta = b**2 - 4*a*c
        if delta >= 0:
            r = -b/(2*a)
        if delta > 0:
            m = math.sqrt(delta)/(2*a)
            l = 9999999999
            for i in [r+m,r-m]:
                g = pyrr.Vector3([i*vecteur[0] + p[0], i*vecteur[1] + p[1], i*vecteur[2] + p[2]])
                v = position-self.position+g
                ll = pyrr.vector3.squared_length(v)
                if ll < l:
                    print("ouii")
                    l = pyrr.vector3.squared_length(v)
                    print('g',g,'pos',self.position)
                    r = g + self.position
        elif delta == 0:
            r = pyrr.Vector3([r*vecteur[0] + p[0],r*vecteur[1] + p[1],r*vecteur[2] + p[2]])
        return r

    def intersectHeight(self):
        tp = self.position.copy()
        st = "h."+str([tp.x,tp.y,tp.z])
        if st in self.save.keys():
            self.main.timer_debug.start("time save")
            self.main.timer_debug.end()
            return self.save[st]
        tp.y = self.main.terrain.getHeightV2(tp.x,tp.y,tp.z)
        self.save[st] = self.position.y  <= tp.y + self.size
        return self.save[st]

    def intersectB(self,bounding_box):
        st = "b."+str(bounding_box)
        if st in self.save.keys():
            self.main.timer_debug.start("time save")
            self.main.timer_debug.end()
            return self.save[st]
        self.save[st] = (pyrr.vector3.squared_length(self.position - bounding_box.position) <= (self.size + bounding_box.size)**2)
        return self.save[st]

    def intersectE(self,entity, fast = False):
        st = "e."+str(entity)
        if st in self.save.keys():
            self.main.timer_debug.start("time save")
            self.main.timer_debug.end()
            return self.save[st]
        if not entity.general_bounding_box == None:
            if self.intersectB(entity.general_bounding_box):
                if fast:
                    return True
                for bounding_box in entity.bounding_boxes:
                    if not bounding_box == None:
                        if bounding_box.intersectB(self):
                            self.save[st] = True
                            return True
        self.save[st] = False
        return False

    def adapt(self,transformation,euler):
        self.save.clear()
        self.main.timer_debug.start("adapt")
        self.position = transformation.translation + pyrr.matrix33.apply_to_vector(euler, self.offset)
        self.main.timer_debug.end()
        self.ent.object.transformation.translation = self.position

    def draw(self):
        self.ent.render()

class Entity():
    def __init__(self, main, texture, mesh = None, obj_size = 1,scaleVector =  [1, 1, 1, 1], bounding_box = None, name = "entity", vao = None, bounding_box_forced = True):
        self.main = main
        self.name = name
        tr = Transformation3D()
        self.texture = texture
        self.collidable = True
        if vao == None or not mesh == None:
            self.mesh = mesh.copy()
            self.mesh.apply_matrix(pyrr.matrix44.create_from_scale(pyrr.Vector4(scaleVector)*obj_size))
            vao_load = self.mesh.load_to_gpu()
            triangles = self.mesh.get_nb_triangles()
        else:
            vao_load = vao
            triangles = self.main.vao_triangle_default[vao_load]
        self.object = Object3D(vao_load, triangles, self.main.program3d_id, self.texture, tr)
        self.start_tick = self.main.ticks_time
        if not bounding_box == None:
            self.general_bounding_box = bounding_box
        elif bounding_box_forced:
            self.general_bounding_box = BoundingBox(main, size = 1, offset = pyrr.Vector3([0,0,0]))
        else:
            self.general_bounding_box = None
        self.bounding_boxes = []
        self.last_trans = self.object.transformation.copy()
        self.life = 100
        self.hide_bounding_box = False
        self.destroy_if_collide = False

    def addBounding_Boxe(self, bounding_box):
        self.bounding_boxes.append(bounding_box)

    def render(self):
        self.object.render()
        if not self.hide_bounding_box:
            if not self.general_bounding_box == None:
                self.general_bounding_box.draw()
            for bounding_box in self.bounding_boxes:
                if not bounding_box == None:
                    bounding_box.draw()

    def intersect(self,position):
        if not self.general_bounding_box == None:
            if self.general_bounding_box.intersect(position):
                if len(self.bounding_boxes) > 0:
                    for bounding_box in self.bounding_boxes:
                        if bounding_box.intersect(position):
                            return True
                else:
                    return True
        return False

    def intersectD(self,vecteur,position, max_len = 1):
        if not self.general_bounding_box == None:
            if self.general_bounding_box.intersectD(vecteur, position, max_len = max_len):
                if len(self.bounding_boxes) > 0:
                    for bounding_box in self.bounding_boxes:
                        if bounding_box.intersectD(vecteur, position, max_len = max_len):
                            return bounding_box
                else:
                    return self.general_bounding_box
        return False

    def intersectHeight(self):
        if not self.general_bounding_box == None:
            if self.general_bounding_box.intersectHeight():
                if len(self.bounding_boxes) > 0:
                    for bounding_box in self.bounding_boxes:
                        if bounding_box.intersectHeight():
                            return True
                else:
                    return True
        return False

    def intersectE(self,entity):
        if not self.general_bounding_box == None:
            if self.general_bounding_box.intersectE(entity, fast = True):
                if len(self.bounding_boxes) > 0:
                    i = 0
                    for bounding_box in self.bounding_boxes:
                        if bounding_box.intersectE(entity):
                            return True
                        i += 1
                else:
                    return True
        return False

    def update(self):
        euler = pyrr.matrix33.create_from_eulers(self.object.transformation.rotation_euler)
        if not self.general_bounding_box == None:
            self.general_bounding_box.adapt(self.object.transformation,euler)
        for bounding_box in self.bounding_boxes:
            if not bounding_box == None:
                bounding_box.adapt(self.object.transformation,euler)

    def spawn(self):
        self.main.entities.append(self)

    def destroy(self):
        self.main.entities.remove(self)

    def hit(self, am = 1):
        self.life -= am
        if self.life <= 0:
            self.destroy()

    def collidWall(self):
        if self.destroy_if_collide:
            self.destroy()

    # Retourne True si collision avec le terrain, l'entité si c'est une entité
    def collide(self):
        self.main.timer_debug.start("collide h")
        if self.intersectHeight():
            self.object.transformation = self.last_trans
            self.last_trans = self.object.transformation.copy()
            self.collidWall()
            self.main.timer_debug.end()
            return True
        self.main.timer_debug.end()
        self.main.timer_debug.start("collide e")
        for ent in self.main.entities:
            if (not ent.collidable) or ent == self or (hasattr(self,'shooter') and self.shooter == ent):
                # if self.name == "Player":
                #     print("not test",ent.name)
                continue
            elif self.intersectE(ent):
                self.object.transformation = self.last_trans
                self.last_trans = self.object.transformation.copy()
                # print("collide ", ent)
                self.main.timer_debug.end()
                if self.destroy_if_collide:
                    self.destroy()
                if ent.destroy_if_collide:
                    ent.destroy()
                return ent
        self.last_trans = self.object.transformation.copy()
        self.main.timer_debug.end()
        return False


class EntityRafale(Entity):
    def __init__(self,main, name = "Rafale"):
        Entity.__init__(self, main, name = name, vao = main.vao_default['rafale'], texture = main.textures['rafale'])
        self.addBounding_Boxe(BoundingBox(main,size = 0.15, offset = pyrr.Vector3([0,-0.15,-0.6])))
        self.addBounding_Boxe(BoundingBox(main,size = 0.15, offset = pyrr.Vector3([0,-0.15,-0.3])))
        self.addBounding_Boxe(BoundingBox(main,size = 0.15, offset = pyrr.Vector3([0,-0.15,0])))
        self.addBounding_Boxe(BoundingBox(main,size = 0.15, offset = pyrr.Vector3([0,-0.15,0.3])))
        self.addBounding_Boxe(BoundingBox(main,size = 0.15, offset = pyrr.Vector3([0,-0.15,0.6])))
        self.max_speed = 2
        self.speed = 0.0
        self.min_speed = 0.0
        self.acceleration = 0.006
        self.de_acceleration = self.acceleration/10
        self.redressement_speed = 0.04
        self.de_redressement_speed = self.redressement_speed * 2
        self.destroy_if_collide = True
        # Tir à gauche ou droite
        self.last_shoot_side = False
        self.object.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi

        # Gestion du pitch et roll
        self.pitch = 0
        self.roll = 0
        self.yaw = 0

    def render(self):
        Entity.render(self)

    def update(self):
        Entity.update(self)
        self.object.transformation.rotation_euler %= (2*math.pi)
        self.roll%= (2*math.pi)
        self.pitch %= (2*math.pi)

    def goForward(self):
        self.object.transformation.translation += \
            pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.object.transformation.rotation_euler), pyrr.Vector3([0, 0,self.speed]))

    def rotateUp(self):
        self.pitch += self.redressement_speed
        if  math.pi > self.pitch > math.pi/2:
            self.pitch = math.pi/2

    def rotateDown(self):
        self.pitch -= self.redressement_speed
        if  math.pi < self.pitch < 3*math.pi/2:
            self.pitch = 3*math.pi/2

    def rotateLeft(self):
        self.roll += self.redressement_speed

    def rotateRight(self):
        self.roll -= self.redressement_speed

    def input(self):
        pass

    def shoot(self):
        self.main.timer_debug.start("shoot")
        dir = pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.object.transformation.rotation_euler), pyrr.Vector3([0, 0,1]))
        bullet = EntityBullet(self.main,self,dir)
        bullet.object.transformation.translation = self.object.transformation.translation + pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.object.transformation.rotation_euler),  pyrr.Vector3([0.28 if self.last_shoot_side else -0.28 ,-0.18,-0.355]))
        bullet.object.transformation.rotation_euler = self.object.transformation.rotation_euler.copy();
        bullet.spawn()
        # self.main.camera = Camera3P(self.main, entity=bullet)
        self.last_shoot_side = not self.last_shoot_side
        self.main.timer_debug.end()
        return bullet

    def regulePitch(self):
        if 3.14 > self.pitch > 0:
            self.rotateDown()
            if self.pitch < 0:
                    self.pitch = 0
        elif self.pitch >= 3.14:
            self.rotateUp()
            if self.pitch > 6.28:
                    self.pitch = 0
        # if self.pitch == 0:
        #     pass
        # elif self.pitch == math.pi:
        #     pass
        # elif 0 < self.pitch <= math.pi/2:
        #     self.rotateDown()
        #     if self.pitch < 0:
        #         self.pitch = 0
        # elif self.pitch <= math.pi:
        #     self.rotateUp()
        #     if self.pitch > math.pi:
        #         self.pitch = math.pi
        # elif self.pitch <= 3*math.pi/2:
        #     self.rotateDown()
        #     if self.pitch < math.pi:
        #         self.pitch = math.pi
        # elif self.pitch <= 2*math.pi:
        #     self.rotateUp()
        #     if self.pitch > 2*math.pi:
        #         self.pitch = 0

    def reguleRoll(self):
        if self.roll == 0:
            pass
        elif self.roll == math.pi:
            pass
        elif 0 < self.roll <= math.pi/2:
            self.rotateRight()
            if self.roll < 0:
                self.roll = 0
        elif self.roll <= math.pi:
            self.rotateLeft()
            if self.roll > math.pi:
                self.roll = math.pi
        elif self.roll <= 3*math.pi/2:
            self.rotateRight()
            if self.roll < math.pi:
                self.roll = math.pi
        elif self.roll <= 2*math.pi:
            self.rotateLeft()
            if self.roll > 2*math.pi:
                self.roll = 0

class EntityPlayer(EntityRafale):
    def __init__(self,main):
        EntityRafale.__init__(self,main, name = "Player")
        self.object.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
        self.fire_rate = 1000.0/10
        self.last_shoot = self.main.msTime()
        self.gravity = 0.0001
        self.len_droite_dir = 100
        self.droite_dir = EntityCube(self.main,scaleVector=[0.1,0.1,self.len_droite_dir,1],obj_size=0.1)
        self.regulePitchVar = False

        self.hide_bounding_box = True
        # self.object.render_mode = 1

    def center(self):
        x = -self.main.terrain.tile_size/2
        z = x
        y = self.main.terrain.getHeight(x,self.object.transformation.translation.y,z) + 2
        self.object.transformation.translation = pyrr.Vector3([x, y, z])
        self.last_trans = self.object.transformation.copy()

    def respawn(self):
        # self.destroy()
        self.center
        self.spawn()

    def destroy(self):
        super().destroy()
        self.main.playerIsKill()
        print("/!\\Game Over/!\\")

    def render(self):
        EntityRafale.render(self)
        self.droite_dir.render()


    def update(self):
        EntityRafale.update(self)
        self.droite_dir.object.transformation = self.object.transformation.copy()
        mv = self.len_droite_dir*0.1
        d = pyrr.Vector3([0.28 if self.last_shoot_side else -0.28 ,-0.18,-0.355])
        self.droite_dir.object.transformation.translation.z += mv
        self.droite_dir.object.transformation.translation += d
        self.droite_dir.object.transformation.rotation_center.z -= mv
        self.droite_dir.object.transformation.rotation_center -= d
        self.pitch %= 2*math.pi
        self.main.player.object.transformation.rotation_euler[pyrr.euler.index().yaw] = self.yaw
        self.main.player.object.transformation.rotation_euler[pyrr.euler.index().roll] = math.cos(self.yaw)*math.sin(self.pitch)
        self.main.player.object.transformation.rotation_euler[pyrr.euler.index().pitch] = math.sin(self.yaw)*math.sin(self.pitch)

    def input(self):
        EntityRafale.input(self)
        current_time = self.main.msTime()
        if self.main.mouse_catched and self.main.MouseIsPressed(glfw.MOUSE_BUTTON_LEFT) and (current_time - self.last_shoot) > self.fire_rate:
                self.shoot()
                self.last_shoot = current_time


        if self.main.mouse_catched and self.main.keyIsPressedOne(glfw.KEY_M):
                self.regulePitchVar = not self.regulePitchVar

        if self.main.KeyIsPressed(glfw.KEY_W):
            self.rotateDown()
        elif self.main.KeyIsPressed(glfw.KEY_S):
            self.rotateUp()
        elif self.regulePitchVar:
            self.regulePitch()

        if self.main.KeyIsPressed(glfw.KEY_LEFT):
            self.rotateLeft()
        elif self.main.KeyIsPressed(glfw.KEY_RIGHT):
            self.rotateRight()
        # else:
        #     self.reguleRoll()

        if self.main.KeyIsPressed(glfw.KEY_A):
            self.yaw -= 0.1#*self.speed

        if self.main.KeyIsPressed(glfw.KEY_D):
            self.yaw += 0.1#*self.speed

        if self.main.KeyIsPressed(glfw.KEY_SPACE):
            if self.speed < self.max_speed:
                self.speed += self.acceleration
            else:
                self.speed = self.max_speed

        elif self.main.KeyIsPressed(glfw.KEY_LEFT_SHIFT):
            if self.speed > self.min_speed:
                self.speed -= 2*self.acceleration
                if self.speed < self.min_speed:
                    self.speed = self.min_speed
            else:
                self.speed = self.min_speed
        else:
            if self.speed > self.min_speed:
                self.speed -= self.de_acceleration
            else:
                self.speed = self.min_speed

        # Semblant effet résistance air
        # resistance = fct parabole centrée en pi/2 définie sur 0 - pi
        resistance = (1-(((2*(self.pitch%math.pi))/math.pi)-1)**2)
        self.speed -= 5*self.de_acceleration*resistance
            # TODO Planer (gravité ?)
            # self.object.transformation.translation += pyrr.Vector3([0, self.gravity,0])
        self.goForward()

class EntityBullet(Entity):
    def __init__(self,main,shooter,dir,scaleVector=[1,1,1,1],obj_size=0.01,real = True):
        Entity.__init__(self, main, name = 'bullet', vao = main.vao_default["bullet"], texture = main.textures['bullet'], scaleVector=scaleVector,obj_size=obj_size)
        self.speed = 5
        self.direction = dir
        self.tick_life = 300
        self.collidable = False
        self.shooter = shooter
        self.hide_bounding_box = True
        self.real = real
        self.destroy_if_collide = True

    def render(self):
        Entity.render(self)

    def collidWall(self):
        self.destroy()

    def update(self):
        self.main.timer_debug.start("bullet update")
        Entity.update(self)
        if self.main.ticks_time - self.start_tick > self.tick_life:
            print("life end")
            self.destroy()
        self.object.transformation.translation += self.direction*self.speed
        self.main.timer_debug.start("collide h")
        if self.intersectHeight():
            self.object.transformation = self.last_trans
            self.last_trans = self.object.transformation.copy()
            self.collidWall()
            self.main.timer_debug.end()
            self.main.timer_debug.end()
            return
        self.main.timer_debug.end()
        self.main.timer_debug.start("collide e bullet")
        for ent in self.main.entities:
            if (not ent.collidable) or ent == self or (hasattr(self,'shooter') and self.shooter == ent):
                continue
            else:
                bounding_box = ent.intersectD(self.direction,self.object.transformation.translation, max_len = self.speed)
                if bounding_box:
                    pt = bounding_box.intersectDPoint(self.direction,self.object.transformation.translation)
                    print(pt)
                    cube = EntityCube(self.main,obj_size = 0.05)
                    cube.object.transformation.translation = pt
                    cube.spawn()
                    self.object.transformation = self.last_trans
                    self.last_trans = self.object.transformation.copy()
                    self.destroy()
                    ent.hit(am = 50)
                    self.main.timer_debug.end()
                    self.main.timer_debug.end()
                    return
        self.last_trans = self.object.transformation.copy()
        self.main.timer_debug.end()

        self.main.timer_debug.end()

class EntityCube(Entity):
    def __init__(self,main,scaleVector=[1,1,1,1],obj_size=1, no_bounding_box=False):
        Entity.__init__(self, main, mesh = main.meshs["cube"], texture = main.textures['cube'], scaleVector=scaleVector, obj_size=obj_size, bounding_box_forced = not no_bounding_box)
        self.collidable = False
        self.hide_bounding_box = True
