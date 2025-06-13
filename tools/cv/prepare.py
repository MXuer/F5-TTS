import re
import argparse
from tqdm import tqdm
from pathlib import Path

def process_one(proj_dir: Path):
    proj_dir = proj_dir / 'DATA'
    wav_files = proj_dir.rglob('*.WAV')
    transcript_files = proj_dir.rglob('*.TXT')
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
        infos.append([str(wav_file), text])
    return infos


def get_commonvoice_metainfo(cv_dir: Path, setname: str = "validated.tsv"):
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
                        default=['King-ASR-426', 'King-ASR-742'],
                        type=list,
                        help='包含的项目名称')
    parser.add_argument('--data-dir',
                        default='data/bo_bpe',
                        type=str,
                        help='metadata.csv存放地址')

    args = parser.parse_args()
    main(args)