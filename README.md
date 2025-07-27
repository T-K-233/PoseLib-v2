# PoseLib-v2

**Note** This library is going to be deprecated soon. Please see [here](https://github.com/T-K-233/MikuMotionTools) for replacement.

Library for converting and manipulating robot armature motions.


## Installation

First, install [uv](https://docs.astral.sh/uv/).

- for Ubuntu / MacOS
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

- For Windows
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

Then, create a virtual environment and activate.

```bash
uv venv --python=3.10
source ./.venv/bin/activate
```

Finally, install the library.

```bash
uv pip install ./source/poselib-v2
```


## Visualization

We provide a simple script to visualize the converted motion.

```bash
uv run ./scripts/view_motion.py --file ./you_motion_data.npz
```


## Motion Format

This library uses the motion file format defined in IsaacLab [MotionLoader](https://github.com/isaac-sim/IsaacLab/blob/main/source/isaaclab_tasks/isaaclab_tasks/direct/humanoid_amp/motions/motion_loader.py#L12).

Each motion file is a numpy dictionary with the following fields. Here, we assume the robot has `D` number of joints and `B` number of linkages, and the motion file has `F` frames.

- `fps`: an int64 number representing the frame rate of the motion data.
- `dof_names`: a list of length `D` containing the names of each joint.
- `body_names`: a list of length `B` containing the names of each link.
- `dof_positions`: a numpy array of shape `(F, D)` containing the rotational positions of the joints in `rad`.
- `dof_velocities`: a numpy array of shape `(F, D)` containing the rotational (angular) velocities of the joints in `rad/s`.
- `body_positions`: a numpy array of shape `(F, B, 3)` containing the locations of each body in **world frame**, in `m`.
- `body_rotations`: a numpy array of shape `(F, B, 4)` containing the rotations of each body in **world frame**, in quaternion `(qw, qx, qy, qz)`.
- `body_linear_velocities`: a numpy array of shape `(F, B, 3)` containing the linear velocities of each body in **world frame**, in `m/s`.
- `body_angular_velocities`: a numpy array of shape `(F, B, 3)` containing the rotational (angular) velocities of each body in **world frame**, in `rad/s`.

The converted motion file is targeted for one particular robot skeleton structure. 

<!-- To ensure best performance, also make sure that the frame rate matches the training environment policy update rate to avoid interpolations. -->


## Working with MMD

To import and convert MMD motions in Blender, the [MMD Tools](https://extensions.blender.org/add-ons/mmd-tools/) plugin needs to be installed.

