import math
from mesh import Mesh
from cpe3d import Object3D, Transformation3D
import numpy as np
from PIL import Image
import os
import pyrr
import OpenGL.GL as GL
import c_math

class Terrain:
    def __init__(self, main, tile_size = 800, vertex_count=128, max_height = 150):
        self.main = main
        self.tile_size = tile_size
        self.vertex_count = vertex_count
        self.max_height = max_height
        self.max_p_color = 256 * 256 * 256
        self.loadHeightMap()
        self.t = self.generateTerrain()
        self.t.transformation.rotation_center = -pyrr.Vector3([self.tile_size/2,0,self.tile_size/2])
        # self.t.render_mode = 1


    def loadHeightMap(self):
        filename = "heightmap1.png"
        if not os.path.exists(filename):
            print(f'{25*"-"}\nError reading file:\n{filename}\n{25*"-"}')
        self.heightmap_image = Image.open(filename)


    def render(self):
        firstT = self.t.transformation.copy()
        self.t.render()
        self.t.transformation = firstT
        return
        for x in range(-1,2):
            for z in range(-1,2):
                if not abs(x*z) == 1:
                    self.t.transformation.rotation_euler[pyrr.euler.index().yaw] = math.pi
                self.t.transformation.translation.x = x*self.tile_size
                self.t.transformation.translation.z = z*self.tile_size
                self.t.render()

    def getRawHeight(self,x_pos, z_pos, size):
        map = []
        s = len(range(x_pos-size, x_pos+size))
        for x in range(2*size):
            map.append([0]*(size*2))
            if x_pos+x-size >= len(self.heights) or x_pos+x-size < 0:
                continue
            for z in range(2*size):
                if z_pos+z-size >= len(self.heights[x_pos+x-size]) or z_pos+z-size < 0:
                    continue
                map[x][z] = self.heights[x_pos+x-size][z_pos+z-size]

        return map

    def renderPos(self,x,z):
        pass

    def update(self):
        pass

    def generateTerrain(self, text_mult = 100):
        m = Mesh()
        self.heights = []
        count = self.vertex_count*self.vertex_count
        vertices = []
        indices = []
        for i in range(self.vertex_count):
            for j in range(self.vertex_count):
                n = self.calculateNormals(j,i)
                if len(self.heights) <= j :
                    self.heights.append([])
                self.heights[j].append(self.getHeightPixel(j, i))
                vertices.append( [\
                [-self.tile_size*(j/(self.vertex_count-1)), self.heights[j][i] , -self.tile_size*(i/(self.vertex_count-1))]+ \
                [n.x, n.y, n.z] + [1, 1, 1]+ [j*text_mult/(self.vertex_count-1) , i*text_mult/(self.vertex_count-1)]]
                )
        m.vertices = np.array(vertices, np.float32)
        for gz in range(self.vertex_count-1):
            for gx in range(self.vertex_count-1):
                topLeft = (gz*self.vertex_count) + gx
                topRight = topLeft + 1
                bottomLeft = ((gz+1)*self.vertex_count) + gx
                bottomRight = bottomLeft + 1
                indices.append([topLeft,bottomLeft,topRight])
                indices.append([topRight, bottomLeft, bottomRight])
        m.faces = np.array(indices, np.uint32)
        self.m = m
        return Object3D(m.load_to_gpu(), m.get_nb_triangles(), self.main.program3d_id, self.main.textures['grass'], Transformation3D())

    def calculateNormals(self, x, z):
        heightL = self.getHeightPixel(x-1,z)
        heightR = self.getHeightPixel(x+1,z)
        heightD = self.getHeightPixel(x,z-1)
        heightU = self.getHeightPixel(x,z+1)
        vec = pyrr.Vector3([heightL-heightD, 2 , heightD-heightU])
        vec.normalize()
        return vec

    def getHeightPixel(self, x, z):
        if x >= self.heightmap_image.width or z >= self.heightmap_image.height or x < 0 or z < 0:
            return 0
        else:
            h = self.heightmap_image.getpixel((x,z))
            if not isinstance(h,int):
                h = h[0]*h[1]*h[2]
                h /= self.max_p_color
                h *= self.max_height
            else:
                print("erreur dans la heighmap")
                exit()
            return h

    def setRed(self,x,y,z):
        terrain_x = self.t.transformation.translation.x - x
        terrain_z = self.t.transformation.translation.z - z
        grid_square_size = self.tile_size / (len(self.heights) - 1)
        gridX = int((terrain_x/grid_square_size))
        gridZ = int((terrain_z/grid_square_size))
        if gridX + 1 >= len(self.heights) or gridZ + 1 >= len(self.heights) or gridZ- 1 < 0 or gridX - 1 < 0:
            return 0
        x_coord = (terrain_x % grid_square_size)/self.tile_size
        z_coord = (terrain_z % grid_square_size)/self.tile_size

        GL.glUseProgram(self.t.program)
        loc = GL.glGetUniformLocation(self.t.program, "posToSetRed")
        if not (loc == -1) :
            GL.glUniform3f(loc, int(x), self.heights[gridX][gridZ], int(z))

    # Version par intersection plan/droit (dir)
    def getDistanceBeforeCollide(self, pos, dir, max = 70):
        grid_square_size = self.tile_size / (len(self.heights))
        for i in range(0,max):
            p = pos*dir*(i)
            terrain_d = self.t.transformation.translation - p
            gridX = int((terrain_d.x-0.5)/grid_square_size)
            gridZ = int((terrain_d.z-0.5)/grid_square_size)
            gridX2 = int((terrain_d.x)/grid_square_size)
            gridZ2 = int((terrain_d.z)/grid_square_size)
            if gridX + 1 >= len(self.heights) or gridZ + 1 >= len(self.heights) or gridZ- 1 < 0 or gridX - 1 < 0:
                # print("pass")
                continue
            print("next")
            x_coord = (terrain_d.x - (gridX2*grid_square_size)-0.5)%1
            z_coord = (terrain_d.z - (gridZ2*grid_square_size)-0.5)%1
            if x_coord <= (1-z_coord):
                height = c_math.intersecTriangle(pyrr.Vector3([0,self.heights[gridX][gridZ],0]), pyrr.Vector3([0,self.heights[gridX][gridZ+1],1]),pyrr.Vector3([1,self.heights[gridX+1][gridZ],0]), pyrr.Vector3([x_coord, 0,z_coord]))
            else:
                height = c_math.intersecTriangle(pyrr.Vector3([1,self.heights[gridX+1][gridZ+1],1]), pyrr.Vector3([1,self.heights[gridX+1][gridZ],0]), pyrr.Vector3([0,self.heights[gridX][gridZ+1],1]), pyrr.Vector3([x_coord, 0,z_coord]))
            if height >= p.y:
                return (i)
        return 200

    # Version par intersection plan/droit (0,1,0)
    def getHeightV2(self, x, y, z):
        self.main.timer_debug.start("after")
        terrain_x = self.t.transformation.translation.x - x
        terrain_z = self.t.transformation.translation.z - z
        grid_square_size = self.tile_size / (len(self.heights))
        gridX = int((terrain_x-0.5)/grid_square_size)
        gridZ = int((terrain_z-0.5)/grid_square_size)
        gridX2 = int((terrain_x)/grid_square_size)
        gridZ2 = int((terrain_z)/grid_square_size)
        if gridX + 1 >= len(self.heights) or gridZ + 1 >= len(self.heights) or gridZ- 1 < 0 or gridX - 1 < 0:
            self.main.timer_debug.end()
            return 0
        x_coord = (terrain_x - (gridX2*grid_square_size)-0.5)%1
        z_coord = (terrain_z - (gridZ2*grid_square_size)-0.5)%1
        self.main.timer_debug.end()
        if x_coord <= (1-z_coord):
            height = c_math.intersecTriangle(pyrr.Vector3([0,self.heights[gridX][gridZ],0]), pyrr.Vector3([0,self.heights[gridX][gridZ+1],1]),pyrr.Vector3([1,self.heights[gridX+1][gridZ],0]), pyrr.Vector3([x_coord, 0,z_coord]))
        else:
            height = c_math.intersecTriangle(pyrr.Vector3([1,self.heights[gridX+1][gridZ+1],1]), pyrr.Vector3([1,self.heights[gridX+1][gridZ],0]), pyrr.Vector3([0,self.heights[gridX][gridZ+1],1]), pyrr.Vector3([x_coord, 0,z_coord]))
        return height

    def getHeight(self, x, y, z, fake = False):
        self.main.timer_debug.start("before")
        terrain_x = self.t.transformation.translation.x - x
        terrain_z = self.t.transformation.translation.z - z
        grid_square_size = self.tile_size / (len(self.heights))
        gridX = int((terrain_x-0.5)/grid_square_size)
        gridZ = int((terrain_z-0.5)/grid_square_size)
        gridX2 = int((terrain_x)/grid_square_size)
        gridZ2 = int((terrain_z)/grid_square_size)
        if gridX + 1 >= len(self.heights) or gridZ + 1 >= len(self.heights) or gridZ- 1 < 0 or gridX - 1 < 0:
            return 0
        x_coord = (terrain_x - (gridX2*grid_square_size)-0.5)%1
        z_coord = (terrain_z - (gridZ2*grid_square_size)-0.5)%1
        self.main.timer_debug.end()
        if x_coord <= (1-z_coord):
            height = self.cheackBarryCentre(pyrr.Vector3([0,self.heights[gridX][gridZ],0]), pyrr.Vector3([0,self.heights[gridX][gridZ+1],1]),pyrr.Vector3([1,self.heights[gridX+1][gridZ],0]), x_coord, y, z_coord, fake)
        else:
            height = self.cheackBarryCentre(pyrr.Vector3([0,self.heights[gridX][gridZ+1],1]), pyrr.Vector3([1,self.heights[gridX+1][gridZ+1],1]), pyrr.Vector3([1,self.heights[gridX+1][gridZ],0]), x_coord, y,z_coord, fake)
        return height

    def cheackBarryCentre(self,v1,v2,v3,posX,y,posZ, fake = False):
        max = v1.y
        min = v1.y
        if fake:
            if v2.y > max:
                max = v2.y
            elif v2.y < min:
                min = v2.y
            if v3.y > max:
                max = v3.y
            elif v3.y < min:
                min = v3.y
            if y > max + 1:
                return max
            elif max > y > min and (max - min) > 10:
                return y
            else:
                return self.barryCentre(v1, v2, v3, posX, posZ)
        else:
            return self.barryCentre(v1, v2, v3, posX, posZ)

    def barryCentre(self,v1,v2,v3,posX,posZ):
        det = (v2.z-v3.z)*(v1.x-v3.x) + (v3.x-v2.x)*(v1.z-v3.z)
        l1 = ((v2.z - v3.z) * (posX - v3.x) + (v3.x - v2.x) * (posZ - v3.z))/det
        l2 = ((v3.z - v1.z) * (posX - v3.x) + (v1.x - v3.x) * (posZ - v3.z))/det
        l3 = 1 - l1 - l2
        return l1 * v1.y + l2*v2.y + l3*v3.y
