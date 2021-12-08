import typing as ty

import json
import sys
import datetime as dt
from zoneinfo import ZoneInfo

from dataclasses import dataclass

EST = ZoneInfo("US/Eastern")

@dataclass
class DailyResults:
    star1: ty.Optional[dt.timedelta]
    star2: ty.Optional[dt.timedelta]

    @classmethod
    def from_json(cls, j: dict):
        def midnight(t: dt.datetime) -> dt.datetime:
            return t.replace(
                hour=0, minute=0, second=0, microsecond=0)
        def decode(key: str) -> ty.Optional[dt.datetime]:
            if key not in j: return None
            ts = j[key]["get_star_ts"]
            t = dt.datetime.fromtimestamp(ts, tz=EST)
            return t - midnight(t)
        return cls(
            star1 = decode("1"),
            star2 = decode("2")
        )

@dataclass
class Member:
    name: str
    id: str 
    local_score: int
    global_score: int
    stars: int
    days: ty.List[DailyResults]
    last_star_ts: int

    @classmethod
    def from_json(cls, j: dict) -> 'Member':
        d = dict(j.items())

        if d['name'] is None:
            d['name'] = f"Anon #{d['id']}"

        levels = d["completion_day_level"]
        del d["completion_day_level"]
        d["days"] = [
            DailyResults.from_json(levels[day])
            for day in sorted(levels.keys(), key=int)
        ]

        return cls(**d)

def load_members(fname: str) -> dict:
    with open(fname) as f:
        j = json.load(f)
    return {
        m.name: m
        for m 
        in map(Member.from_json, j["members"].values())
    }    

def main():
    filename = sys.argv[1]
    members: ty.Dict[str, Member] = load_members(filename)

    def hms(t: dt.timedelta) -> ty.Tuple[int, int, int]:
        if t is None: return "        -"
        seconds = int(t.total_seconds())
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f'{h:3d}:{m:02d}:{s:02d}'
    def score(m): return m.local_score

    for m in sorted(members.values(), key=lambda m: -score(m)):
        if score(m) == 0: continue
        print(" ".join([
            f'{m.name:<15.15}',
            f'{m.local_score:>5}',
            " ".join(hms(result.star2) for result in m.days),
        ]))

if __name__ == "__main__":
    main()