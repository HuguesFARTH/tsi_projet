from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Object3D, Camera, Transformation3D
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

    def intersect(self,position):
        return pyrr.vector3.length(self.position-position) < size

    def adapt(self,transformation):
        self.position = transformation.translation + self.offset

    def draw(self):
        self.ent.render()

class Entity():
    def __init__(self, main, mesh, texture, obj_size = 1,scaleVector =  [1, 1, 1, 1], bounding_box = None, name = "entity"):
        self.main = main
        self.mesh = mesh.copy()
        self.name = name
        self.mesh.apply_matrix(pyrr.matrix44.create_from_scale(pyrr.Vector4(scaleVector)*obj_size))
        # self.mesh = Mesh.load_obj("rafale_texture/cube.obj")
        # self.mesh.normalize()
        # self.mesh.apply_matrix(pyrr.matrix44.create_from_scale(pyrr.Vector4(scaleVector)*obj_size))
        tr = Transformation3D()
        self.texture = texture#glutils.load_texture(texture)
        self.object = Object3D(self.mesh.load_to_gpu(), self.mesh.get_nb_triangles(), self.main.program3d_id, self.texture, tr)
        self.start_tick = self.main.ticks_time
        self.bounding_boxes = []
        self.bounding_boxes.append(bounding_box)

    def addBounding_Boxe(self, bounding_box):
        self.bounding_box.append(bounding_box)

    def render(self):
        self.object.render()

    def intersect(self,position):
        for bounding_box in self.bounding_boxes:
            if not bounding_box == None:
                if bounding_box.intersect(position):
                    return True
            else:
                self.bounding_boxes.remove(bounding_box)

    def update(self):
        for bounding_box in self.bounding_boxes:
            if not bounding_box == None:
                bounding_box.adapt(self.object.transformation)
            else:
                self.bounding_boxes.remove(bounding_box)

    def spawn(self):
        self.main.entities.append(self)

    def destroy(self):
        self.main.entities.remove(self)

    def collide(self):
        pass

class EntityRafale(Entity):
    def __init__(self,main, name = "Rafale"):
        Entity.__init__(self, main, name = name, mesh = main.meshs["rafale"], texture = main.textures['rafale'],bounding_box = BoundingBox(main,size = 0.15, offset = pyrr.Vector3([0,-0.15,0])))
        self.max_speed = 5
        self.speed = 0.1
        self.acceleration = 0.002
        self.de_acceleration = self.acceleration*2
        # Tir à gauche ou droite
        self.object.transformation.rotation_center.y = -2
        self.last_shoot = False
        # self.object.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
    def render(self):
        Entity.render(self)

    def update(self):
        Entity.update(self)
        self.object.transformation.rotation_euler[pyrr.euler.index().roll] %= (2*math.pi)
        pitch = self.object.transformation.rotation_euler[pyrr.euler.index().pitch]
        pas = 0.005
        # self.object.transformation.translation += \
            # pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.object.transformation.rotation_euler), pyrr.Vector3([0, 0,self.speed]))
        # self.main.player.object.transformation.rotation_euler[pyrr.euler.index().pitch]  %= 2*math.pi

    def input(self):
        pass

    def shoot(self):
        self.main.timer_debug.start("shoot")
        dir = pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.object.transformation.rotation_euler), pyrr.Vector3([0, 0,1]))
        bullet = EntityBullet(self.main,dir,scaleVector=[0.5,0.5,1,1],obj_size=0.1)
        bullet.object.transformation.translation = self.object.transformation.translation + pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.object.transformation.rotation_euler),  pyrr.Vector3([0.28 if self.last_shoot else -0.28 ,-0.18,-0.355]))
        bullet.object.transformation.rotation_euler = self.object.transformation.rotation_euler.copy();
        bullet.spawn()
        self.last_shoot = not self.last_shoot
        self.main.timer_debug.end()
        return bullet

