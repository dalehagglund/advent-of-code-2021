import typing as ty
import sys
import requests
from configparser import ConfigParser
import json
from functools import partial

warn = partial(print, file=sys.stderr)

def read_config(fname: str) -> ConfigParser:
    config = ConfigParser()
    config.read(['leaders.ini'])
    return config

def board_url(config, id) -> str:
    template = config['fetch']['template']
    year = config['fetch']['year']
    return template.format(year=year, id=id)

def fetch_board(config, board):
    id = int(config['boards'][board])
    url = board_url(config, id)
    session = config['fetch']['session']
    cookies = {'session': session}

    r = requests.get(url, cookies=cookies)
    if r.status_code != 200:
        print(f"bad status: {r.status_code}", file=sys.stderr)
        exit(1)
    if not r.text.startswith('{'):
        head = "\n".join(r.text.split("\n")[:25])
        print(f"bad response: {head}", file=sys.stderr)
        exit(1)
    return r.json()

def save_json(j, dest):
    with open(dest, "w") as f:
        print(json.dumps(j, indent=4), file=f)

config = read_config("leaders.ini")
for section in 'fetch boards'.split():
    if section not in config:
        warn(f"fetch: no [{section}] section in leaders.ini")
        exit(1)

for board in sys.argv[1:]:
    print(f"fetching {board} ...")
    j = fetch_board(config, board)

    dest = f'data/{board}.json'
    print(f'writing to {dest} ...')
    save_json(j, dest)