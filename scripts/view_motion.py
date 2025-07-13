import argparse

import matplotlib
from poselib_v2.motion_viewer import MotionViewer


parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str, required=True, help="Motion file")
parser.add_argument(
    "--render-scene",
    action="store_true",
    default=True,
    help=(
        "Whether the scene (space occupied by the skeleton during movement) is rendered instead of a reduced view"
        " of the skeleton."
    ),
)
parser.add_argument("--matplotlib-backend", type=str, default="TkAgg", help="Matplotlib interactive backend")
parser.add_argument("--show-velocity", action="store_true", default=False, help="Show velocity vectors")
# parser.add_argument("--show-frames", type=str, default="", help="Show frames")

args, _ = parser.parse_known_args()

# https://matplotlib.org/stable/users/explain/figure/backends.html#interactive-backends
matplotlib.use(args.matplotlib_backend)

frame_list = ["pelvis", "left_rubber_hand", "right_rubber_hand", "left_ankle_roll_link", "right_ankle_roll_link"]

viewer = MotionViewer(
    args.file,
    render_scene=args.render_scene,
    show_velocity=args.show_velocity,
    show_frames=frame_list,
)
viewer.show()
