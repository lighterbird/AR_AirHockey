import numpy as np
import pyrr
from OpenGL.GL import *
from renderer.VBO import VertexBuffer
from renderer.IBO import IndexBuffer
from renderer.VAO import VertexArray
from renderer.VBL import VertexBufferLayout
from renderer.Shader import Shader
from renderer.Renderer import Renderer
from renderer.Utils import GLCall

class Object:
    def __init__(self, obj_file_path: str, shader: Shader):
        self.shader = shader

        # Set object position and rotation (Euler angles)
        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.rotation = np.array([0, 0, 0], dtype=np.float32)
        self.scale = np.array([1, 1, 1], dtype=np.float32)
        self.colour = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.diffuseCoeff = np.array([1, 1, 1], dtype=np.float32)
        self.specularCoeff = np.array([1, 1, 1], dtype=np.float32)
        self.ambientCoeff = np.array([1, 1, 1], dtype=np.float32)
        self.shine = 10

        self.modelMatrix = None

        vertices, indices = self.LoadObjNormals(obj_file_path)
        # print(f"Vertices: {vertices}\nIndices: {indices}")

        # Create Vertex Buffer Object (VBO) for vertices
        self.vbo = VertexBuffer(np.array(vertices, dtype=np.float32))

        # Create Index Buffer Object (IBO) for indices
        self.ibo = IndexBuffer(np.array(indices, dtype=np.uint32), len(indices))

        # Create Vertex Buffer Layout (VBL) and define the structure
        self.vbl = VertexBufferLayout()
        self.vbl.Push("float", 3)  # 3 pos
        self.vbl.Push("float", 3)  # 3 normals

        # Create Vertex Array Object (VAO) and add VBO and VBL to it
        self.vao = VertexArray()
        self.vao.AddBuffer(self.vbo, self.vbl)

        self.renderer = Renderer()

    def LoadOBJ(self, filepath: str):
        vertices = []
        indices = []
        vertex_index = {}

        with open(filepath, 'r') as file:
            for line in file:
                if line.startswith('v '):  # Vertex position line
                    parts = line.split()
                    x, y, z = map(float, parts[1:4])
                    vertices.extend([x, y, z])
                elif line.startswith('f '):  # Face line
                    parts = line.split()
                    for part in parts[1:]:
                        idx = int(part.split('/')[0]) - 1  # OBJ indices start at 1
                        indices.append(idx)

        return vertices, indices
    def LoadObjNormals(self, filepath: str):
        vertices = []
        indices = []
        temp_vertices = []
        temp_normals = []
        
        with open(filepath, 'r') as file:
            for line in file:
                parts = line.split()
                if not parts:
                    continue
                
                prefix = parts[0]
                
                # Parse vertex positions
                if prefix == 'v':
                    position = list(map(float, parts[1:4]))
                    temp_vertices.append(position)
                    
                # Parse vertex normals
                elif prefix == 'vn':
                    normal = list(map(float, parts[1:4]))
                    temp_normals.append(normal)
                    
                # Parse faces (indices and normals)
                elif prefix == 'f':
                    face_indices = []
                    for part in parts[1:]:
                        temp = part.split('//')
                        #print(temp)
                        v, vn = map(int, temp)
                        # Convert to zero-based index
                        v -= 1
                        vn -= 1
                        
                        # Prepare vertex data
                        position = temp_vertices[v]
                        normal = temp_normals[vn]
                        vertex_data = position + normal
                        if vertex_data not in vertices:
                            vertices.append(vertex_data)
                        
                        # Track the index for faces
                        face_indices.append(vertices.index(vertex_data))
                    
                    # Add triangle indices
                    indices.extend(face_indices)
        flattened_vertices = [item for sublist in vertices for item in sublist]
        return flattened_vertices, indices
    def Draw(self, modelMatrix = None):
        if modelMatrix is None:
            # Create the model matrix from position and rotation
            translation_matrix = pyrr.matrix44.create_from_translation(self.position, dtype=np.float32).T
            
            scaling_matrix = pyrr.matrix44.create_from_scale(self.scale)
            
            rotation_matrix_x = pyrr.matrix44.create_from_x_rotation(np.radians(self.rotation[0]), dtype=np.float32).T
            rotation_matrix_y = pyrr.matrix44.create_from_y_rotation(np.radians(self.rotation[1]), dtype=np.float32).T
            rotation_matrix_z = pyrr.matrix44.create_from_z_rotation(np.radians(self.rotation[2]), dtype=np.float32).T
            rotation_matrix = pyrr.matrix44.multiply(m1=rotation_matrix_z, m2=pyrr.matrix44.multiply(m1=rotation_matrix_y, m2=pyrr.matrix44.multiply(rotation_matrix_x, scaling_matrix)))
            
            # Combine the translation, scale and rotation matrices
            self.model_matrix =  pyrr.matrix44.multiply(m1=translation_matrix, m2=pyrr.matrix44.multiply(scaling_matrix, rotation_matrix))
        else:
            self.modelMatrix = modelMatrix
        
        # Set the uniforms in the shader
        self.shader.SetUniformMatrix4fv("modelMatrix", self.model_matrix)
        self.shader.SetUniform4f("objectColour", self.colour[0], self.colour[1], self.colour[2], self.colour[3])
        self.shader.SetUniform3f("diffuseCoefficient", self.diffuseCoeff[0], self.diffuseCoeff[1], self.diffuseCoeff[2])
        self.shader.SetUniform3f("specularCoefficient", self.specularCoeff[0], self.specularCoeff[1], self.specularCoeff[2])
        self.shader.SetUniform3f("ambientCoefficient", self.ambientCoeff[0], self.ambientCoeff[1], self.ambientCoeff[2])
        self.shader.SetUniform1f("shininess", self.shine)

        # Draw the object
        self.renderer.Draw(self.vao, self.ibo, self.shader)