import sys
import typing as ty
from dataclasses import dataclass, field
from collections import Counter, defaultdict, deque

@dataclass(frozen=True)
class Node:
    label: str

    def __str__(self):
        return f'{self.label}'
    def __repr__(self):
        return f'N:{self.label}'

    def is_big(self):
        return self.label == self.label.upper()
    def is_small(self):
        return self.label == self.label.lower()

@dataclass
class Graph:
    nodes: ty.Set[Node] = field(default_factory=set)
    by_label: ty.Dict[str, Node] = field(default_factory=dict)
    adjacent: ty.Dict[Node, ty.Set[Node]] = field(default_factory=lambda: defaultdict(set))

    def add_node(self, label: str) -> Node:
        if label not in self.by_label:
            n = Node(label)
            self.nodes.add(n)
            self.by_label[label] = n
        n = self.by_label[label]
        assert n in self.nodes
        assert label in self.by_label
        return n

    def add_edge(self, n1: Node, n2: Node):
        assert n1 in self.nodes
        assert n2 in self.nodes
        assert {n1, n2} <= self.nodes, \
            f"add_edge: can't find {n1} or {n2}"
        self.adjacent[n1].add(n2)
        self.adjacent[n2].add(n1)

    def lookup(self, s: str) -> Node:
        return self.by_label[s]

@dataclass
class PathState:
    g: Graph
    visited: ty.Set[Node]
    path: ty.List[Node]
    dup_small: ty.Optional[Node] = None

    def end(self) -> Node:
        return self.path[-1]

    def next_state_2(self) -> ty.Iterator['PathState']:
        for n in self.g.adjacent[self.path[-1]]:
            dup_small = self.dup_small
            if n.is_big():
                pass
            elif n not in self.visited:
                pass
            elif n == self.g.lookup('start') or n == self.g.lookup('end'):
                continue
            elif dup_small is None:
                dup_small = n
            else:
                continue
                    
            yield PathState(
                g = self.g,
                visited = self.visited | { n },
                path = self.path + [n], 
                dup_small = dup_small,
            )
            
    def next_state_1(self) -> ty.Iterator['PathState']:
        for n in self.g.adjacent[self.path[-1]]:
            if n in self.visited and n.is_small(): continue
            yield PathState(
                g = self.g,
                visited = self.visited.union({ n }),
                path = self.path + [n]
            )

def find_paths(
    g: Graph,
    start: Node, end: Node,
    expand_path
) -> ty.Iterator[ty.List[Node]]:
    queue: ty.Deque[PathState] = deque()
    queue.append(PathState(g, {start}, [start]))
    while queue:
        ps = queue.popleft()
        if ps.end() == end:
            yield ps.path
            continue
        queue.extend(expand_path(ps))

def read_input(fname: str) -> Graph:
    with open(fname) as f:
        g = Graph()
        for line in f:
           n1, n2 = map(g.add_node, line.strip().split("-"))
           g.add_edge(n1, n2)
        return g

def part1(fname: str):
    g = read_input(fname)
    start = g.lookup('start')
    end = g.lookup('end')

    paths = list(find_paths(g, start, end, PathState.next_state_1))
    print(f"part1: {len(paths)}")

    paths = list(find_paths(g, start, end, PathState.next_state_2))
    print(f"part2: {len(paths)}")

def part2(fname: str):
    print(f"part2:")

if __name__ == '__main__':
    part1(sys.argv[1])
