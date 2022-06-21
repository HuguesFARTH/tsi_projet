import pyrr
import math

def produit_vectoriel(v1,v2):
    return pyrr.Vector3([v1.y*v2.z-v1.z*v2.y,v1.z*v2.x-v1.x*v2.z,v1.x*v2.y-v1.y*v2.x])

def produit_scalaire(v1,v2):
    return v1.x*v2.x + v1.y*v2.y + v1.z*v2.z

# s1: sommet 1
# s2: sommet 1
# s3: sommet 1
# pt: point coordonnées x,y,z de test (peut import la valeur de y)
def intersecTriangle(s1,s2,s3,pt,dir = pyrr.Vector3([0,1,0])):
    pt.y = 0
    n = produit_vectoriel(s1 - s2,s3 - s2)
    d = -(s1.x*n.x + s1.y*n.y + s1.z*n.z)
    t = -(produit_scalaire(pt,n) + d)/produit_scalaire(dir,n)
    return pt.y + dir.y*t


'''
                                            # $ % & { } ( )
'''
def getArrow(fr, yaw, to):
    dx = to.x - fr.x;
    dz = to.z - fr.z;
    baseAngleWithZAxis = math.degrees(math.atan(dx / dz)) #+ (180 if (dx >= 0) else -180)
    finalAngle = baseAngleWithZAxis + math.degrees(yaw)
    finalAngle = -(finalAngle%360)+180
    if (-22.5 < finalAngle and finalAngle < 22.5): return "%"
    if (22.5 < finalAngle and finalAngle < 67.5): return ")"
    if (67.5 < finalAngle and finalAngle < 112.5): return "$"
    if (112.5 < finalAngle and finalAngle < 157.5): return "}"
    if (157.5 < finalAngle or finalAngle < -157.5): return "&"
    if (-157.5 < finalAngle and finalAngle < -112.5): return "{"
    if (-112.5 < finalAngle and finalAngle < -67.5): return "#"
    if (-67.5 < finalAngle and finalAngle < -22.5): return "("
    return "-"