class EntityPlayer(EntityRafale):
    def __init__(self,main):
        EntityRafale.__init__(self,main, name = "Player")
        self.object.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
        # self.bullet = self.shoot()
        # self.bullet.direction = pyrr.Vector3([0, 0, 0])
        # time in ms
        self.fire_rate = 1000.0/10
        self.last_shoot = self.main.msTime()
        # self.object.render_mode = 1


    def render(self):
        EntityRafale.render(self)

    def update(self):
        EntityRafale.update(self)
        # self.bullet.object.transformation.rotation_euler = self.object.transformation.rotation_euler.copy();
        # print(self.object.transformation.translation-self.bullet.object.transformation.translation)

    def input(self):
        EntityRafale.input(self)
        current_time = self.main.msTime()
        if self.main.mouse_catched and self.main.MouseIsPressed(glfw.MOUSE_BUTTON_LEFT) and (current_time - self.last_shoot) > self.fire_rate:
                self.shoot()
                self.last_shoot = current_time
                return

        if self.main.keyIsPressed(glfw.KEY_W):
            # yaw = self.object.transformation.rotation_euler[pyrr.euler.index().yaw]
            # self.object.transformation.translation += pyrr.Vector3([-self.speed*math.sin(yaw),0,self.speed*math.cos(yaw)])
            self.object.transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.object.transformation.rotation_euler), pyrr.Vector3([0, 0,self.speed]))

        if self.main.keyIsPressed(glfw.KEY_S):
            # yaw = self.object.transformation.rotation_euler[pyrr.euler.index().yaw]
            # self.object.transformation.translation += pyrr.Vector3([+self.speed*math.sin(yaw),0,-self.speed*math.cos(yaw)])
            self.object.transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.object.transformation.rotation_euler), pyrr.Vector3([0, 0,-self.speed]))

        if self.main.keyIsPressed(glfw.KEY_A):
            # yaw = self.object.transformation.rotation_euler[pyrr.euler.index().yaw]
            # self.object.transformation.translation += pyrr.Vector3([self.speed*math.cos(yaw),0,self.speed*math.sin(yaw)])
            self.object.transformation.rotation_euler[pyrr.euler.index().yaw] -= self.speed/4
        if self.main.keyIsPressed(glfw.KEY_D):
            # yaw = self.object.transformation.rotation_euler[pyrr.euler.index().yaw]
            # self.object.transformation.translation += pyrr.Vector3([-self.speed*math.cos(yaw),0,-self.speed*math.sin(yaw)])
            self.object.transformation.rotation_euler[pyrr.euler.index().yaw] += self.speed/4

        if self.main.keyIsPressed(glfw.KEY_SPACE):
            self.object.transformation.translation += pyrr.Vector3([0, self.speed,0])
            # self.object.transformation.rotation_euler[pyrr.euler.index().roll] += self.speed/4

        if self.main.keyIsPressed(glfw.KEY_LEFT_SHIFT):
            # self.object.transformation.translation += pyrr.Vector3([0, -self.speed,0])
            self.object.transformation.rotation_euler[pyrr.euler.index().roll] -= self.speed/4

        return
        # TEST bullet move
        if self.main.keyIsPressed(glfw.KEY_I):
            # yaw = self.object.transformation.rotation_euler[pyrr.euler.index().yaw]
            # self.object.transformation.translation += pyrr.Vector3([-self.speed*math.sin(yaw),0,self.speed*math.cos(yaw)])
            self.bullet.object.transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.bullet.object.transformation.rotation_euler), pyrr.Vector3([0, 0,self.speed]))

        if self.main.keyIsPressed(glfw.KEY_K):
            # yaw = self.object.transformation.rotation_euler[pyrr.euler.index().yaw]
            # self.object.transformation.translation += pyrr.Vector3([+self.speed*math.sin(yaw),0,-self.speed*math.cos(yaw)])
            self.bullet.object.transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.bullet.object.transformation.rotation_euler), pyrr.Vector3([0, 0,-self.speed]))

        if self.main.keyIsPressed(glfw.KEY_J):
            yaw = self.bullet.object.transformation.rotation_euler[pyrr.euler.index().yaw]
            self.bullet.object.transformation.translation += pyrr.Vector3([self.bullet.speed*math.cos(yaw),0,self.bullet.speed*math.sin(yaw)])

        if self.main.keyIsPressed(glfw.KEY_L):
            yaw =  self.bullet.object.transformation.rotation_euler[pyrr.euler.index().yaw]
            self.bullet.object.transformation.translation += pyrr.Vector3([-self.bullet.speed*math.cos(yaw),0,-self.bullet.speed*math.sin(yaw)])

        if self.main.keyIsPressed(glfw.KEY_O):
            self.bullet.object.transformation.translation += pyrr.Vector3([0, self.bullet.speed,0])

        if self.main.keyIsPressed(glfw.KEY_P):
            self.bullet.object.transformation.translation += pyrr.Vector3([0, -self.bullet.speed,0])

class EntityBullet(Entity):
    def __init__(self,main,dir,scaleVector=[1,1,1,1],obj_size=0.05):
        Entity.__init__(self, main, mesh = main.meshs["cube"], texture = main.textures['bullet'], scaleVector=scaleVector,obj_size=obj_size)
        self.speed = 0.001
        self.direction = dir
        self.tick_life = 1000
        # self.object.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi

    def render(self):
        # return
        Entity.render(self)

    def update(self):
        self.object.transformation.translation += self.direction*self.speed
        if self.main.ticks_time - self.start_tick > self.tick_life < 0:
            self.destroy()

    def spawn(self):
        self.main.particules.append(self)

    def destroy(self):
        self.main.particules.remove(self)

class EntityCube(Entity):
    def __init__(self,main,scaleVector=[1,1,1,1],obj_size=1):
        Entity.__init__(self, main, mesh = main.meshs["cube"], texture = main.textures['cube'], scaleVector=scaleVector,obj_size=obj_size)
