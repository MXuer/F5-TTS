import os
import sys
import random
import argparse

from tqdm import tqdm
from pathlib import Path
from pydub import AudioSegment
from collections import defaultdict

random.seed(2005)

def get_commonvoice_metainfo(cv_dir: Path, setname: str = 'validated'):
    tsv_file = cv_dir / f"{setname}.tsv"
    data_infos = []
    for line in tqdm(open(tsv_file, "r").readlines()[1:], desc=f'reading {tsv_file}'):
        client_id, path, _, text, *_ = line.strip().split("\t")
        wav_path = cv_dir / 'clips_wav_16k' / (path[:-4] + '.wav')
        data_infos.append([wav_path, text])
    return data_infos
def main(args):
    cv_dir = Path(args.cv_dir) / args.lang
    dataset_dir = Path(args.dataset_dir) / f'{args.lang}_bpe'
    dataset_dir.mkdir(parents=True, exist_ok=True)
    data_infos = get_commonvoice_metainfo(cv_dir)
    with open(dataset_dir / 'metadata_cv.csv', 'w') as f:
        for (wav_path, text) in data_infos:
            f.write(f'{wav_path}|{text}\n')

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="generate testset for commonvoice")
    parser.add_argument('--cv-dir',
                        type=str,
                        default='/data/duhu/cv-corpus-21.0-2025-03-14/',
                        help='path to commonvoice dataset')
    parser.add_argument('--dataset-dir',
                        type=str,
                        default="data",
                        help='')
    parser.add_argument('--lang',
                        type=str,
                        default='ug',
                        help='language to generate testset for')
    args = parser.parse_args()
    main(args)