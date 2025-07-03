import re
import json
import argparse
from tqdm import tqdm
from pathlib import Path
from collections import defaultdict

def read_spk2region(proj_dir: Path):
    speaker_file = proj_dir / 'TABLE' / 'SPEAKER.TXT'
    spk2region = {}
    for line in open(speaker_file, encoding='utf-8-sig').readlines():
        spk, *_, region_raw = line.strip().split('\t')
        if region_raw.endswith(','):
            region_raw = region_raw[:-1]
        region_raw = region_raw.replace('Khams', 'Kham')
        region = region_raw.split(',')[-1].strip().split('-')[-1]
        spk2region[spk] = region
        
    return spk2region


def process_one(proj_dir: Path):
    proj_dir = proj_dir / 'DATA'
    wav_files = proj_dir.rglob('*.WAV')
    transcript_files = proj_dir.rglob('*.TXT')
    
    spk2region = read_spk2region(proj_dir.parent)
    
    name2text = {}
    for transcript_file in tqdm(transcript_files, desc='reading transcript files...'):
        cons = open(transcript_file, encoding='utf-8-sig').readlines()
        for index in range(0, len(cons), 2):
            name, text = cons[index].split('\t')[0], cons[index+1].strip()
            text = re.sub('<.*?>', '', text)
            if text:
                name2text[name] = text
    infos = []
    for wav_file in tqdm(wav_files, desc='get all wav files...'):
        name = wav_file.stem
        text = name2text[name]
        spk = name[1:5]
        region = spk2region[spk]
        infos.append([str(wav_file), text, region])
    return infos

def read_dur_file(proj_dir):
    dur_json_file = proj_dir / 'duration.json'
    dur_infos = json.load(open(dur_json_file))
    return dur_infos


def main(args):
    root_dir = Path(args.root_dir)
    data_dir = Path(args.data_dir) / f'{args.lang}_lid_bpe'
    data_dir.mkdir(exist_ok=True, parents=True)
    meta_file = data_dir / 'metadata.csv'
    region2infos = defaultdict(list)
    total_dur_infos = {}
    with open(meta_file, 'w') as f:
        for proj in args.projs:
            proj_dir = root_dir / proj
            dur_infos = read_dur_file(proj_dir)
            total_dur_infos.update(dur_infos)
            infos = process_one(proj_dir)
            for info in infos:
                wav_file, text, region = info
                region2infos[region].append([wav_file, text])
                # f.write(f'{wav_file}|{text}\n')
                f.write(f'{wav_file}|<{region}>{text}</{region}>\n')
    dur_json_file = data_dir / 'raw_dur.json'
    with open(dur_json_file, 'w') as f:
        f.write(json.dumps(total_dur_infos, ensure_ascii=False))
                
    
    for region, infos in region2infos.items():
        region_data_dir = Path(args.data_dir) / f'{args.lang}_{region}_bpe'
        region_data_dir.mkdir(exist_ok=True, parents=True)
        each_dur_info = {}
        with open(region_data_dir / 'metadata.csv', 'w') as f:
            for wav_file, text in infos:
                f.write(f'{wav_file}|{text}\n')
                each_dur_info[wav_file] = total_dur_infos[wav_file]
                
        each_dur_json_file = region_data_dir / 'raw_dur.json'
        with open(each_dur_json_file, 'w') as f:
            f.write(json.dumps(each_dur_info, ensure_ascii=False))
                


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-dir',
                        default='/share/dataocean/ASR',
                        type=str,
                        help='原始数据目录')
    parser.add_argument('--projs',
                        default=['King-ASR-426', 'King-ASR-742'],
                        type=list,
                        help='包含的项目名称')
    parser.add_argument('--data-dir',
                        default='data/',
                        type=str,
                        help='metadata.csv存放地址')
    parser.add_argument('--lang',
                        default='bo',
                        type=str,
                        help='metadata.csv存放地址')

    args = parser.parse_args()
    main(args)