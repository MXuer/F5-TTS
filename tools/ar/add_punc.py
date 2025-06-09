import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, wait, ALL_COMPLETED
from punctuators.models import PunctCapSegModelONNX


PROJS = [
    "King-ASR-109",
    "King-ASR-293",
    "King-ASR-318",
    "King-ASR-627",
    "King-ASR-628",
    "King-ASR-629",
    "King-ASR-864",
    "King-ASR-865",
    "King-ASR-907",
]

BASE_DIR = Path("/share/dataocean/ASR")

def batch_add_punctuation(input_texts, wav_files):
    print('Loading model...')
    model = PunctCapSegModelONNX.from_pretrained(
        "1-800-BAD-CODE/xlm-roberta_punctuation_fullstop_truecase"
    )
    print('Add punctuation...')
    results = model.infer(texts=input_texts, apply_sbd=True,)
    return results, wav_files


def main(args):
    final_texts, final_wav_files = [], []
    for proj in PROJS:
        print(f'Processing {proj}...')
        input_texts, wav_files = [], []
        csv_file = BASE_DIR / proj / 'metadata_tashkeel.csv'
        cons = open(csv_file).readlines()
        for line in cons:
            wav_file, text = line.strip().split("|")
            input_texts.append(text)
            wav_files.append(wav_file)
        
        
        k, r = divmod(len(input_texts), 8)
        batch_data = [
            [
                input_texts[i * k + min(i, r):(i + 1) * k + min(i + 1, r)],
                wav_files[i * k + min(i, r):(i + 1) * k + min(i + 1, r)],
            ]
            for i in range(8)
        ]
        with ProcessPoolExecutor(max_workers=8) as executor:
            tasks = []
            for index, batch in enumerate(batch_data):
                tasks.append(executor.submit(batch_add_punctuation, batch[0], batch[1],))
            wait(tasks, return_when=ALL_COMPLETED)
            
            for task in tasks:
                results, wav_files = task.result()
                final_texts += results
                final_wav_files += wav_files

    args.output_dir = Path(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.output_dir / 'metadata.csv', "w") as f:
        for index, text in enumerate(final_texts):
            wav_file = final_wav_files[index]
            text = ' '.join(text)
            f.write(f"{wav_file}|{text}\n")
    
        
        
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, required=True)
    args = parser.parse_args()
    main(args)