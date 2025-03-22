import re
import json
import argparse

from tqdm import tqdm
from pathlib import Path
from openai import OpenAI
import uuid

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

client = OpenAI(api_key='test', base_url="http://10.10.23.11:8000/v1")
def single_request(info, language: str):
    prompt = f"""任务：给{language}文本加上「标点符号」，输出的时候不要修改输入的文本。请检查下文字内容是不是没有变化。请直接输出加标点之后的文本，不要输出其他内容。文本为：\n
    {info}"""
    response = client.chat.completions.create(
        model="Qwen/QwQ-32B",
        messages=[{'role': 'user', 'content': prompt}],
        stream=False,
    )
    return response.choices[-1].message.content

def batch_punc(data, index, language):
    results_dict = {}
    for ii, item in enumerate(data):
        print(f'{index} | {ii} / {len(data)} processing {item["text"]}')
        text = item['text'].replace(' ', '').replace('*', '')
        punc_result = single_request(text, language)
        punc_result_remove_think = punc_result.split('</think>')[-1].strip()
        punc_result_no_punc = re.sub('[，。？！、]', '', punc_result_remove_think)
        if text == punc_result_no_punc:
            results_dict[item['wav_file']] = punc_result_remove_think
        else:
            print(text, punc_result_remove_think)

    return results_dict

def main(args):
    csv_file = Path(args.csv_file)

    exp_dir = csv_file.parent / 'temp_punc'
    exp_dir.mkdir(exist_ok=True, parents=True)

    done_files = exp_dir.glob("*.json")

    done_results = {}
    for done_file in done_files:
        cons = json.load(open(done_file, 'r', encoding='utf-8'))
        done_results.update(cons)

    cons = open(args.csv_file, 'r', encoding='utf-8').readlines()
    
    data = []

    for line in cons:
        wav_file, text = line.strip().split('|')
        if wav_file in done_results:
            continue
        else:
            data.append({'wav_file': wav_file, 'text': text})
    print(len(data))
    return
    thead_nums = 128

    each_nums = len(data) // thead_nums + 1

    batches = [data[each_nums*index:each_nums*(index+1)] for index in range(thead_nums)]

    with ThreadPoolExecutor(max_workers=thead_nums) as executor:
        tasks = []
        for index, batch in enumerate(batches):
            task = executor.submit(batch_punc, batch, index, args.language)
            tasks.append(task)

        wait(tasks, return_when=ALL_COMPLETED)

        new_results = {}
        for task in tasks:
            result = task.result()
            new_results.update(result)
    with open(exp_dir / f'{uuid.uuid4()}.json', 'w', encoding='utf-8') as f:
        json.dump(new_results, f, ensure_ascii=False, indent=2)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv-file', default='data/ct/metadata_clean.csv', type=str)
    parser.add_argument('--language', default='粤语', type=str)
    args = parser.parse_args()
    main(args)