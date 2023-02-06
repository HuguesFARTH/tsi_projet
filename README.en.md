# Image Processing and Synthesis
_Languages: [French](README.md), [English](README.en.md)_

## Introduction
The objective of this project is to create a minimalist game using the OpenGL language. To do this, we will develop the game in python using the python library of OpenGL, OpenGL.GL. We have chosen to develop a small fighter plane game. So we embody a plane that moves on a map and passes through circles placed on the map. There is also another plane that tries to crash into us and we have to kill it before that happens. We must also avoid colliding with our environment, otherwise it's "game over".

## Opengl/Shaders
OpenGL is a standardized set of 2D or 3D image calculation functions launched in 1992. OpenGL allows a program to display 3-dimensional objects on the screen, taking into account distance, orientation, shadows, transparency...
To do this, OpenGL uses two types of shaders to create triangles. These triangles are the basis of any object, whether it is a map, a sphere or a plane. First, there is a vertex shader that creates the vertices of the triangles and calculates their position in the 3d environment. Then, the fragment shader takes care of filling these triangles with a certain color, texture...
We created two sets of shaders (vertex and fragment): one is used to manage the 3d display and the whole game, this is the main shader. The second pair displays the game data (altitude, position, speed of the plane...) on the screen.
As for the main shader, allowing the display of entities, terrain and others, we first send the camera data (position, rotation, center of rotation). Once these data are sent, we can then display the entities one by one, and modify their position on the screen. Then the shader takes care of arranging the position of the different vertices on the screen, adding the position of the camera and adjusting according to the angle.
We also added a kind of fog, the further the vertex is from the camera, the more it will blend with the color of the sky. So we have a horizon impression.

## Objects
### [Main](main.py)
It is the main object of the game, managing the instantiation of different entities, their updates, renderings, keyboard/mouse input.
The loop function is the project's loop. It manages when to update the display, update the entities while keeping the FPS and TICK (update/s) limits as stable as possible that are defined for it.
The loadMeshAndTexture function allows loading the different models/textures that will be used, generating the meshes and vao. This avoids instantiating the same model multiple times in the GPU.
There are also many other functions that can 'catch' the mouse, make an Ring appear, a Ghost Burst, display the end hud.
In the initialization we generate the terrain, the player, the cameras, the initialization of the window, the shaders, the different huds...

### [Camera](cpe3d.py#L72)

This is a virtual camera, symbolizing the location that should be displayed on the screen. It can undergo translations and rotations. In the shader, each object refers to the camera. Camera3P is inherited from Camera. Camera3P is a camera with its rotation center at the object being targeted (for example the player). This way, you can turn around the entity independently of its movements, move away or closer while keeping the "view" fixed on the latter.

### [HudPlayerFonction](hud.py#L162)

This is an object for displaying text on the screen. It inherits from HudV2, which is a modified version of the provided Hud. As a parameter, it is given a function that returns what should be displayed every tick. For display, like Hud, we define which shader we give the texture number, we send the different variables to the shader, and finally display the text with 2 triangles.
This object allows us to display real-time score, position, and several other information on the screen directly. It is also possible to define the text size.

### [Entity](rafale.py)

This is a class for all entities, it groups information, stores different variables specific to each entity (texture, vao), and creates the object.
We also define collision boxes (here they are spheres) which will later help us manage the different collisions with the terrain and other entities:

* self.collidable: the entity handles collisions
* self.hide_bounding_box: hide or show the collision boxes
* self.destroy_if_collide: the entity is destroyed if it touches something
* self.can_be_collided: the entity can receive a collision
* self.transparent: the entity can receive a collision but is not solid (can pass through)

Regarding collisions, it is sufficient to check for each box if the distance with the box of the other entity is less than both radii.
The game capture shows the different collision boxes of the player, a large one to make a first rough test, and smaller ones for precision.
Terrain collisions will be explained later.

[`EntityBullet`](rafale.py#L497) :
For this entity, we need to redo the collisions. Indeed, its high movement speed makes it not optimal to check 60 times per second if it hits anything. So we choose to check the intersection between a line and a sphere. When it hits an entity other than its launcher, it deals 50 damage.

[`EntityRafale`](rafale.py#L254):
Main class of a rafale. Larger collision boxes to make it easier to hit, many modifications excluding the player allow the aircraft to be invulnerable to walls, continuously following the player wherever he goes at a constant speed. We can notice different interesting functions: goForward allowing the rafale to move forward in the direction it is facing, the shoot function making it shoot a bullet, and regulatePitch automatically straightening the aircraft horizontally (useful for the player)

[`EntityPlayer`](rafale.py#L394):
Inherits from EntityRafale but mainly contains the input part (movements, shooting, adding a ring, activation/deactivation of pitch regulation).
The player is the only aircraft that can shoot for now, shooting bullets in the direction it is facing on either side of where it is facing. A black line allows observing the direction the projectiles will take.

[`EntityRing`](rafale.py#L547)
A ring that if crossed by a player increases their score. The longer the ring stays on the field, the less points it gives.

## [Terrain](terrain.py)
This class manages the display of the terrain, its creation from an image (heightmap), saves the different heights and manages collisions with the terrain. To do this, we aim to calculate the intersection between a plane (triangle at the position) and the direction line (0,1,0), thus locally retrieving the height of the terrain.
This capture illustrates the simple generation of mountains, reacting well to shadows.

## [Object3D](cpe3d.py#L35)
A class containing all the information necessary to display an object: its transformation (translation, rotation) and its texture, vao, and number of triangles.

## [timerDebug](timeDebug.py)
Utility class for debugging time of function execution.

## Conclusion
This project allowed us to take our first step into the design of 3D games with OpenGl. We learned how to manage a camera, its different viewing angles, use shaders to display objects according to the camera. The functions made available to us allowed us to load textures, .obj and instance them in the GPU for simplified use later, allowing for intelligent reuse. We were able to learn the basics of HUDs, collisions in a 3D environment, interaction with keyboard/mouse inputs and the notion of projectiles.
