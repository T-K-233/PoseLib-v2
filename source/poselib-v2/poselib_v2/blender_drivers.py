from typing import Callable

import numpy as np
import bpy
import bpy_types
from mathutils import Vector


C = bpy.context
D = bpy.data
O = bpy.ops

"""
Generic quick references:

# getting an armature
armature = D.objects.get("Armature")

# get pose bones
bones = armature.pose.bones

# get bone location
bones.get("bone_name").location

# get bone rotation
bones.get("bone_name").rotation_quaternion

# get bone rotation matrix
bones.get("bone_name").matrix

# get bone scale
bones.get("bone_name").scale

# get edit bones
armature.data.bones
"""


def quat_mul(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    """Multiply two quaternions together.

    Args:
        q1: The first quaternion in (w, x, y, z). Shape is (..., 4).
        q2: The second quaternion in (w, x, y, z). Shape is (..., 4).

    Returns:
        The product of the two quaternions in (w, x, y, z). Shape is (..., 4).

    Raises:
        ValueError: Input shapes of ``q1`` and ``q2`` are not matching.
    """
    # check input is correct
    if q1.shape != q2.shape:
        msg = f"Expected input quaternion shape mismatch: {q1.shape} != {q2.shape}."
        raise ValueError(msg)
    # reshape to (N, 4) for multiplication
    shape = q1.shape
    q1 = q1.reshape(-1, 4)
    q2 = q2.reshape(-1, 4)
    # extract components from quaternions
    w1, x1, y1, z1 = q1[:, 0], q1[:, 1], q1[:, 2], q1[:, 3]
    w2, x2, y2, z2 = q2[:, 0], q2[:, 1], q2[:, 2], q2[:, 3]
    # perform multiplication
    ww = (z1 + x1) * (x2 + y2)
    yy = (w1 - y1) * (w2 + z2)
    zz = (w1 + y1) * (w2 - z2)
    xx = ww + yy + zz
    qq = 0.5 * (xx + (z1 - x1) * (x2 - y2))
    w = qq - ww + (z1 - y1) * (y2 - z2)
    x = qq - xx + (x1 + w1) * (x2 + w2)
    y = qq - yy + (w1 - x1) * (y2 + z2)
    z = qq - zz + (z1 + y1) * (w2 - x2)

    return np.stack([w, x, y, z], axis=-1).reshape(shape)


def cleanup_usd_axis_display(display_size: float = 0.01) -> None:
    """
    This function shrinks the axis display of the imported IsaacLab USD object
    to make this looks cleaner.

    Args:
        display_size: the size of the axes
    """
    for object in D.objects:
        if "visuals" in object.name or "collisions" in object.name:
            object.empty_display_size = display_size


def set_scene_fps(fps: int) -> None:
    """
    Set the scene FPS.
    """
    C.scene.render.fps = fps
    C.scene.render.fps_base = 1.0


def set_scene_animation_range(start: int, end: int) -> None:
    """
    Set the animation range for the current scene.

    Args:
        start: The start frame.
        end: The end frame.
    """
    C.scene.frame_start = start
    C.scene.frame_end = end


def set_bones_to_1d_rotation(armature: bpy_types.Object) -> None:
    """
    Set the bones to 1D rotation mode, and allow only Y-axis rotation (along the bone axis).
    Use this function to convert arbitrary armature to "realistic" robot armature with revolute joints.

    Args:
        armature: The armature object.
    """

    for bone in armature.pose.bones:
        print(f"found bone {bone.name}")
        # set to XYZ rotation mode
        bone.rotation_mode = "XYZ"

        # allow only Y-axis rotation
        bone.lock_rotation[0] = False
        bone.lock_rotation[1] = False
        bone.lock_rotation[2] = False

        # allow only Y-axis rotation in IK
        bone.lock_ik_x = False
        bone.lock_ik_y = False
        bone.lock_ik_z = False


def build_motion_data(
    armature: bpy_types.Object,
    mapping: dict[str, tuple[str, Callable]],
    scaling_ratio: float = 1.0,
) -> dict:
    """
    Build motion data from the source armature.

    Args:
        armature: The source armature object.
        mapping: The mapping from bone names to their positions.
        scaling_ratio: The scaling ratio of the armature.

    Returns:
        A dictionary containing the motion data.
    """
    fps_exact = C.scene.render.fps / C.scene.render.fps_base
    start_frame = C.scene.frame_start
    end_frame = C.scene.frame_end

    assert end_frame >= start_frame, f"Frame range is invalid: {start_frame} to {end_frame}"

    link_names = list(mapping.keys())

    n_frames = end_frame - start_frame + 1
    n_dof = 0  # the number of skeleton DOFs
    n_body = len(link_names)

    # === create motion data buffers ===
    # frame rate
    fps = np.array([fps_exact], dtype=np.int64)  # this needs to be int64
    # joint names
    dof_names = np.array([])
    # body names
    body_names = np.array(link_names)
    # joint positions
    dof_positions = np.zeros((n_frames, n_dof), dtype=np.float32)
    # joint velocities
    dof_velocities = np.zeros((n_frames, n_dof), dtype=np.float32)
    # body world positions
    body_positions = np.zeros((n_frames, n_body, 3), dtype=np.float32)
    # body world rotations
    body_rotations = np.zeros((n_frames, n_body, 4), dtype=np.float32)
    # body world linear velocities
    body_linear_velocities = np.zeros((n_frames, n_body, 3), dtype=np.float32)
    # body world angular velocities
    body_angular_velocities = np.zeros((n_frames, n_body, 3), dtype=np.float32)

    # used to calculate angular velocities
    body_rotations_euler = np.zeros((n_frames, n_body, 3), dtype=np.float32)

    # ensure correct default quaternion representation
    body_rotations[:, :, 0] = 1.0

    # === extract motion data ===
    for frame in range(n_frames):
        # navigate to the corresponding frame
        bpy.context.scene.frame_set(start_frame + frame)
        bpy.context.view_layer.update()

        # force UI update to update bone pose matrix
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

        # read bone positions
        for idx, name in enumerate(body_names):
            entry = mapping.get(name)
            if not entry:
                print(f"WARNING: cannot find link mapping for {name}")
                continue
        
            source_bone_name, mapping_function = entry

            source_bone = armature.pose.bones.get(source_bone_name)
            if not source_bone:
                print(f"WARNING: cannot find source bone {source_bone_name}")
                continue

            body_positions[frame, idx, :] = mapping_function(source_bone)

            matrix = source_bone.matrix
            body_rotations[frame, idx, :] = matrix.to_quaternion()
            body_rotations_euler[frame, idx, :] = matrix.to_euler()

        print(f"Processing: #{frame}/{n_frames} ({frame / n_frames * 100:.2f}%)")

    # === post-process motion data ===
    # cancel first frame global offset
    offset_x = np.mean(body_positions[0, :, 0])
    offset_y = np.mean(body_positions[0, :, 1])
    body_positions[:, :, 0] -= offset_x
    body_positions[:, :, 1] -= offset_y

    # in Blender, scaling the armature does not scale the retreived bone position, so we need to
    # manually apply the scaling to the sampled data here.
    body_positions[:] *= scaling_ratio

    # calculate velocities
    body_linear_velocities[1:] = np.diff(body_positions, axis=0) / (1 / fps_exact)

    # calculate angular velocities
    # handle euler angle discontinuity
    # TODO: this is not quite correct, we need to use quaternions to calculate angular velocities
    body_rotations_euler = np.unwrap(body_rotations_euler, axis=0)
    body_angular_velocities[1:] = np.diff(body_rotations_euler, axis=0) / (1 / fps_exact)

    # handle euler angle wrapping
    body_angular_velocities = np.unwrap(body_angular_velocities, axis=0)

    print(f"Done generating {n_frames} frames ({n_frames / fps_exact:.2f} seconds)")

    return {
        "fps": fps,
        "dof_names": dof_names,
        "body_names": body_names,
        "dof_positions": dof_positions,
        "dof_velocities": dof_velocities,
        "body_positions": body_positions,
        "body_rotations": body_rotations,
        "body_linear_velocities": body_linear_velocities,
        "body_angular_velocities": body_angular_velocities
    }


def export_motion_data(output_file: str, motion_data: dict) -> None:
    """
    Export motion data to a Numpy npz file.

    Args:
        output_file: The path to the output file.
        motion_data: The motion data to export.
    """
    np.savez(
        output_file,
        fps=motion_data["fps"],
        dof_names=motion_data["dof_names"],
        body_names=motion_data["body_names"],
        dof_positions=motion_data["dof_positions"],
        dof_velocities=motion_data["dof_velocities"],
        body_positions=motion_data["body_positions"],
        body_rotations=motion_data["body_rotations"],
        body_linear_velocities=motion_data["body_linear_velocities"],
        body_angular_velocities=motion_data["body_angular_velocities"]
    )

    print(f"Results saved to {output_file}")


def construct_skeleton_tree():
    skeleton_tree_usd = {
        "node_names": [  # joint names
            "pelvis",                     # 0
            "waist_yaw",                  # 1
            "waist_roll",                 # 2
            "waist_pitch",                # 3
            "neck_yaw",                   # 4
            "neck_roll",                  # 5
            "neck_pitch",                 # 6
            "arm_left_shoulder_pitch",    # 7
            "arm_left_shoulder_roll",     # 8
            "arm_left_shoulder_yaw",      # 9
            "arm_left_elbow_pitch",       # 10
            "arm_left_wrist_yaw",         # 11
            "arm_left_wrist_roll",        # 13
            "arm_left_wrist_pitch",       # 12
            "arm_right_shoulder_pitch",   # 14
            "arm_right_shoulder_roll",    # 15
            "arm_right_shoulder_yaw",     # 16
            "arm_right_elbow_pitch",      # 17
            "arm_right_wrist_yaw",        # 18
            "arm_right_wrist_roll",       # 20
            "arm_right_wrist_pitch",      # 19
            "leg_left_hip_pitch",         # 21
            "leg_left_hip_roll",          # 22
            "leg_left_hip_yaw",           # 23
            "leg_left_knee_pitch",        # 24
            "leg_left_ankle_yaw",         # 25
            "leg_left_ankle_pitch",       # 26
            "leg_left_ankle_roll",        # 27
            "leg_right_hip_pitch",        # 28
            "leg_right_hip_roll",         # 29
            "leg_right_hip_yaw",          # 30
            "leg_right_knee_pitch",       # 31
            "leg_right_ankle_yaw",        # 32
            "leg_right_ankle_pitch",      # 33
            "leg_right_ankle_roll",       # 34
        ],
        "link_names": [
            "pelvis",                     # 0
            "chest_yaw",                  # 1
            "chest_roll",                 # 2
            "chest_pitch",                # 3
            "head_yaw",                   # 4
            "head_roll",                  # 5
            "head_pitch",                 # 6
            "arm_left_upper_pitch",       # 7
            "arm_left_upper_roll",        # 8
            "arm_left_upper_yaw",         # 9
            "arm_left_forearm_pitch",     # 10
            "arm_left_hand_yaw",          # 11
            "arm_left_hand_roll",         # 12
            "arm_left_hand_pitch",        # 13
            "arm_right_upper_pitch",      # 14
            "arm_right_upper_roll",       # 15
            "arm_right_upper_yaw",        # 16
            "arm_right_forearm_pitch",    # 17
            "arm_right_hand_yaw",         # 18
            "arm_right_hand_roll",        # 19
            "arm_right_hand_pitch",       # 20
            "leg_left_thigh_pitch",       # 21
            "leg_left_thigh_roll",        # 22
            "leg_left_thigh_yaw",         # 23
            "leg_left_calf_pitch",        # 24
            "leg_left_foot_yaw",          # 25
            "leg_left_foot_pitch",        # 26
            "leg_left_foot_roll",         # 27
            "leg_right_thigh_pitch",      # 28
            "leg_right_thigh_roll",       # 29
            "leg_right_thigh_yaw",        # 30
            "leg_right_calf_pitch",       # 31
            "leg_right_foot_yaw",         # 32
            "leg_right_foot_pitch",       # 33
            "leg_right_foot_roll",        # 34
        ],
        "parent_indices": {
            "arr": np.array([
                -1,
                0, 1, 2, 3, 4, 5,
                3, 7, 8, 9, 10, 11, 12,
                3, 14, 15, 16, 17, 18, 19,
                0, 21, 22, 23, 24, 25, 26,
                0, 28, 29, 30, 31, 32, 33
            ]),
            "context": {"dtype": "int64"}
            },
        "global_translations": [],
        "bone_orientations": [
            [ .0,  .1,  .0],
            [ .0,  .0,  .1],
            [ .1,  .0,  .0],
            [ .0,  .1,  .0],
            [ .0,  .0,  .1],
            [ .1,  .0,  .0],
            [ .0,  .1,  .0],

            [ .0,  .1,  .0],
            [ .1,  .0,  .0],
            [ .0, -.1*np.cos(np.deg2rad(60)),  .1*np.sin(np.deg2rad(60))],
            [ .0,  .1*np.sin(np.deg2rad(60)),  .1*np.cos(np.deg2rad(60))],
            [ .0, -.1*np.cos(np.deg2rad(60)),  .1*np.sin(np.deg2rad(60))],
            [ .0,  .1*np.sin(np.deg2rad(60)),  .1*np.cos(np.deg2rad(60))],
            [ .1,  .0,  .0],
            [ .0,  .1,  .0],
            [ .1,  .0,  .0],
            [ .0,  .1*np.cos(np.deg2rad(60)),  .1*np.sin(np.deg2rad(60))],
            [ .0,  .1*np.sin(np.deg2rad(60)), -.1*np.cos(np.deg2rad(60))],
            [ .0,  .1*np.cos(np.deg2rad(60)),  .1*np.sin(np.deg2rad(60))],
            [ .0,  .1*np.sin(np.deg2rad(60)), -.1*np.cos(np.deg2rad(60))],
            [ .1,  .0,  .0],

            [ .0,  .1,  .0],
            [ .1,  .0,  .0],
            [ .0,  .0,  .1],
            [ .0,  .1,  .0],
            [ .0,  .0,  .1],
            [ .0,  .1,  .0],
            [ .1,  .0,  .0],

            [ .0,  .1,  .0],
            [ .1,  .0,  .0],
            [ .0,  .0,  .1],
            [ .0,  .1,  .0],
            [ .0,  .0,  .1],
            [ .0,  .1,  .0],
            [ .1,  .0,  .0],
        ],
    }

    for link_name in skeleton_tree_usd["link_names"]:
        skeleton_tree_usd["global_translations"].append(np.array(D.objects.get(link_name).location))

    # skeleton_tree_usd["global_translations"] += np.array([0, 0, 0.6])

    return skeleton_tree_usd


class SkeletonTree:
    skeleton_tree_a_pose = {
        "node_names": [
            "pelvis",               # 0
            "chest",                # 1
            "head",                 # 2
            "arm_left_upper",       # 3
            "arm_left_lower",       # 4
            "arm_left_hand",        # 5
            "arm_right_upper",      # 6
            "arm_right_lower",      # 7
            "arm_right_hand",       # 8
            "leg_left_upper",       # 9
            "leg_left_lower",       # 10
            "leg_left_foot",        # 11
            "leg_right_upper",      # 12
            "leg_right_lower",      # 13
            "leg_right_foot",       # 14
        ],
        "parent_indices": {
            "arr": np.array([-1, 0, 1, 1, 3, 4, 1, 6, 7, 0, 9, 10, 0, 12, 13]),
            "context": {"dtype": "int64"}
            },
        "local_translations": [
            [  .000,   .000,  0.600],
            [  .000,   .000,  0.100],
            [  .000,   .000,  0.300],
            [-0.018,  0.066,  0.218],
            [  .000,  0.150*np.cos(np.deg2rad(60)), -0.150*np.sin(np.deg2rad(60))],
            [  .000,  0.150*np.cos(np.deg2rad(60)), -0.150*np.sin(np.deg2rad(60))],
            [-0.018, -0.066,  0.218],
            [  .000, -0.150*np.cos(np.deg2rad(60)), -0.150*np.sin(np.deg2rad(60))],
            [  .000, -0.150*np.cos(np.deg2rad(60)), -0.150*np.sin(np.deg2rad(60))],
            [  .000,  0.084,   .000],
            [  .000, -0.030, -0.255],
            [-0.023,   .000, -0.293],
            [  .000, -0.084,   .000],
            [  .000,  0.030, -0.255],
            [-0.023,   .000, -0.293],
        ],
        "bone_orientations": [
            [  .000,   .000,  0.100],
            [  .000,   .000,  0.218],
            [  .000,   .000,  0.100],
            [  .000,  0.150*np.cos(np.deg2rad(60)), -0.150*np.sin(np.deg2rad(60))],
            [  .000,  0.150*np.cos(np.deg2rad(60)), -0.150*np.sin(np.deg2rad(60))],
            [  .000,  0.100*np.cos(np.deg2rad(60)), -0.100*np.sin(np.deg2rad(60))],
            [  .000, -0.150*np.cos(np.deg2rad(60)), -0.150*np.sin(np.deg2rad(60))],
            [  .000, -0.150*np.cos(np.deg2rad(60)), -0.150*np.sin(np.deg2rad(60))],
            [  .000, -0.100*np.cos(np.deg2rad(60)), -0.100*np.sin(np.deg2rad(60))],
            [  .000,   .000, -0.250],
            [-0.023,   .000, -0.290],
            [ 0.066,   .000, -0.056],
            [  .000,   .000, -0.250],
            [-0.023,   .000, -0.290],
            [ 0.066,   .000, -0.056],
        ],
    }

    skeleton_tree_t_pose = {
        "node_names": [
            "pelvis",               # 0
            "chest",                # 1
            "head",                 # 2
            "arm_left_upper",       # 3
            "arm_left_lower",       # 4
            "arm_left_hand",        # 5
            "arm_right_upper",      # 6
            "arm_right_lower",      # 7
            "arm_right_hand",       # 8
            "leg_left_upper",       # 9
            "leg_left_lower",       # 10
            "leg_left_foot",        # 11
            "leg_right_upper",      # 12
            "leg_right_lower",      # 13
            "leg_right_foot",       # 14
        ],
        "parent_indices": {
            "arr": np.array([-1, 0, 1, 1, 3, 4, 1, 6, 7, 0, 9, 10, 0, 12, 13]),
            "context": {"dtype": "int64"}
            },
        "local_translations": [
            [  .000,   .000,  0.600],
            [  .000,   .000,  0.100],
            [  .000,   .000,  0.300],
            [-0.018,  0.066,  0.218],
            [  .000,  0.150,   .000],
            [  .000,  0.150,   .000],
            [-0.018, -0.066,  0.218],
            [  .000, -0.150,   .000],
            [  .000, -0.150,   .000],
            [  .000,  0.084,   .000],
            [  .000, -0.030, -0.255],
            [-0.023,   .000, -0.293],
            [  .000, -0.084,   .000],
            [  .000,  0.030, -0.255],
            [-0.023,   .000, -0.293],
        ],
        "bone_orientations": [
            [  .000,   .000,  0.100],
            [  .000,   .000,  0.218],
            [  .000,   .000,  0.100],
            [  .000,  0.150,   .000],
            [  .000,  0.150,   .000],
            [  .000,  0.100,   .000],
            [  .000, -0.150,   .000],
            [  .000, -0.150,   .000],
            [  .000, -0.100,   .000],
            [  .000,   .000, -0.250],
            [-0.023,   .000, -0.290],
            [ 0.066,   .000, -0.056],
            [  .000,   .000, -0.250],
            [-0.023,   .000, -0.290],
            [ 0.066,   .000, -0.056],
        ],
    }


def build_armature(skeleton_tree: dict, armature_name="Armature"):
    armature = D.objects.get(armature_name)

    # delete the existing armature, if any
    if armature:
        O.object.mode_set(mode="OBJECT")
        armature.select_set(True)
        O.object.delete()


    O.object.armature_add(enter_editmode=False, align="WORLD", scale=(1, 1, 1))
    armature = C.active_object
    armature.name = armature_name

    # switch to edit mode
    O.object.mode_set(mode="EDIT")
    edit_bones = armature.data.edit_bones

    # reconfigure root bone
    root = edit_bones[0]
    root.name = "root"
    root.tail = Vector([0.5, 0, 0])


    for name in skeleton_tree["node_names"]:
        edit_bones.new(name)

    for i, name in enumerate(skeleton_tree["node_names"]):
        parent_idx = skeleton_tree["parent_indices"]["arr"][i]

        bone = edit_bones.get(name)

        if skeleton_tree.get("local_translations"):
            # use local translation
            if parent_idx == -1:
                bone.head = Vector(skeleton_tree["local_translations"][i])
                bone.parent = root
            else:
                parent_bone_name = skeleton_tree["node_names"][parent_idx]
                parent_bone = edit_bones.get(parent_bone_name)

                bone.head = parent_bone.head + Vector(skeleton_tree["local_translations"][i])
                bone.parent = parent_bone

        else:
            # use global translation
            if parent_idx == -1:
                bone.parent = root
            else:
                parent_bone_name = skeleton_tree["node_names"][parent_idx]
                parent_bone = edit_bones.get(parent_bone_name)

                bone.parent = parent_bone

            bone.head = Vector(skeleton_tree["global_translations"][i])

        bone.tail = bone.head + Vector(skeleton_tree["bone_orientations"][i])

    O.object.mode_set(mode="OBJECT")

    bones = D.objects.get("Armature").pose.bones
    for bone in bones:
        bone.rotation_mode = "XYZ"

def bind_to_armature(skeleton_tree: dict):

    armature = D.objects.get("Armature")

    for idx, link_name in enumerate(skeleton_tree["link_names"]):
        frame = D.objects.get(link_name)
        bone_name = skeleton_tree["node_names"][idx]

        print(f"binding {link_name} to {bone_name}")

        # the use of matrix world is to maintain the original transform
        # i.e. the equivalent of "Keep Transform" GUI option

        # save original world matrix
        matrix_world = frame.matrix_world.copy()

        frame.parent = armature
        frame.parent_bone = bone_name
        frame.parent_type = "BONE"

        # restore world matrix to maintain global transform
        frame.matrix_world = matrix_world.copy()


def load_replay(skeleton_tree: dict, armature: bpy_types.Object, data_path: str):
    # TODO: refactor the replay motion format to use the same format as the motion data
    data = np.load(data_path)

    fps = data["fps"]
    joint_order = data["joint_order"].tolist()
    root_positions = data["root_positions"]
    root_quaternions = data["root_quaternions"]
    joint_positions = data["joint_positions"]


    print(joint_positions.shape)

    n_frames = joint_positions.shape[0]
    n_dof = joint_positions.shape[-1]

    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = n_frames

    for frame in range(n_frames):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()

        root = armature.pose.bones.get("pelvis")
        root.location = root_positions[frame]
        # root.location[2] -= 0.6
        root.keyframe_insert(data_path="location", frame=frame)

        root.rotation_mode = "QUATERNION"
        root.rotation_quaternion = root_quaternions[frame]
        root.keyframe_insert(data_path="rotation_quaternion", frame=frame)

        for joint_idx, joint_name in enumerate(joint_order):
            bone_name = joint_name.replace("_joint", "")
            bone = armature.pose.bones.get(bone_name)
            # ensure using Euler angles
            bone.rotation_mode = "XYZ"
            bone.rotation_euler[1] = joint_positions[frame, joint_idx]

            # insert rotation_euler keyframe, for index 1 (Y-axis)
            bone.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)

        print(f"Processing: #{frame}/{n_frames} ({frame / n_frames * 100:.2f}%)")
