# Motion Sequence Data Format

Each motion sequence is stored as a NumPy `.npz` file containing several fields that describe the motion data.

## Notation
- `F`: Total number of frames  
- `D`: Number of degrees of freedom (joints)  
- `B`: Number of bodies (links)  

## Fields

- **`fps`**: shape = (1,)  
  Frames per second (FPS) of the motion sequence.

- **`dof_names`**: shape = (D,)  
  Names of the joints (degrees of freedom).

- **`body_names`**: shape = (B,)  
  Names of the bodies (links).

- **`dof_positions`**: shape = (F, D)  
  Joint positions for each frame.

- **`dof_velocities`**: shape = (F, D)  
  Joint velocities for each frame.

- **`body_positions`**: shape = (F, B, 3)  
  Global position of each body at every frame, in Cartesian coordinates `(x, y, z)`.

- **`body_rotations`**: shape = (F, B, 4)  
  Global orientation of each body as quaternions, in the format `(w, x, y, z)`.

- **`body_linear_velocities`**: shape = (F, B, 3)  
  Linear velocity of each body at every frame, in Cartesian components `(vx, vy, vz)`.

- **`body_angular_velocities`**: shape = (F, B, 3)  
  Angular velocity of each body at every frame, in components `(rx, ry, rz)`.
