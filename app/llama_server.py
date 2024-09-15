import json
import subprocess
import urllib.parse
import time

import requests
from loguru import logger as log
from utils import load_config

config = load_config()

LLAMA_URL = config["llama_cpp"]["url"]
LLAMA_PORT = config["llama_cpp"]["port"]
LLAMA_MODEL = config["llama_cpp"]["model_path"]
CHAT_FORMAT = config["llama_cpp"]["chat_format"]
SYSTEM = config["model"]["system"]


def start_server():
    kill_process_llama_cpp()

    command = f'python -B -m llama_cpp.server --model "{LLAMA_MODEL}" --host 0.0.0.0 --port {LLAMA_PORT} --n_gpu_layers -1 --cache True --verbose True --chat_format {CHAT_FORMAT}'

    try:
        subprocess.Popen(command, shell=True, start_new_session=True)
    except Exception as err:
        log.info(err)


def check_server_running(label_title):
    port = LLAMA_PORT
    while True:
        try:
            subprocess.check_output(
                f"netstat -ano | findstr :{port}", shell=True, universal_newlines=True
            )
            break
        except subprocess.CalledProcessError:
            time.sleep(2)

    label_title.configure(
        text="🔴   ",
        text_color="green",
    )
    return True

def kill_process_llama_cpp():
    port = LLAMA_PORT
    try:
        output = subprocess.check_output(
            f"netstat -ano | findstr :{port}", shell=True, universal_newlines=True
        )
        pid = output.split()[-1]
        subprocess.run(f"taskkill /PID {pid} /F", shell=True, check=True)

    except subprocess.CalledProcessError as err:
        log.warning(err)


def invoke_stream(prompt: str, context: str = None):
    content = prompt
    if context:
        content = f"Contexto: {context}. {prompt}"

    payload = {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM,
            },
            {"role": "user", "content": content},
        ],
        "stream": True,
    }
    log.debug(f"PROMPT: {payload}")

    response = requests.post(
        urllib.parse.urljoin(f"{LLAMA_URL}:{LLAMA_PORT}", "/v1/chat/completions"),
        data=json.dumps(payload),
        stream=True,
    )

    response.raise_for_status()

    for line in response.iter_lines():
        if line:
            decoded_line = line.decode("utf-8")

            if decoded_line.startswith("data:"):
                json_data = decoded_line[len("data:") :].strip()

                if json_data == "[DONE]":
                    break

                chunk = json.loads(json_data)
                if "choices" in chunk and chunk["choices"]:
                    yield chunk["choices"][0]["delta"].get("content", "")
