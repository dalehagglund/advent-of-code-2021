import typing as ty
import sys
import requests

urlmap = { ... }

what = sys.argv[1]
url = urlmap[what]
dest = what + ".json"

print(f"fetching {what} from {url}")
print(f"dest {dest}")

r = requests.get(urlmap[what])
if r.status_code != 200:
    print(f"bad status: {r.status_code}")
    exit(1)

with open(dest, "w") as f:
    print(r.text, file=f, end=None)