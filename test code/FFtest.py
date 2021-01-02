#  ffmpeg -y -i source.mp3 -filter:a atempo=1.25 output_125.mp3

import subprocess
import time
from multiprocessing import Pool

speeds = ['1.5', '1.25', '.75', '.5']


def time_stretch(speed):
    subprocess.run(f"ffmpeg -y -i source.mp3 -filter:a atempo={speed} output_{speed.replace('.', '')}.mp3",
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    try:
        t0 = time.perf_counter()
        with Pool(4) as p:
            p.map(time_stretch, speeds)
            # subprocess.run(ff_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        print(f'execution time: {time.perf_counter() - t0:.1f} seconds')
    except FileNotFoundError as fnfe:
        print(fnfe)
    except subprocess.CalledProcessError as cpe:
        print(cpe)
