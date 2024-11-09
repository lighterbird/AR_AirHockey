#version 330 core

// Input from the vertex shader
in vec3 fragPosition;
in vec3 fragNormal;

// Output color
out vec4 FragColor;

// Light and camera position in world space
uniform vec3 lightPosition;
uniform vec3 cameraPosition;

// Material coefficients
const vec3 ambientCoefficient = vec3(0.2, 0.2, 0.2);
const vec3 diffuseCoefficient = vec3(0.5, 0.5, 0.5);
const vec3 specularCoefficient = vec3(1.0, 1.0, 1.0);
const float shininess = 32.0;

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
    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, 1.0);
}