import color
import direction

import networkx as nx
import networkx.algorithms.isomorphism as iso
import numpy as np
import typing as tp


def array_to_graph(arr: np.ndarray, periodic=True):
    """
    Convert a numpy array to a grid graph
    :param arr: numpy array
    :param periodic: whether the array edges should be connected
    :return: graph
    """
    graph = nx.grid_2d_graph(arr.shape[1], arr.shape[0], periodic=periodic)
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            graph[(x, y)]["value"] = arr[y, x]
    return graph


def map_to_digraph(map_arr: np.ndarray, periodic=True):
    """
    Convert a color map to a DiGraph
    :param map_arr: map array
    :param periodic: connect edges
    :return: DiGraph
    """
    graph = nx.DiGraph()

    # Create nodes
    for x in range(map_arr.shape[1]):
        for y in range(map_arr.shape[0]):
            graph.add_node((x, y), color=color.Color(map_arr[y, x]))

    # Create edges

    for y in range(map_arr.shape[0]-1):
        for x in range(map_arr.shape[1]):
            graph.add_edge((x, y), (x, y+1), direction=direction.Direction.SOUTH)

    for y in range(map_arr.shape[0]):
        for x in range(map_arr.shape[1]-1):
            graph.add_edge((x, y), (x+1, y), direction=direction.Direction.EAST)

    for y in range(1, map_arr.shape[0]):
        for x in range(map_arr.shape[1]):
            graph.add_edge((x, y), (x, y-1), direction=direction.Direction.NORTH)

    for y in range(map_arr.shape[0]):
        for x in range(1, map_arr.shape[1]):
            graph.add_edge((x, y), (x-1, y), direction=direction.Direction.WEST)

    if periodic:
        for x in range(map_arr.shape[1]):
            graph.add_edge((x, 0), (x, map_arr.shape[0] - 1), direction=direction.Direction.NORTH)
            graph.add_edge((x, map_arr.shape[0] - 1), (x, 0), direction=direction.Direction.SOUTH)

        for y in range(map_arr.shape[0]):
            graph.add_edge((0, y), (map_arr.shape[1] - 1, y), direction=direction.Direction.WEST)
            graph.add_edge((map_arr.shape[1] - 1, y), (0, y), direction=direction.Direction.EAST)

    return graph


def history_to_digraph(history: np.ndarray, start_direction: tp.Union[direction.Direction, int]):
    """
    Convert the history of a vehicle to a graph
    :param history: vehicle history (numpy array)
    :param start_direction: vehicle orientation (guess)
    :return: DiGraph
    """
    graph = nx.DiGraph()

    for hist_ind in range(history.shape[0]):
        graph.add_node(hist_ind, color=color.Color(history[hist_ind, 1]))

    for hist_ind in range(1, history.shape[0]):
        relative_dir = direction.RelativeDirection(history[hist_ind, 0])
        abs_dir = direction.Direction((relative_dir + start_direction) % 4)

        graph.add_edge(hist_ind-1, hist_ind, direction=abs_dir)

    return graph


def digraph_history_analyzer(history: nx.DiGraph):
    for node in history.nodes(data=True):
        print(node)

    for edge in history.edges(data=True):
        print(edge)


def color_match(node1: dict, node2: dict):
    """
    Check that the node colors match
    :param node1: node 1
    :param node2: node 2
    :return: match
    """
    return node1["color"] == node2["color"]


def direction_match(edge1: dict, edge2: dict):
    """
    Check that the edge directions match
    :param edge1: edge 1
    :param edge2: edge 2
    :return: match
    """
    return edge1["direction"] == edge2["direction"]


def graph_matcher(map: nx.DiGraph, history: nx.DiGraph):
    """
    Check whether the history can be created on the given map
    :param map: map graph
    :param history: history graph
    :return: match
    """
    dg_matcher = iso.DiGraphMatcher(map, history)
    return dg_matcher.subgraph_is_isomorphic()


if __name__ == "__main__":
    random_arr = np.random.randint(0, 4, (10, 5))
    print(random_arr)
    g = array_to_graph(random_arr)
    print(g.nodes())
    print(g.graph)

    g2 = map_to_digraph(random_arr)
    print(g2.nodes())
