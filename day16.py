"""
https://adventofcode.com/2022/day/16
"""

from collections import deque
from heapq import heappush, heappop
import re
from typing import IO, Collection, Literal, Sequence, NamedTuple, NewType, Self

from aoc import puzzle


Label = NewType("Label", str)
Path = tuple[Label, ...]


class Room(NamedTuple):
    label: Label
    flow_rate: int
    exits: tuple[Label]


START = Label("AA")


def parse_input(input: IO[str]):
    # Valve BB has flow rate=13; tunnels lead to valves CC, AA
    pattern = re.compile(
        r"^Valve (?P<label>.+) has flow rate=(?P<rate>\d+);"
        r" tunnels? leads? to valves? (?P<exits>.+)$"
    )
    for line in input:
        m = pattern.match(line)
        assert m is not None
        label = Label(m["label"])
        flow_rate = int(m["rate"])
        exits = tuple(Label(x) for x in m["exits"].split(", "))
        yield Room(label, flow_rate, exits)


def solve_reachability(rooms: dict[Label, Room]) -> dict[Label, dict[Label, Path]]:
    graph: dict[Label, dict[Label, Path]] = {}
    for source in rooms.values():
        if source.flow_rate == 0 and source.label != START:
            continue
        paths = {}
        graph[source.label] = paths
        queue: deque[tuple[Path, Label]] = deque(
            [((dest,), dest) for dest in source.exits]
        )
        visited = {source.label}
        while queue:
            path, label = queue.popleft()
            room = rooms[label]
            visited.add(label)
            if room.flow_rate > 0:
                try:
                    prev_cost = len(paths[label])
                except KeyError:
                    paths[label] = path
                else:
                    if len(path) < prev_cost:
                        paths[label] = path
            for exit in room.exits:
                if exit not in visited:
                    queue.append(((*path, exit), exit))

    return graph


def collapse_graph(
    rooms: dict[Label, Room], start: Label = Label("AA")
) -> dict[Label, dict[Label, int]]:
    graph: dict[Label, dict[Label, int]] = {}
    for source in rooms.values():
        if source.flow_rate == 0 and source.label != start:
            continue
        paths = {}
        graph[source.label] = paths
        for dest in source.exits:
            stack: list[tuple[int, Label]] = [(1, dest)]
            visited = [source.label]
            while stack:
                cost, label = stack.pop()
                room = rooms[label]
                visited.append(label)
                if room.flow_rate > 0:
                    prev_cost = paths.get(label, float("inf"))
                    if cost < prev_cost:
                        paths[label] = cost
                else:
                    for exit in room.exits:
                        if exit not in visited:
                            stack.append((cost + 1, exit))

    return graph


