# Alakazam's_Trickery

import subprocess

command = "start python -m bokeh serve --show dice_visualisation.py"
process = subprocess.Popen(command, shell=True, start_new_session=True).wait()
