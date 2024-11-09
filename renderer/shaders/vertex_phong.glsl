#version 330 core

// Input layout positions
layout(location = 0) in vec3 position; // Vertex position
layout(location = 1) in vec3 normal;   // Vertex normal

// Output data to the fragment shader
out vec3 fragPosition;
out vec3 fragNormal;

// Uniform matrices for transformations
uniform mat4 cameraMatrix;
uniform mat4 modelMatrix;

// Light and camera position in world space
uniform vec3 lightPosition;
uniform vec3 cameraPosition;

void main() {
    // Transform the vertex position by model and camera matrices
    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    fragPosition = worldPosition.xyz;  // Position in world space for lighting calculations
    
    // Transform normal to world space
    fragNormal = (modelMatrix * vec4(normal, 1.0)).xyz - fragPosition;
    
    // Output final position in screen space
    gl_Position = cameraMatrix * worldPosition;
}