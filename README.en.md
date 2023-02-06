# Projet Traitement et Synthèse d'Image
_Langues: [Français](README.md), [Anglais](README.en.md)_

## Introduction
The objective of this project is to create a minimalist game using the OpenGL language. To do this, we will develop the game in python using the python library of OpenGL, OpenGL.GL. We have chosen to develop a small fighter plane game. So we embody a plane that moves on a map and passes through circles placed on the map. There is also another plane that tries to crash into us and we have to kill it before that happens. We must also avoid colliding with our environment, otherwise it's "game over".

## Opengl/Shaders
OpenGL is a standardized set of 2D or 3D image calculation functions launched in 1992. OpenGL allows a program to display 3-dimensional objects on the screen, taking into account distance, orientation, shadows, transparency...
To do this, OpenGL uses two types of shaders to create triangles. These triangles are the basis of any object, whether it is a map, a sphere or a plane. First, there is a vertex shader that creates the vertices of the triangles and calculates their position in the 3d environment. Then, the fragment shader takes care of filling these triangles with a certain color, texture...
We created two sets of shaders (vertex and fragment): one is used to manage the 3d display and the whole game, this is the main shader. The second pair displays the game data (altitude, position, speed of the plane...) on the screen.
As for the main shader, allowing the display of entities, terrain and others, we first send the camera data (position, rotation, center of rotation). Once these data are sent, we can then display the entities one by one, and modify their position on the screen. Then the shader takes care of arranging the position of the different vertices on the screen, adding the position of the camera and adjusting according to the angle.
We also added a kind of fog, the further the vertex is from the camera, the more it will blend with the color of the sky. So we have a horizon impression.

## Objects
### Main
It is the main object of the game, managing the instantiation of different entities, their updates, renderings, keyboard/mouse input.
The loop function is the project's loop. It manages when to update the display, update the entities while keeping the FPS and TICK (update/s) limits as stable as possible that are defined for it.
The loadMeshAndTexture function allows loading the different models/textures that will be used, generating the meshes and vao. This avoids instantiating the same model multiple times in the GPU.
There are also many other functions that can 'catch' the mouse, make an Ring appear, a Ghost Burst, display the end hud.
In the initialization we generate the terrain, the player, the cameras, the initialization of the window, the shaders, the different huds...

### Camera

This is a virtual camera, symbolizing the location that should be displayed on the screen. It can undergo translations and rotations. In the shader, each object refers to the camera. Camera3P is inherited from Camera. Camera3P is a camera with its rotation center at the object being targeted (for example the player). This way, you can turn around the entity independently of its movements, move away or closer while keeping the "view" fixed on the latter.

### HudPlayerFonction

This is an object for displaying text on the screen. It inherits from HudV2, which is a modified version of the provided Hud. As a parameter, it is given a function that returns what should be displayed every tick. For display, like Hud, we define which shader we give the texture number, we send the different variables to the shader, and finally display the text with 2 triangles.
This object allows us to display real-time score, position, and several other information on the screen directly. It is also possible to define the text size.

### Entity

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

`EntityBullet` :
	Pour cette entité on doit refaire les collisions. En effet sa vitesse de déplacement importante il est peu optimiser de vérifier 60/s si elle touche quelque chose. On choisit donc de vérifier l’intersection entre une droite et une sphère. Quand elle touche une entité autre que son lanceur elle inflige 50 dégats.

`EntityRafale`  :
	Classe principale d’un rafale. Des boites de collision plus grande pour faciliter le touché, de nombreuses modifications excluant le joueur permettent de rendre cet avion invulnérable aux murs, suivant sans relâche le joueur où qu’il aille à vitesse constante. On peut relever différentes fonctions intéressantes : goForward permettant au rafale d’avancer dans la direction où il regarde, la fonction shoot lui faisant tirer une balle, regulePitch permettant de redresser automatiquement l’avion à l’horizontale (utile pour le joueur)

`EntityPlayer`:
	Hérite de EntityRafal mais contient principalement la partie input (déplacements, tir, ajout d’un anneau, activation/désactivation de la régulation du pitch).
	Le joueur étant le seul avion à pouvoir tirer pour le moment, tire les balles dans la direction où il regarde de part et d’autre d’où il regarde. Une ligne noire permet d’observer la direction que prendrons les projectiles.


`EntityRing`
	Anneau qui si traversé par un joueur lui augmente le score. Plus l’anneau reste longtemps sur le terrain moins il donne de points.

## Terrain

Cette classe gère l’affichage du terrain, sa création à partir d’une image (heightmap), sauvegarde les différentes hauteurs et gère les collisions avec le terrain. Pour cela on cherche à calculer l’intersection entre un plan (triangle à la position), et la droite de direction (0,1,0) on récupère ainsi la hauteur du terrain localement.
Cette capture illustre la génération de montagnes de façon simple, réagissant bien aux ombres

## Object3D

Une classe comprenant toutes les informations nécessaires à l’affichage d’un objet : sa transformation (translation, rotation) ainsi que sa texture, son vao et son nombre de triangles.

## timerDebug

Classe utilitaire permettant de faire du debug de temps d’exécution de fonctions

## Conclusion

Ce projet nous a permis de faire un premier pas dans la conception de jeux en 3D avec OpenGl. On y a appris à gérer une caméra, ses différents angles de vus, utiliser les shaders pour afficher les objets selon la caméra. Les fonctions mises à notre disposition nous ont permis de charger les textures, les .obj et de les instancier dans le gpu pour une utilisation simplifiée par la suite, permettant une réutilisation intelligente. On a pu apprendre les bases sur les huds, les collisions dans un environnement 3D, l’interaction avec les entrées clavier/souris et la notion de projectiles.
