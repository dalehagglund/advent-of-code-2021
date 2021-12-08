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

config = read_config("leaders.ini")
for section in 'fetch boards'.split():
    if section not in config:
        warn(f"fetch: no [{section}] section in leaders.ini")
        exit(1)

year = 2021
board = sys.argv[1]
id = int(config['boards'][board])
session = config['fetch']['session']

url = board_url(config, id)
dest = f'data/{board}.json'

print(f"year {year} board {board}")
print(f"from {url}")
print(f"session {session}")
print(f"dest {dest}")

cookies = {'session': session}
r = requests.get(url, cookies=cookies)
if r.status_code != 200:
    print(f"bad status: {r.status_code}", file=sys.stderr)
    exit(1)

if not r.text.startswith('{'):
    head = "\n".join(r.text.split("\n")[:25])
    print(f"bad response: {head}", file=sys.stderr)
    exit(1)

j = r.json()
with open(dest, "w") as f:
    print(json.dumps(j, indent=4), file=f)