def solve(
    rooms: dict[Label, Room], start: Label, max_depth: int = 30, two_rooms: bool = False
):
    graph = solve_reachability(rooms)

    paths = {
        src: sorted(
            ((dest, len(path), rooms[dest].flow_rate) for dest, path in paths.items()),
            key=lambda x: (x[1], -x[2]),
        )
        for src, paths in graph.items()
    }

    class Actor(NamedTuple):
        minutes_left: int = max_depth
        room: Room = rooms[start]

        def __repr__(self):
            return f"{self.room.label}@{self.minutes_left}"

    class Frame(NamedTuple):
        prio: int | float
        timer: int
        actors: tuple[Actor, ...]
        upper_bound: int = 999999999
        open: frozenset[Label] = frozenset()
        value: int = 0
        trace: tuple[tuple[int, int, str], ...] = ()

        def go_open(
            self,
            label: Label,
            cost: int,
            which: Literal[0] | Literal[1],
        ) -> Self:
            actor = self.actors[which]

            assert len(graph[actor.room.label][label]) == cost
            assert label not in self.open

            room = rooms[label]
            new_open = self.open.union((label,))
            new_minutes_left = actor.minutes_left - cost - 1
            value = room.flow_rate * new_minutes_left
            total_value = self.value + value
            trace = (which, new_minutes_left, label)

            new_actor = Actor(new_minutes_left, room)

            new_actors = (*self.actors[:which], new_actor, *self.actors[which + 1 :])
            assert len(new_actors) == len(self.actors)

            # potential_h = (max_valves - len(new_open)) * (new_minutes_left - 2)
            # potential_h = sum(
            #     r.flow_rate * new_minutes_left
            #     for r in rooms.values()
            #     if r.label not in new_open
            # )
            ubound = total_value + ubound_heuristic_two_headed(
                paths, new_actors, new_open
            )
            # lbound, _ = heuristic(graph, rooms, label, new_minutes_left, new_open)
            # if lbound > best_solution:
            #     print(lbound)

            return Frame(
                prio=self.prio - value - ubound,
                timer=timer,
                actors=new_actors,
                upper_bound=ubound,
                open=new_open,
                value=total_value,
                trace=(*self.trace, trace),
            )

    max_valves = sum(1 for room in rooms.values() if room.flow_rate > 0)

    actors = (Actor(),)
    if two_rooms:
        actors *= 2

    queue = [Frame(0, 0, actors)]
    solutions: list[Frame] = []
    best_solution = 0
    timer = 0
    while queue:
        if timer % 10_000 == 0:
            print(f"... {len(queue)=} ...")
        # if timer < 10:
        #     print(f"Queue at {timer=}:")
        #     for x in sorted(queue):
        #         print(
        #             f"{x.prio:5} depth {x.actors} value={x.value:4}: {', '.join(x.trace)}"
        #         )
        #     print()

        timer += 1
        if timer > 8_000_000 and len(queue) > 100:
            print("\n\n!!!!!!!!!!!!!!!!!!!!!!!! GIVING UP !!!!!!!!!!!!!!!!!!!!!!!!")
            print(f"{len(queue)} items left in queue")
            break

        current = heappop(queue)

        if current.upper_bound < best_solution:
            continue

        any_exit = False
        which = max(range(len(actors)), key=lambda i: current.actors[i].minutes_left)
        assert which in (0, 1)
        actor = current.actors[which]
        for destination, cost, _ in paths[actor.room.label]:
            if actor.minutes_left > cost + 1 and destination not in current.open:
                any_exit = True
                frame = current.go_open(destination, cost, which)
                # (early pruning, the real check is done when popping)
                if frame.upper_bound > best_solution:
                    heappush(queue, frame)

        if not any_exit:
            if current.value > best_solution:
                print("found new solution")
                print("open", current.open)
                print("total relieved pressure", current.value)
                solutions.append(current)
                best_solution = current.value
    else:
        print(f"\n======= Solutions (after {timer} cycles) =======\n")

    solutions.sort(key=lambda s: s.value)
    for solution in solutions:
        print("found at cycle", solution.timer)
        print("open valves", ", ".join(sorted(solution.open)))
        print("total relieved pressure", solution.value)
        print(("|" + " 1 2 3 4 5 6 7 8 9 |" * 3)[: (max_depth + 1) * 2])
        for actor in 0, 1:
            time = max_depth
            for which, minutes_left, room in solution.trace:
                if which == actor:
                    prefix = (time - minutes_left) * 2
                    time = minutes_left - 1
                    print(" " * prefix + room, end="")
            print()
        print()


def draw_map(rooms: dict[Label, Room]):
    import graphviz

    # graph = solve_reachability(rooms)
    graph = collapse_graph(rooms)

    dot = graphviz.Graph(
        comment="Valves",
        # engine="dot",
        # engine="neato",
        # graph_attr=dict(
        #     mode="ipsep",
        #     overlap="prism",
        # ),
        engine="sfdp",
        graph_attr=dict(
            overlap="prism",
        ),
        edge_attr={"color": "#305050"},
        node_attr=dict(
            fontname="Comic Sans MS",
        ),
    )
    for node_id, edges in graph.items():
        room = rooms[node_id]
        if node_id == "AA":
            label = "AA"
            attrs = dict(
                penwidth="2",
                shape="doublecircle",
            )
        elif room.flow_rate > 0:
            label = f"{node_id}\n{room.flow_rate}"
            attrs = dict(
                shape="circle",
            )
        else:
            label = node_id
            attrs = dict(
                shape="circle",
                style="filled",
                fontcolor="white",
                # fillcolor="blue",
                color="#181820",
                fontsize="4",
                height="0.2",
                margin="0.05",
                # width="0",
            )
        dot.node(node_id, label, **attrs)
        for destination, cost in edges.items():
            if node_id < destination:
                dot.edge(node_id, destination, str(cost))

    # print(dot.source)
    dot.view()


def ubound_heuristic(
    graph: dict[Label, dict[Label, Path]],
    rooms: dict[Label, Room],
    start: Label,
    turns: int,
    open_valves: Sequence[Label] = (),
    initial: int = 0,
) -> int:
    # errrr this is the same as heuristic() below but returns early to only
    # compute the upper bound when it can (almost always)
    room = start
    values = [
        (
            (turns - len(paths) - 1) * rooms[r].flow_rate,
            -len(paths),
            r,
        )
        for r, paths in graph[room].items()
        # for r, path in graph[room].items()
        if (turns - len(paths) - 1) > 0 and r not in open_valves
    ]
    if values:
        # as an upper bound, we imagine an ideal path where we collect
        # the best value by jumping from the top room to the next best
        # in 1 minute (+1 to open the valve):
        values.sort()
        value, cost, room = values.pop()
        upper = initial + value
        ideal_distance = (-cost) + 1
        while values:
            _, _, r = values.pop()
            if ideal_distance <= turns:
                upper += (turns - ideal_distance) * rooms[r].flow_rate
                ideal_distance += 2
            else:
                break
        return upper
    else:
        return initial


