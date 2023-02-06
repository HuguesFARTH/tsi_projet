# Projet Traitement et Synthèse d'Image
## Introduction
L’objectif de ce projet est de réaliser un jeu minimaliste avec le langage OpenGL. Pour cela, nous développerons le jeu en python en utilisant la libraire python d’OpenGL, OpenGL.GL. Nous avons fait le choix de développer un petit jeu d’avion de chasse. On incarne donc un avion qui se déplace dans une carte et qui passer à travers des cercles placés sur la carte. Il existe également un autre avion qui essaye de nous foncer dessus et que nous devons tuer avant que ça n’arrive. On doit également éviter de rentrer en collision avec notre environnement, car sinon c’est « game over ».
## OPENGL/SHADERS
OpenGL est un ensemble normalisé de fonctions de calcul d'images 2D ou 3D lancé en 1992. OpenGL permet à un programme d’afficher des objets tridimensionnels à l’écran en tenant compte de la distance, l’orientation, les ombres, la transparence… . 
Pour ce faire, OpenGL utilise deux types de shaders afin de créer des triangles. Ces triangles sont la base de tout objet, que ce soit une map, une sphère ou un avion. Il y a tout d’abord un vertex shader qui va créer les sommets des triangles et calculer leur position dans l’environnement 3d. Ensuite, le fragment shader s’occupe de remplir ces triangles d’un certaine couleur, texture … .
Nous avons créé deux couples de shader (vertex et fragment) : l’un est utilisé pour gérer l’affichage 3d et l’ensemble du jeu, c’est le shader principal. Le second couple affiche à l’écran les données du jeu (altitude, position, vitesse de l’avion…).
Pour ce qui est du shader principal, permettant l’affichage des entités, terrain et autre, on envoie dans un premier temps les données de la caméra (position, rotation, centre de rotation). Une fois ces données envoyées, on peut ensuite afficher une par une les entités, et modifier leur position à l’écran. Par la suite le shader s’occupe d’arranger la position des différents vertex à l’écran, ajoutant la position de la caméra et ajustant selon l’angle.
	On a également ajouté une sorte de brouillard, plus le vertex est loin de la caméra, plus il se confondra avec la couleur du ciel. Ainsi on a une impression d’horizon.
## Les objets

### Main
Il s’agit de l’objet principal du jeu, gérant l’instanciation des différentes entités, leurs updates, les rendus, input clavier/souris.
La fonction loop est la boucle du projet. Elle gère quand actualiser l’affichage, update les entités en gardant le plus stable possible les limites de FPS et TICK (update/s) que l’on lui définit.
La fonction loadMeshAndTexture permet de charger les différents modèles/textures qui seront utilisées, générant les mesh et vao. On évite ainsi d’instancier plusieurs fois le même modèle dans le GPU.
On y retrouve aussi de nombreuses autres fonctions permettant ‘d’attraper’ la souris, faire apparaitre un Anneau, un Rafale fantôme, afficher l’hud de fin.
Dans l’initialisation on y génère le terrain, le joueur, les caméras, l’initialisation de la fenêtre, des shaders, des différents hud…

### Camera

Il s’agit d’une caméra virtuelle, symbolisant l’emplacement qui doit être rendu à l’écran. Elle peut subir des translations et des rotations. Dans le schader chaque objet a pour référence la caméra. Camera3P est hérité de Camera. Camera3P est une caméra avec pour centre de rotation celui de l’objet visé (par exemple le joueur). On peut ainsi tourner autour de l’entité indépendamment de ses mouvements à elle, s’éloigner ou se rapprocher tout en gardant le « regard » fixé sur ce dernier. 

### HUDPLAYERFONCTION

Il s’agit d’un objet permettant d’afficher du texte à l’écran. Il hérite de HudV2 qui est une version modifiée du Hud fournit. En paramètre on lui donne une fonction retournant ce qui doit être affiché tous les ticks. Pour l’affichage, de la même manière que Hud on définit quel shader on lui donne le numéro de texture, on envoie vers le shader les différentes variables puis enfin on affiche le texte avec 2 triangles.
Cet objet nous permet d’afficher en temps réel le score, la position, ainsi que plusieurs autres informations à l’écran directement. Il est également possible de définir la taille du texte.

