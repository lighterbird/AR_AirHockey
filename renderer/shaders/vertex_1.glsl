#version 330 core

// Uniform matrices for camera and model transformations
uniform mat4 cameraMatrix;
uniform mat4 modelMatrix;

// Input vertex position
layout(location = 0) in vec3 position;

void main() {
    // Transform the vertex position by model and camera matrices
    gl_Position = cameraMatrix * modelMatrix * vec4(position, 1.0);
    // gl_Position = vec4(position, 1.0);
}