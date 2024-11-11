#version 330 core

// Input from the vertex shader
in vec3 fragPosition;
in vec3 fragNormal;

// Output color
out vec4 FragColor;

// Light and camera position in world space
uniform vec3 lightPosition;
uniform vec3 lightColour;
uniform vec3 cameraPosition;

// Material coefficients

uniform vec3 ambientCoefficient;
uniform vec3 diffuseCoefficient;
uniform vec3 specularCoefficient;
uniform float shininess;
uniform vec4 objectColour;


void main() {
    // Normalize the normal vector
    vec3 norm = normalize(fragNormal);

    // Calculate the light direction vector
    vec3 lightDir = normalize(lightPosition - fragPosition);

    // Ambient component
    vec3 ambient = ambientCoefficient;

    // Diffuse component (Lambert's cosine law)
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * diffuseCoefficient;

    // Specular component (Blinn-Phong reflection model)
    vec3 viewDir = normalize(cameraPosition - fragPosition);
    vec3 halfwayDir = normalize(lightDir + viewDir); // halfway vector between light and view directions
    float spec = pow(max(dot(norm, halfwayDir), 0.0), shininess);
    vec3 specular = spec * specularCoefficient;

    // Combine components
    vec4 result = vec4((ambient + (diffuse + specular) * lightColour), 1.0) * objectColour;
    FragColor = result;
}