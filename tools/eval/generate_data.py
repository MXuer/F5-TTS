import os
import re
import random
import argparse

from tqdm import tqdm
from pathlib import Path
from pydub import AudioSegment
from collections import defaultdict

random.seed(2005)

def get_tts_metainfo(data_dir: Path):
    txt_files = data_dir.rglob('*.txt')
    wav_files = data_dir.rglob('*.wav')
    
    name2text = {}
    for txt_file in txt_files:
        cons = open(txt_file, encoding='utf-8-sig').readlines()
        for index in range(0, len(cons), 2):
            name, text = cons[index].strip().split('\t')
            text = text.replace('/', '').replace('%', '')
            if re.findall('[a-zA-Z0-9\(\)《》]', text): continue
            name2text[name] = text
    id2infos = defaultdict(list)
    for wav_file in wav_files:
        name = wav_file.stem
        id = name.split('_')[0]
        if name not in name2text: continue
        id2infos[id].append([wav_file, name2text[name]])
        
    return id2infos
        
    
        


def main(args):
    data_dir = Path(args.data_dir)
    testset_dir = Path(args.testset_dir) / args.lang
    testset_dir.mkdir(parents=True, exist_ok=True)
    id2infos = get_tts_metainfo(data_dir)

    prompt_wavs_dir = testset_dir / 'prompt-wavs'
    wavs_dir_dir = testset_dir / 'wavs'
    prompt_wavs_dir.mkdir(parents=True, exist_ok=True)
    wavs_dir_dir.mkdir(parents=True, exist_ok=True)
    
    with open(testset_dir / 'meta.lst', 'w', encoding='utf-8') as f:
        for id, infos in tqdm(id2infos.items(), desc='generate test dataset...'):
            random.shuffle(infos)
            split_num = len(infos) // 2
            prompt_infos, gen_infos = infos[:split_num], infos[split_num:]
            chosen_files = []
            for index in range(300):
                prompt_raw_file, prompt_text = random.choice(prompt_infos)
                prompt_name = prompt_raw_file.stem
                prompt_wav_file = prompt_wavs_dir / f"{prompt_name}.wav"
                
                gen_raw_file, gen_text = random.choice(gen_infos)
                gen_name = gen_raw_file.stem
                filename = f"{prompt_name}-{gen_name}"
                
                if filename in chosen_files: 
                    continue
                
                prompt_sound = AudioSegment.from_file(prompt_raw_file)
                prompt_sound.export(prompt_wav_file, format="wav", parameters=["-ar", "16000", "-ac", "1", "-loglevel", "quiet"])
                gen_sound = AudioSegment.from_file(gen_raw_file)
                gen_sound.export(wavs_dir_dir / f"{gen_name}.wav", format="wav", parameters=["-ar", "16000", "-ac", "1", "-loglevel", "quiet"])
                
                f.write(f'{filename}|{prompt_text}|prompt-wavs/{prompt_name}.wav|{gen_text}\n')
                

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="generate testset for commonvoice")
    parser.add_argument('--data-dir',
                        type=str,
                        default='/share/dataocean/TTS/King-TTS-201',
                        help='path to commonvoice dataset')
    parser.add_argument('--testset-dir',
                        type=str,
                        default="data/dotts_testset",
                        help='path to testset dir')
    parser.add_argument('--lang',
                        type=str,
                        default='bo',
                        help='language to generate testset for')
    args = parser.parse_args()
    main(args)