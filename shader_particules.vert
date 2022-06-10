#version 330 core


//Fog
const float density = 0.006;
const float gradient = 1.5;
out float visibility;

layout (location = 0) in vec3 position;
layout (location = 2) in vec3 color;
layout (location = 3) in vec2 tex;

uniform mat4 rotation_model;
uniform vec4 translation_model;

uniform mat4 rotation_view;
uniform vec4 rotation_center_view;
uniform vec4 translation_view;

uniform mat4 projection;

out vec3 coordonnee_3d;
out vec3 coordonnee_3d_locale;
out vec3 vnormale;
out vec4 vcolor;
out vec2 vtex;

//Un Vertex Shader minimaliste
void main (void)
{
  //application de la deformation du model
  vec4 p_model = rotation_model*(vec4(position, 1.0))+translation_model;
  //application de la deformation de la vue
  vec4 p_modelview = rotation_view*(p_model-rotation_center_view)+rotation_center_view+translation_view;
  //vec4 p_modelview = (p_model-rotation_center_view)+rotation_center_view+translation_view;

  //Projection du sommet
  vec4 p_proj = projection*p_modelview;

  //Couleur du sommet
  vcolor=vec4(color,1.0);

  //position dans l'espace ecran
  gl_Position = p_proj;

  //coordonnees de textures
  vtex=tex;

  //ajout Fog
  float distance = length(coordonnee_3d_locale);
  visibility = exp(-pow((distance*density),gradient));
  visibility = clamp(visibility, 0.0,1.0);
}
