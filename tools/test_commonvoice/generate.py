import os
import sys
import random
import argparse

from tqdm import tqdm
from pathlib import Path
from pydub import AudioSegment
from collections import defaultdict

random.seed(2005)

def get_commonvoice_metainfo(cv_dir: Path, setname: str):
    tsv_file = cv_dir / f"{setname}.tsv"
    id2mp3_files = defaultdict(list)
    id2texts = defaultdict(list)
    for line in tqdm(open(tsv_file, "r").readlines()[1:], desc=f'reading {tsv_file}'):
        client_id, path, _, text, *_ = line.strip().split("\t")
        mp3_path = cv_dir / 'clips' / path
        id2mp3_files[client_id].append(str(mp3_path))
        id2texts[client_id].append(text)
    return id2mp3_files, id2texts
def main(args):
    cv_dir = Path(args.cv_dir)
    testset_dir = Path(args.testset_dir) / args.lang
    testset_dir.mkdir(parents=True, exist_ok=True)
    id2wav_files, id2texts = get_commonvoice_metainfo(cv_dir, args.setname)
    counts = 0
    prompt_wavs_dir = testset_dir / 'prompt-wavs'
    wavs_dir_dir = testset_dir / 'wavs'
    prompt_wavs_dir.mkdir(parents=True, exist_ok=True)
    wavs_dir_dir.mkdir(parents=True, exist_ok=True)
    with open(testset_dir / 'meta.lst', 'w', encoding='utf-8') as f:
        for id, mp3_files in tqdm(id2wav_files.items(), desc='generate final testset'):
            if len(mp3_files) <= 2:
                continue
            texts = id2texts[id]
            prompt_mp3_file = random.choice(mp3_files)
            prompt_index = mp3_files.index(prompt_mp3_file)
            prompt_text = texts[prompt_index]
            
            mp3_files = mp3_files[:prompt_index] + mp3_files[prompt_index+1:]
            texts = texts[:prompt_index] + texts[prompt_index+1:]
            
            other_two_mp3_file = random.sample(mp3_files, min(2, len(mp3_files)))
            other_two_text =  [texts[mp3_files.index(mp3_file)] for mp3_file in other_two_mp3_file]
            counts += 1
            prompt_name = os.path.basename(prompt_mp3_file)[:-4]
            prompt_wav_file = prompt_wavs_dir / f"{prompt_name}.wav"
            prompt_sound = AudioSegment.from_file(prompt_mp3_file)
            prompt_sound.export(prompt_wav_file, format="wav", parameters=["-ar", "16000", "-ac", "1", "-loglevel", "quiet"])
            
            for index, gen_mp3_file in enumerate(other_two_mp3_file):
                gen_name = os.path.basename(gen_mp3_file)[:-4]
                gen_sound = AudioSegment.from_file(gen_mp3_file)
                gen_sound.export(wavs_dir_dir / f"{gen_name}.wav", format="wav", parameters=["-ar", "16000", "-ac", "1", "-loglevel", "quiet"])
                gen_text = other_two_text[index]
                filename = f"{prompt_name}-{gen_name}"
                f.write(f'{filename}|{prompt_text}|prompt-wavs/{prompt_name}.wav|{gen_text}\n')
                
        print(counts)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="generate testset for commonvoice")
    parser.add_argument('--cv-dir',
                        type=str,
                        default=None,
                        help='path to commonvoice dataset')
    parser.add_argument('--testset-dir',
                        type=str,
                        default="data/dotts_testset",
                        help='path to testset dir')
    parser.add_argument('--lang',
                        type=str,
                        default=None,
                        help='language to generate testset for')
    parser.add_argument('--num-samples',
                        type=int,
                        default=1000,
                        help='number of samples to generate')
    parser.add_argument('--setname',
                        type=str,
                        default='test',
                        help='name of the set to sample',
                        choices=['train', 'dev', 'test'])
    args = parser.parse_args()
    main(args)