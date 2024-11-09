import numpy as np
from scipy.spatial.transform import Rotation as R

# Define Euler angles in radians
euler_angles = [3.09503425, -0.05681953, 0.57382914]

# Create rotation object based on XYZ rotation order
rotation = R.from_euler('ZYX', euler_angles)

# Convert to a 3x3 rotation matrix
rotation_matrix = rotation.as_matrix()

print("Rotation matrix:\n", rotation_matrix)