import logger
import locator
import mapgrid
import vehicle
import plotter

import numpy as np
import time

log = logger.get_logger(__name__, level="DEBUG", disabled=False)  # Root logger


def movement_single_run():
    height = 10
    width = 10

    m = mapgrid.generate_map(width=width, height=height)
    v = vehicle.Vehicle(m, 10)

    plot = plotter.LocatorPlot(v)
    plot.plot_map()

    num_matches, x, y, possible_loc, movements = locator.locate_with_movement_and_error_fallback(m, v, 20, plot)

    if num_matches == 1:
        loc_x, loc_y, dir = v.location()
        log.info(
            "Found on location",
            x, y,
            " and its correctness is " + str((num_matches == 1) and (x == loc_x) and (y == loc_y))
        )
        log.info("Required movements:", movements)
    else:
        log.warning("Location not found!")

    plot.show()


def movement_monte_carlo():
    start_time = time.perf_counter()

    height = 10
    width = 10
    iterations = 10000
    min_moves = 9
    max_moves = 30

    success = 0
    wrong = 0
    fail = 0
    required_moves = np.zeros(max_moves+1, dtype=int)

    for i in range(iterations):
        if i % 100 == 0:
            log.debug("Running iteration", i)

        m = mapgrid.generate_map(width=width, height=height)
        v = vehicle.Vehicle(m, 10)
        num_matches, x, y, possible_loc, movements = \
            locator.locate_with_movement_and_error_fallback(m, v, max_moves, min_moves=min_moves)

        if num_matches == 1:
            correct_x, correct_y, direction = v.location()
            if x == correct_x and y == correct_y:
                success += 1
                required_moves[movements] += 1
            else:
                wrong += 1
        else:
            fail += 1

    print("Success:", success)
    print("Wrong:", wrong)
    print("Fail", fail)
    print("Required moves", required_moves)
    print("Total time", time.perf_counter() - start_time)

if __name__ == "__main__":
    # movement_single_run()
    movement_monte_carlo()
