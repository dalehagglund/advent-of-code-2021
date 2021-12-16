from abc import ABC, abstractmethod
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
import typing as ty
from functools import reduce
from contextlib import contextmanager

to_bits = {
    "0": "0000",
    "1": "0001",
    "2": "0010",
    "3": "0011",
    "4": "0100",
    "5": "0101",
    "6": "0110",
    "7": "0111",
    "8": "1000",
    "9": "1001",
    "A": "1010",
    "B": "1011",
    "C": "1100",
    "D": "1101",
    "E": "1110",
    "F": "1111",
}

@dataclass
class bitstream:
    bits: ty.List[int]
    pos: int = 0
    def take(self, n: int) -> int:
        v = self.peek(n)
        self.pos += n
        return v
    @classmethod
    def from_hex(cls, hex: str):
        bits = list(map(
            int,
            "".join(to_bits[c] for c in hex)
        ))
        return cls(bits, 0)

    def save(self) -> int: return self.pos
    def restore(self, pos): self.pos = pos

    def peek(self, n: int) -> int:
        assert n <= len(self), f'{n = } {len(self) = }'
        v = reduce(
            lambda acc, b: acc * 2 + b,
            self.bits[self.pos: self.pos+n],
            0)
        return v
    def __len__(self):
        return len(self.bits) - self.pos
    def __str__(self):
        return (
            "".join("01"[b] for b in self.bits[:self.pos])
            + "^"
            + "".join("01"[b] for b in self.bits[self.pos:])
        )
    __repr__ = __str__ 

def read_input(fname: str):
    with open(fname) as f:
        return [
            (line.strip(), bitstream.from_hex(line.strip()))
            for line
            in f
        ]


class Packet(ABC):
    @abstractmethod
    def sum_version(self) -> int: ...
    @abstractmethod
    def eval(self) -> int: ... 


@dataclass(frozen=True)
class Lit(Packet):
    hdr: int
    ptype: int
    value: int
    def sum_version(self): return self.hdr
    def eval(self): return self.value

@dataclass(frozen=True)
class Op(Packet):
    hdr: int
    ptype: int
    mode: int
    n: int
    packets: ty.List[Packet]
    def sum_version(self):
        return self.hdr + sum(pkt.sum_version() for pkt in self.packets)
    def eval(self):
        import operator
        pkts = self.packets
        if self.ptype == 0:
            return sum(p.eval() for p in pkts)
        elif self.ptype == 1:
            return reduce(operator.mul, (p.eval() for p in pkts), 1)
        elif self.ptype == 2:
            return min(p.eval() for p in pkts)
        elif self.ptype == 3:
            return max(p.eval() for p in pkts)
        elif self.ptype == 5:
            return int(operator.gt(pkts[0].eval(), pkts[1].eval()))
        elif self.ptype == 6:
            return int(operator.lt(pkts[0].eval(), pkts[1].eval()))
        elif self.ptype == 7:
            return int(operator.eq(pkts[0].eval(), pkts[1].eval()))

        return -1

@contextmanager
def savepos(bits):
    pos = bits.save()
    yield bits
    bits.restore(pos)

def skip_expected_zeros(bits, end):
    assert bits.pos <= end
    assert bits.peek(end - bits.pos) == 0
    bits.take(end - bits.pos)

def parse_packet(bits, expected: ty.Optional[int]):
    start = bits.pos
    with savepos(bits) as b:
        _, ptype = b.take(3), b.take(3)
    if ptype == 4:
        pkt = parse_literal(bits, expected) 
    else:
        pkt = parse_operator(bits, expected)
    
    if expected is not None:
        skip_expected_zeros(bits, start + expected)

    return pkt

def parse_operator(bits, expected: int) -> Op:
    start = bits.pos
    hdr, ptype = bits.take(3), bits.take(3)
    assert ptype != 4
    mode = bits.take(1)
    if mode == 0:
        n = bits.take(15)
    else:
        n = bits.take(11)

    op = Op(hdr, ptype, mode, n, [])
    payload_start = bits.pos

    def consume_by_length(bitcount: int):
        # print(f'{bits.pos = } {payload_start = } {bitcount = } {bits}')
        while bits.pos - payload_start < bitcount:
            op.packets.append(parse_packet(bits, None))
            # print(f'{bits.pos = } {payload_start = } {bitcount = } {bits}')
        assert bits.pos - payload_start == bitcount, \
            f'exceeded bit length: {bitcount = } {op = } {bits = }'
    
    def consume_by_count(count: int):
        # print(f'{bits.pos = } {payload_start = } {count = } {bits}')
        for i in range(count):
            op.packets.append(parse_packet(bits, None))
            # print(f'{bits.pos = } {payload_start = } {i = } {bits}')

    if mode == 0:       # bit length
        consume_by_length(n)
    else:               # packet count
        consume_by_count(n)

    if expected is not None:
        skip_expected_zeros(bits, start + expected)

    return op

def parse_literal(bits, expected: ty.Optional[int]) -> Lit:
    start = bits.pos
    hdr, ptype = bits.take(3), bits.take(3)

    assert ptype == 4

    value = 0
    while True:
        flag, nibble = bits.take(1), bits.take(4)
        value = value * 16 + nibble
        if not flag:
            break

    if expected is not None:
        skip_expected_zeros(bits, start + expected)

    return Lit(hdr, ptype, value)

def part1(fname:str):
    print("=" * 10, "part1")
    for hex, bits in read_input(fname):
        pkt = parse_packet(bits, len(bits))
        print(f'>>> {hex}')
        # print('   ', pkt)
        # print('   ', bits)
        print('   ptype', pkt.ptype)
        print('   sum  ' , pkt.sum_version())
        print('   eval ', pkt.eval())

def part2(fname: str):
    print("=" * 10, "part2")
    ...

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])