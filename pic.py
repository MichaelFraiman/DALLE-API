import openai
import os
import requests
import datetime
import json
import re
import sys
import argparse
from pathlib import Path


def main():

    with open("key.pem", "r") as f:
        s = f.read()
    
    TOKEN = re.sub(r"\n","",s)
    openai.api_key = TOKEN

    dir_name = "p"
    dir_path = Path(dir_name)
    dir_path.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description='Process DALLE options')
    parser.add_argument('prompt', type=str, help='Prompt')
    parser.add_argument('-n', '--number', type=int, help='Number of pics', default=1)
    parser.add_argument('-s', '--size', type=str, help='Size of the pic', default='1024x1024')

    args = parser.parse_args()

    gen_image(args.prompt, n = args.number, size = args.size, dir = dir_name)

    return 


def download_image(url, name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'{name}.png', 'wb') as f:
            f.write(response.content) 

def get_time():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d_%H-%M-%S-%f')[:-3]

    return formatted_datetime

def clear_name(filename):
    filename = filename.replace("/",". ")
    filename = filename.replace("\\",". ")
    filename = filename.replace("|",". ")
    filename = filename.replace(":","-")
    filename = filename.replace("?",".")
    filename = filename.replace("*",".")
    filename = filename.replace('"',"'")
    filename = filename.replace("<","-")
    filename = filename.replace(">","-")
    filename = filename.replace(",",".")
    filename = re.sub(r"\s+", "_", filename)

    return filename

def modify_json(filename, append):

    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print("Error, something is wrong with file, I am assuming it's empty")
        data = []

    data += append

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def gen_image(prompt, n=1, size='1024x1024', dir="p"):

    response = openai.Image.create(
        prompt = prompt,
        n = n,
        size = size
    )

    images = []

    print(response)

    for i in response['data']:
        images.append(i['url'])

    log = []

    for image_url in images:
        t = get_time()
        name = os.path.join(dir, t + "_" + clear_name(prompt))
        download_image(image_url, name)
        entry = {
            "prompt": prompt,
            "n": n,
            "size": size,
            "url": image_url,
            "name": name
        }
        log.append(entry)

    modify_json("log.json", log)

    return

main()