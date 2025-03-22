# pip install pinyin_jyutping_sentence

import re
import argparse
import pinyin_jyutping_sentence
import jieba
from tqdm import tqdm
from pathlib import Path

from collections import defaultdict


def main(args):
    csv_file = Path(args.csv_file)
    cons = open(csv_file).readlines()
    vocab_dict = defaultdict(lambda : 0)
    error_numbers = 0
    for line in tqdm(cons, desc='extracting the vocabs for jyutping'):
        wav_file, text = line.strip().split('|')
        text = text.replace('*', '')
        flag = True if re.findall('([\u4e00-\u9fa5]) +([\u4e00-\u9fa5])', text) else False
        while flag:
            text = re.sub("([\u4e00-\u9fa5]) +([\u4e00-\u9fa5])", lambda x:x.group(1)+x.group(2), text)
            flag = True if re.findall('([\u4e00-\u9fa5]) +([\u4e00-\u9fa5])', text) else False
        text = re.sub('([\u4e00-\u9fa5])([a-zA-Z])', lambda x:x.group(1)+" "+x.group(2), text)
        text = re.sub('([a-zA-Z])([\u4e00-\u9fa5])', lambda x:x.group(1)+" "+x.group(2), text)
        jyutpings = pinyin_jyutping_sentence.jyutping(text, spaces=True,tone_numbers=True)
        if re.sub('[a-zA-Z0-9]', '', jyutpings).strip(): 
            error_numbers += 1
            continue
        print(line.strip())
        for jyup in jyutpings.split():
            vocab_dict[jyup] += 1



if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv-file', type=str, default='/data/duhu/F5-TTS/data/ct/metadata.csv')
    args = parser.parse_args()
    main(args)
