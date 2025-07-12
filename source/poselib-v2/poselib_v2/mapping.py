

# only thing need to be cautious is that the first entry must be the root.


class UnitreeG1Mapping:
    actorcore = {
        "pelvis"                    : ("CC_Base_Pelvis",        lambda b: b.head),
        "left_shoulder_roll_link"   : ("CC_Base_L_Clavicle",    lambda b: b.tail),
        "left_elbow_link"           : ("CC_Base_L_Forearm",     lambda b: b.head),
        "left_wrist_pitch_link"     : ("CC_Base_L_Hand",        lambda b: b.head),
        "left_rubber_hand"          : ("CC_Base_L_Hand",        lambda b: b.tail),
        "right_shoulder_roll_link"  : ("CC_Base_R_Clavicle",    lambda b: b.tail),
        "right_elbow_link"          : ("CC_Base_R_Forearm",     lambda b: b.head),
        "right_wrist_pitch_link"    : ("CC_Base_R_Hand",        lambda b: b.head),
        "right_rubber_hand"         : ("CC_Base_R_Hand",        lambda b: b.tail),
        "left_hip_roll_link"        : ("CC_Base_L_Thigh",       lambda b: b.head),
        "left_knee_link"            : ("CC_Base_L_Calf",        lambda b: b.head),
        "left_ankle_pitch_link"     : ("CC_Base_L_Foot",        lambda b: b.head),
        "left_ankle_roll_link"      : ("CC_Base_L_Foot",        lambda b: b.tail),
        "right_hip_roll_link"       : ("CC_Base_R_Thigh",       lambda b: b.head),
        "right_knee_link"           : ("CC_Base_R_Calf",        lambda b: b.head),
        "right_ankle_pitch_link"    : ("CC_Base_R_Foot",        lambda b: b.head),
        "right_ankle_roll_link"     : ("CC_Base_R_Foot",        lambda b: b.tail),
        "torso_link"                : ("CC_Base_Spine02",       lambda b: b.head),
        "head_link"                 : ("CC_Base_Head",          lambda b: b.tail),
    }
    meshcapade = {
        "pelvis"                    : ("pelvis",        lambda b: b.head),
        "left_shoulder_roll_link"   : ("upperarm_l",    lambda b: b.head),
        "left_elbow_link"           : ("lowerarm_l",    lambda b: b.head),
        "left_wrist_pitch_link"     : ("hand_l",        lambda b: b.head),
        "left_rubber_hand"          : ("hand_l",        lambda b: b.tail),
        "right_shoulder_roll_link"  : ("upperarm_r",    lambda b: b.head),
        "right_elbow_link"          : ("lowerarm_r",    lambda b: b.head),
        "right_wrist_pitch_link"    : ("hand_r",        lambda b: b.head),
        "right_rubber_hand"         : ("hand_r",        lambda b: b.tail),
        "torso_link"                : ("torso",         lambda b: b.head),
        "head_link"                 : ("head",          lambda b: b.head),
        "left_hip_roll_link"        : ("thigh_l",       lambda b: b.head),
        "left_knee_link"            : ("calf_l",        lambda b: b.head),
        "left_ankle_pitch_link"     : ("foot_l",        lambda b: b.head),
        "left_ankle_roll_link"      : ("ball_l",        lambda b: b.head),
        "right_hip_roll_link"       : ("thigh_r",       lambda b: b.head),
        "right_knee_link"           : ("calf_r",        lambda b: b.head),
        "right_ankle_pitch_link"    : ("foot_r",        lambda b: b.head),
        "right_ankle_roll_link"     : ("ball_r",        lambda b: b.head),
    }


class AirDraftMapping:
    mixamo = {
        "pelvis"            : ("mixamorig:Hips",            lambda b: b.head),
        "left_shoulder"     : ("mixamorig:LeftArm",         lambda b: b.head),
        "left_elbow"        : ("mixamorig:LeftForeArm",     lambda b: b.head),
        "left_hand"         : ("mixamorig:LeftHand",        lambda b: b.head),
        "right_shoulder"    : ("mixamorig:RightArm",        lambda b: b.head),
        "right_elbow"       : ("mixamorig:RightForeArm",    lambda b: b.head),
        "right_hand"        : ("mixamorig:RightHand",       lambda b: b.head),
        "left_hip"          : ("mixamorig:LeftUpLeg",       lambda b: b.head),
        "left_knee"         : ("mixamorig:LeftLeg",         lambda b: b.head),
        "left_foot"         : ("mixamorig:LeftToeBase",     lambda b: b.head),
        "right_hip"         : ("mixamorig:RightUpLeg",      lambda b: b.head),
        "right_knee"        : ("mixamorig:RightLeg",        lambda b: b.head),
        "right_foot"        : ("mixamorig:RightToeBase",    lambda b: b.head),
        "chest"             : ("mixamorig:Spine1",          lambda b: b.head),
        "head"              : ("mixamorig:Head",            lambda b: b.head),
    }

    mmd_yyb = {
        "pelvis"            : ("腰",        lambda b: b.head),
        "left_shoulder"     : ("腕.L",      lambda b: b.head),
        "left_elbow"        : ("腕.L",      lambda b: b.tail),
        "left_hand"         : ("ひじ.L",    lambda b: b.tail),
        "right_shoulder"    : ("腕.R",      lambda b: b.head),
        "right_elbow"       : ("腕.R",      lambda b: b.tail),
        "right_hand"        : ("ひじ.R",    lambda b: b.tail),
        "left_hip"          : ("足.L",      lambda b: b.head),
        "left_knee"         : ("足.L",      lambda b: b.tail),
        "left_foot"         : ("ひざ.L",    lambda b: b.tail),
        "right_hip"         : ("足.R",      lambda b: b.head),
        "right_knee"        : ("足.R",      lambda b: b.tail),
        "right_foot"        : ("ひざ.R",    lambda b: b.tail),
        "chest"             : ("上半身",    lambda b: b.head),
        "head"              : ("頭",        lambda b: b.head),
    }
