from pydub import AudioSegment

from concurrent.futures import ProcessPoolExecutor, wait, ALL_COMPLETED

from pathlib import Path

import argparse
import json


def process_batch(wav_files):
    wav2dur = {}
    for index, wav_file in enumerate(wav_files):
        print(f"{index} / {len(wav_files)} | doing {wav_file}...")
        sound = AudioSegment.from_wav(wav_file)
        duration = sound.duration_seconds
        wav2dur[wav_file] = duration
    return wav2dur

def main(args):
    args.data_dir = Path(args.data_dir)
    csv_file =  args.data_dir / 'metadata.csv'
    wav_files = [line.strip().split('|')[0] for line in open(csv_file).readlines()]
    
    k, r = divmod(len(wav_files), 32)
    batches = [wav_files[i * k + min(i, r):(i + 1) * k + min(i + 1, r)] for i in range(32)]


    wav2dur = {}
    with ProcessPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(process_batch, batch) for index, batch in enumerate(batches) if batch]
        wait(futures, return_when=ALL_COMPLETED)
        
        for future in futures:
            result = future.result()
            wav2dur.update(result)


    with open(args.data_dir / 'raw_dur.json', 'w') as f:
        f.write(json.dumps(wav2dur, ensure_ascii=False, indent=2))            


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default=None, type=str)
    args = parser.parse_args()
    main(args)