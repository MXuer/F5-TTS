import re
import argparse
from tqdm import tqdm
from pathlib import Path

def process_one(proj_dir: Path):
    proj_dir = proj_dir / 'DATA'
    wav_files = proj_dir.rglob('*.WAV')
    transcript_files = proj_dir.rglob('*.TXT')
    name2text = {}
    print(f'=> {proj_dir}')
    for transcript_file in tqdm(transcript_files, desc='reading transcript files...'):
        cons = open(transcript_file, encoding='utf-8-sig').readlines()
        for index in range(0, len(cons), 2):
            name, text = cons[index].split('\t')[0], cons[index+1].strip()
            text = re.sub('<.*?>', '', text).replace('*', '')
            if text:
                name2text[name] = text
    infos = []
    for wav_file in tqdm(wav_files, desc='get all wav files...'):
        name = wav_file.stem
        text = name2text.get(name, None)
        if text is None: continue
        infos.append([str(wav_file), text])
    return infos

def main(args):
    root_dir = Path(args.root_dir)
    data_dir = Path(args.data_dir)
    data_dir.mkdir(exist_ok=True, parents=True)
    meta_file = data_dir / 'metadata.csv'
    with open(meta_file, 'w') as f:
        for proj in args.projs:
            proj_dir = root_dir / proj
            infos = process_one(proj_dir)
            for info in infos:
                f.write(f'{info[0]}|{info[1]}\n')
                

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-dir',
                        default='/share/dataocean/ASR',
                        type=str,
                        help='原始数据目录')
    parser.add_argument('--projs',
                        default=["King-ASR-018", "King-ASR-023", "King-ASR-042", "King-ASR-052", "King-ASR-059", "King-ASR-065", "King-ASR-084", "King-ASR-120", "King-ASR-166", "King-ASR-169", "King-ASR-188", "King-ASR-216", "King-ASR-228", "King-ASR-256", "King-ASR-358", "King-ASR-409", "King-ASR-410", "King-ASR-428", "King-ASR-459", "King-ASR-462", "King-ASR-502", "King-ASR-503", "King-ASR-506", "King-ASR-602", "King-ASR-620", "King-ASR-625", "King-ASR-700", "King-ASR-701", "King-ASR-721", "King-ASR-722", "King-ASR-723"],
                        type=list,
                        help='包含的项目名称')
    parser.add_argument('--data-dir',
                        default='data/zh_bpe',
                        type=str,
                        help='metadata.csv存放地址')

    args = parser.parse_args()
    main(args)