import argparse

import matplotlib
from poselib_v2.motion_viewer import MotionViewer


parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str, required=True, help="Motion file")
parser.add_argument(
    "--render-scene",
    action="store_true",
    default=False,
    help=(
        "Whether the scene (space occupied by the skeleton during movement) is rendered instead of a reduced view"
        " of the skeleton."
    ),
)
parser.add_argument("--matplotlib-backend", type=str, default="TkAgg", help="Matplotlib interactive backend")
args, _ = parser.parse_known_args()

# https://matplotlib.org/stable/users/explain/figure/backends.html#interactive-backends
matplotlib.use(args.matplotlib_backend)

viewer = MotionViewer(args.file, render_scene=args.render_scene)
viewer.show()