# @profile
def ubound_heuristic_two_headed(
    paths: dict[Label, list[tuple[Label, int, int]]],
    actors: tuple[tuple[int, Room], ...],
    open_valves: Collection[Label] = (),
    heappush=heappush,
    heappop=heappop,
) -> int:
    # as an upper bound, we imagine an ideal path where we collect
    # the best value by jumping from the top room to the next best
    # in 1 minute (+1 to open the valve)
    upper = 0
    for turns, room in actors:
        values = []
        for r, distance, flow_rate in paths[room.label]:
            path_turns = turns - distance - 1
            if r in open_valves or path_turns < 0:
                continue
            # values.append((-path_turns * flow_rate, -path_turns, r, flow_rate))
            heappush(values, (-path_turns * flow_rate, -path_turns, r, flow_rate))
        if not values:
            continue
        # values.sort(reverse=True)
        value, turns, _, _ = heappop(values)
        # value, turns, _, _ = values.pop()
        value *= -1
        turns *= -1
        upper += value
        while values:
            _, _, r, flow_rate = heappop(values)
            if turns > 0:
                upper += turns * flow_rate
                turns -= 2
            else:
                break
    return upper


def heuristic(
    graph: dict[Label, dict[Label, Path]],
    rooms: dict[Label, Room],
    start: Label,
    turns: int,
    open_valves: Sequence[Label] = (),
    initial: int = 0,
) -> int:
    """Lower bound"""
    room = start
    total = initial
    visited = [*open_valves]
    upper = None
    # print("starting", room, total, "turns", turns)
    distances = {
        src: {dest: len(path) for dest, path in paths.items()}
        for src, paths in graph.items()
    }
    while True:
        values = [
            (
                (turns - distance - 1) * rooms[r].flow_rate,
                -distance,
                r,
            )
            for r, distance in distances[room].items()
            # for r, path in graph[room].items()
            if (turns - distance - 1) > 0 and r not in visited
        ]
        if values:
            value, cost, room = max(values)
            turns += cost - 1
            visited.append(room)
            total += value
            # print(f"{turns:2} {total:4} {room} | {value:4} | {upper:4}")
        else:
            break
    return total


def reconstruct_steps(rooms: dict[Label, Room], path: Sequence[Label]):
    graph = solve_reachability(rooms)

    path = list(path)
    turns = 30
    start = START
    visited = [START]
    value = 0
    lower_global = 0
    while True:
        print(visited)
        lower = heuristic(graph, rooms, start, turns, visited, value)
        upper = ubound_heuristic(graph, rooms, start, turns, visited)
        lower_global = max(lower, lower_global)
        print(lower, upper)
        if not path:
            break

        # Evaluate lower/upper bounds of potential destinations
        potential_destinations = [
            (
                destination,
                heuristic(
                    graph,
                    rooms,
                    destination,
                    turns - len(path) - 1,
                    (*visited, destination),
                    value + rooms[destination].flow_rate * (turns - len(path) - 1),
                ),
                ubound_heuristic(
                    graph,
                    rooms,
                    destination,
                    turns - len(path) - 1,
                    (*visited, destination),
                    value + rooms[destination].flow_rate * (turns - len(path) - 1),
                ),
            )
            for destination, path in graph[start].items()
            if destination not in visited
        ]
        best_lower_bound = max(
            lower_global, max(lb for _, lb, _ in potential_destinations)
        )
        for destination, lower_local, upper_local in potential_destinations:
            print(
                f"-> {destination}   {lower_local} .. {upper_local} {'*' if upper_local >= best_lower_bound else ''}"
            )

        step = path.pop(0)
        cost = len(graph[start][step]) + 1
        turns -= cost
        value += rooms[step].flow_rate * turns
        visited.append(step)
        start = step
        print()


@puzzle
def day16(input: IO[str]):
    rooms = {r.label: r for r in parse_input(input)}
    assert START in rooms

    # reconstruct_steps(rooms, ["DD", "BB", "JJ", "HH", "EE", "CC"])
    # draw_map(rooms)

    print("Part 1\n-----------------------------")
    solve(rooms, START)
    # part 1: 1880
    print("Part 2\n-----------------------------")
    solve(rooms, START, max_depth=26, two_rooms=True)


if __name__ == "__main__":
    day16.run_puzzle()
