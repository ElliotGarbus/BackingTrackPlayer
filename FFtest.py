#  ffmpeg -y -i source.mp3 -filter:a atempo=1.25 output_125.mp3

import subprocess

ffmpeg_cmd = 'ffmpeg -y -i source.mp3 -filter:a atempo=0.75 output_075.mp3'.split()
try:
    result = subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
except FileNotFoundError as fnfe:
    print(fnfe)
except subprocess.CalledProcessError as cpe:
    print(cpe)
