import os
import sys
import argparse

from pathlib import Path
from pydub import AudioSegment

from concurrent.futures import ProcessPoolExecutor, wait, ALL_COMPLETED

import logging

LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d:%(funcName)s] %(message)s"
LOGGING_LEVEL = logging.INFO
logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)


def batch_process(audio_files: list, exp_dir: Path, data_dir: str, sr: int = 24000):
    for index, audio_file in enumerate(audio_files):
        logging.info(f'{index}/{len(audio_files)} | {audio_file}')
        wav_file = exp_dir / f'{audio_file.stem}.wav'
        sound = AudioSegment.from_file(audio_file)
        sound.export(wav_file, format="wav", parameters=["-ar", f"{sr}", "-ac", "1", "-loglevel", "quiet"])
            

def main(args):
        
    exp_dir = Path(args.exp_dir)
    exp_dir.mkdir(exist_ok=True, parents=True)
    
    audio_files = list(Path(args.raw_dir).glob("*.mp3"))
    
    each_batch_num = len(audio_files) // 64 + 1
    batches = [audio_files[each_batch_num*i:each_batch_num*(i+1)] for i in range(64)]
    with ProcessPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(batch_process, batch, exp_dir, args.sr) for batch in batches]
        wait(futures, return_when=ALL_COMPLETED)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=str, default="", required=True)
    parser.add_argument("--exp-dir", type=str, default="", required=True)
    parser.add_argument("--sr", type=int, default=24000)
    args = parser.parse_args()
    main(args)
    
