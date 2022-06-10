#version 330 core

//Fog
in float visibility;
uniform vec3 skyColor;

// Variable de sortie (sera utilisé comme couleur)
out vec4 color;

in vec4 vcolor;
in vec2 vtex;

uniform sampler2D t;

void main (void)
{
  //recuperation de la texture
  vec4 color_texture = texture(t, vtex);
  color   = vcolor*color_texture;

}
