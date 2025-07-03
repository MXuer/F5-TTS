import os
import json
from pathlib import Path
from time import sleep
from concurrent.futures import ProcessPoolExecutor, ALL_COMPLETED, wait
import requests
import datetime
import logging


LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d:%(funcName)s] %(message)s"
LOGGING_LEVEL = logging.INFO
logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)

SHORT_URL = "http://ai.speechocean.com/speech/api/v2/asr/recognize"
TOKEN_URL = "http://auth.ai.speechocean.com/api/v2/login_token"


def get_app_key(appkey_dir=".appkeys"):
    os.makedirs(appkey_dir, exist_ok=True)
    now = datetime.datetime.now()
    now_str = datetime.datetime.strftime(now, "%Y-%m-%d")
    appkey_file = os.path.join(appkey_dir, f"{now_str}.json")
    
    if os.path.exists(appkey_file):
        appkey = json.loads(open(appkey_file).read())["data"]["access_token"]
    else:
        request = {
            "username": os.environ.get('tts_name'),
            "password": os.environ.get('tts_passwd')
        }
        headers = {
            "Authorization": "application/json"
        }
        
        resp = requests.post(TOKEN_URL, json=request, headers=headers, timeout=10)
        appkey_json = resp.json()
        appkey = appkey_json["data"]["access_token"]
        with open(appkey_file, 'w') as f:
            f.write(json.dumps(appkey_json, ensure_ascii=False, indent=2))
    return appkey


def recognize_short(wav_file, language, appkey):
    text = None
    request = {
        "domain": f"{language}",
        "add_punct": False
    }
    headers = {
        "Authorization": f"Bearer {appkey}",
        "Knative-Serving-Tag": "normal"
    }
    while text is None:
        try:
            files = {
                "wav_path": open(wav_file, "rb"),
            }
            resp = requests.post(SHORT_URL, data=request, headers=headers, files=files, timeout=30)
            rec_result = resp.json()
            if rec_result['code'] == 200:
                text = [ele['text'] for ele in rec_result['data']['segments']]
                text = " ".join(text)
                logging.info(f'{wav_file} {text}')
        except Exception as e:
            pass
            # logging.info(f"Recognition error with {e} {language}")
        sleep(2)
    return text

def batch_asr(wav_files: list, language: str, appkey: str, db_dir: Path):
    name2results = {}
    for index, wav_file in enumerate(wav_files):
        text = recognize_short(str(wav_file), language, appkey)
        logging.info(f'{index+1} / {len(wav_files)} | {round((index+1) * 100 / len(wav_files), 3)}% recognizing {wav_file.name} | {text}...')
        if text is None:
            continue
        name2results[wav_file] = text


def dataocean_batch_asr(wav_dir, lang):
    if lang == "bo":
        lang = "bo_lhasa"
        
    wav_files = list(Path(wav_dir).rglob('*.wav'))
    app_key = get_app_key()
    total_results = {}
    while len(wav_files) != len(total_results):
        to_be_done = [wav_file for wav_file in wav_files if not wav_file in total_results]
        k, r = divmod(len(to_be_done), 96)
        batch_asr_data = [to_be_done[i * k + min(i, r):(i + 1) * k + min(i + 1, r)] for i in range(96)]
        
        with ProcessPoolExecutor(max_workers=96) as executor:
            tasks = []
            for index, batch in enumerate(batch_asr_data):
                tasks.append(executor.submit(batch_asr, batch, lang, app_key))

            for task in tasks:
                total_results.update(task.result())
        sleep(10)

