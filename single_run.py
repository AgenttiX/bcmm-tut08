# import direction
# import graph_utils
import logger
import locator
import mapgrid
import vehicle
import plotter

log = logger.get_logger(__name__, level="DEBUG", disabled=False)  # Root logger


def plot_single_run():
    height = 10
    width = 10

    m = mapgrid.generate_map(width=width, height=height)
    v = vehicle.Vehicle(m, 10)

    plot = plotter.LocatorPlot(v)
    plot.plot_map()

    # The placement of the vehicle need not be shown
    # plot.plot_vehicle()

    log.info("Start location:", str(v.location()))
    log.info("Start color:", v.color())

    for i in range(10):
        v.move_unbound()
        plot.plot_vehicle()

    # found, x, y = locator.locate(v.map(), v.history(), v)
    num_matches, x, y, possible_loc = locator.locate(v.map(), v.history())

    log.info("End location:", v.location())
    log.info("End color:", v.color())

    if num_matches == 1:
        loc_x, loc_y, dir = v.location()
        log.info(
            "Found on location",
            x, y,
            " and its correctness is " + str((num_matches == 1) and (x == loc_x) and (y == loc_y))
        )
    else:
        log.warning("Location not found!")

    # Graph testing
    """
    history_graphs = []
    for i in range(4):
        history_graph = graph_utils.history_to_digraph(v.history(), i)
        history_graphs.append(history_graph)

        graph_utils.digraph_history_analyzer(history_graph)

    map_graph = graph_utils.map_to_digraph(m)

    for i in range(4):
        match = graph_utils.graph_matcher(map_graph, history_graphs[i])
        print("Start direction", direction.Direction(i), "graph match:", match)
    """

    # History error handling test
    locator.locate_with_one_possible_error(v.map(), v.history())
    locator.locate_with_one_possible_error(v.map(), v.history_error_one())

    plot.show()


if __name__ == "__main__":
    plot_single_run()
