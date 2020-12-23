#  ffmpeg -y -i source.mp3 -filter:a atempo=1.25 output_125.mp3

import subprocess
import time

speeds = ['1.5', '1.25', '.75', '.5']

try:
    t0 = time.perf_counter()
    sps = []
    for speed in speeds:
        cmd = f"ffmpeg -y -i source.mp3 -filter:a atempo={speed} output_{speed.replace('.', '')}.mp3"
        sps.append(subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

    while any([sp.poll() is None for sp in sps]):
        for i, sp in enumerate(sps):
            print(f'waiting... returncode: {i} {sp.returncode}')
            time.sleep(.1)

    print(f'execution time: {time.perf_counter() - t0:.1f} seconds')

except FileNotFoundError as fnfe:
    print(fnfe)
except Exception as e:
    print(e)
