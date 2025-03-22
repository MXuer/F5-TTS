import os
import re
import sys
import yaml
import argparse
from pathlib import Path
from tqdm import tqdm

def main(args):
    with open(args.config_file) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    root_dir = Path(config['root_dir'])

    name2wav_file = {}
    dataset_infos = []
    for dataset in config['datasets']:
        print(f'{dataset}...')
        dataset_dir = root_dir / dataset
        wav_files = Path(dataset_dir / 'DATA').rglob("*.WAV")
        for wav_file in tqdm(wav_files, desc='read wav files'):
            name2wav_file[wav_file.stem] = str(wav_file)

        script_files = Path(dataset_dir / 'DATA').rglob("*.TXT")
        for script_file in tqdm(script_files, desc='read script files'):
            cons = open(script_file).readlines()
            for index in range(0, len(cons), 2):
                name, *_ = cons[index].split()
                text = cons[index + 1].strip()
                text = re.sub('<.*?>', '', text)
                if name not in name2wav_file:
                    continue
                dataset_infos.append(
                    f'{str(name2wav_file[name])}|{text}'
                )


    exp_dir = Path(config['data_dir']) / config['language']
    exp_dir.mkdir(exist_ok=True, parents=True)

    with open(exp_dir / 'metadata.csv', 'w') as f:
        for info in dataset_infos:
            f.write(info + '\n')

    



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", type=str, default="configs/default.yaml")
    args = parser.parse_args()

    main(args)
