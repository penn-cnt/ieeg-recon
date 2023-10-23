import os
import glob
import pydeface
import argparse

# Argument Parser
parser = argparse.ArgumentParser()

parser.add_argument("-s", "--subject", required=True, help="Subject ID")
parser.add_argument("-d", "--source_directory", required=True, help="Source Directory")

args = parser.parse_args()

subject = args.subject
source_dir = args.source_directory

mod2 = os.path.join(source_dir, subject, 'derivatives', 'ieeg_recon', 'module2')

def deface_image(path, img):
    # run defacing
    pydeface_command = 'pydeface {} --outfile {} --force'.format(os.path.join(path, img), os.path.join(path, img))
    os.system(pydeface_command)

# Search for images in the mod2 folder and its subfolders
for root, dirs, files in os.walk(mod2):
    for file in files:
        if ('T1w' in file) and file.endswith(('.nii', '.nii.gz')) and ('spheres' not in file):
            deface_image(root, file)
