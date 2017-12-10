import color
import direction
import logger
import vehicle

import numpy as np
import time
import typing as tp

log = logger.get_logger(__name__, level="DEBUG", disabled=False)


def locate(m: np.ndarray, history: np.ndarray, v: vehicle.Vehicle = None, skip: tp.Union[int, tp.List[int]] = None) \
        -> tp.Tuple[int, int, int, np.ndarray]:
    """
    Vehicle locator algorithm
    :param m: map (numpy array)
    :param history: vehicle history (numpy array)
    :param v: vehicle object for debugging
    :param skip: skip these indexes
    :return: number of matches, located x, located y
    """

    start_time = time.perf_counter()

    skip_list = []

    # Check the skip values
    if skip is None:
        pass
    elif type(skip) is int:
        skip_list.append(skip)
    elif type(skip) is list:
        skip_list.extend(skip)
    else:
        raise ValueError("Invalid skip input")

    for index in skip_list:
        if not 0 <= index < history.shape[0]:
            raise ValueError("Invalid skip index", index)

    # Enable debug output if the vehicle is given
    debug = (v is not None)

    if debug:
        end_x, end_y, end_dir = v.location()
    else:
        end_x = -9000
        end_y = -9000

    if debug:
        log.debug("History:")
        for y in range(history.shape[0]):
            log.debug(direction.RelativeDirection(history[y, 0]), color.Color(history[y, 1]), history[y, 2], history[y, 3])

    if (skip_list is not None) and (0 in skip_list):
        possible_start_loc = np.ones(m.shape, dtype=bool)
    else:
        possible_start_loc = np.equal(m, history[0, 1])
    possible_loc = np.zeros(m.shape, dtype=bool)

    # Iterate map
    for y in range(m.shape[0]):
        for x in range(m.shape[1]):

            # If start location is possible
            if possible_start_loc[y, x]:
                if debug:
                    log.debug("Checking start location (x, y):", x, y)

                    if x == end_x and y == end_y:
                        log.debug("----")
                        log.debug("Checking the correct location", x, y)

                # Iterate orientations
                for start_direction in range(0, 4):
                    if debug:
                        log.debug("Checking with start direction", direction.Direction(start_direction))

                        if start_direction == v.start_direction():
                            log.debug("Checking correct start direction")

                    check_x = x
                    check_y = y
                    failed = False

                    # Iterate history
                    for hist_ind in range(1, history.shape[0]):
                        relative_dir = direction.RelativeDirection(history[hist_ind, 0])
                        abs_dir = direction.Direction((relative_dir + start_direction) % 4)

                        if debug:
                            log.debug(
                                "Converting history dir",
                                hist_ind,
                                ":",
                                relative_dir,
                                "to",
                                abs_dir
                            )

                        dx, dy = abs_dir.xy()
                        check_x -= dx
                        check_y -= dy
                        check_x = check_x % m.shape[1]
                        check_y = check_y % m.shape[0]

                        # No longer a problem since the vehicle is allowed to go outside the map
                        """
                        if not (0 <= check_x < m.shape[1] and 0 <= check_y < m.shape[0]):
                            log.debug("Locator went outside the map")
                            failed = True
                            break
                        """

                        # Skip color checking if the history index is in the skip list
                        if hist_ind in skip_list:
                            if debug:
                                log.debug("Skipped history color",
                                          hist_ind,
                                          color.Color(history[hist_ind, 1]),
                                          "of",
                                          check_x,
                                          check_y,
                                          "which would correctly be",
                                          color.Color(m[check_y, check_x]))
                        # Check the color matching (the normal situation)
                        elif m[check_y, check_x] != history[hist_ind, 1]:
                            if debug:
                                log.debug(
                                    "History color",
                                    hist_ind,
                                    color.Color(history[hist_ind, 1]),
                                    "of",
                                    check_x,
                                    check_y,
                                    "didn't match to",
                                    color.Color(m[check_y, check_x])
                                )
                            failed = True
                            break

                        if debug:
                            log.debug("Color match", color.Color(m[check_x, check_y]), check_x, check_y)

                    if not failed:
                        log.debug("Found possible loc", x, y)
                        possible_loc[check_y, check_x] = True

    log.debug("Locator results:\n", possible_loc.astype(int))
    possible_y, possible_x = possible_loc.nonzero()

    num_matches = possible_y.size

    log.debug("Location took", time.perf_counter() - start_time)

    if num_matches == 0:
        log.debug("No suitable places found")
        loc_x = -9999
        loc_y = -9999
    elif num_matches == 1 and possible_x.size == 1:
        log.debug("Found location", possible_x[0], possible_y[0])
        loc_x = possible_x[0]
        loc_y = possible_y[0]
    else:
        log.debug("Multiple possible locations found")
        loc_x = -9999
        loc_y = -9999

    return num_matches, loc_x, loc_y, possible_loc


def locate_with_one_possible_error(m: np.ndarray, history: np.ndarray, v: vehicle.Vehicle = None):
    """
    Try locating when exactly one of the data points can be wrong
    :param m: map (numpy array)
    :param history: vehicle history (numpy array)
    :param v: vehicle for debugging purposes
    :return: number of possible locations, loc_x, loc_y, array of possible locations
    """
    start_time = time.perf_counter()
    possible_total_loc = np.zeros(m.shape)

    for i in range(history.shape[0]):
        num_matches, x, y, possible_loc = locate(m, history, v=v, skip=i)
        possible_total_loc = np.logical_or(possible_total_loc, possible_loc)

    log.debug("Possible locations with error handling:\n", possible_total_loc.astype(int))
    possible_y, possible_x = possible_total_loc.nonzero()
    num_matches = possible_y.size

    log.debug("Locating with error handling took", time.perf_counter() - start_time)

    if num_matches == 0:
        log.debug("No suitable places found")
        loc_x = -9999
        loc_y = -9999
    elif num_matches == 1 and possible_x.size == 1:
        log.debug("Found location", possible_x[0], possible_y[0])
        loc_x = possible_x[0]
        loc_y = possible_y[0]
    else:
        log.debug("Multiple possible locations found")
        loc_x = -9999
        loc_y = -9999

    return num_matches, loc_x, loc_y, possible_total_loc


def locate_with_error_fallback(m: np.ndarray, history: np.ndarray, v: vehicle.Vehicle = None):
    """
    Try locating with the primary algorithm and fall back to the algorithm that can handle errors if necessary
    :param m: map (numpy array)
    :param history: vehicle history (numpy array)
    :param v: vehicle for debugging purposes
    :return: number of possible locations, loc_x, loc_y, array of possible locations
    """
    num_matches, x, y, possible_loc = locate(m, history, v=v)

    if num_matches == 0:
        log.debug("No possible locations found, so the history has errors. Falling back to the error handling version.")
        num_matches, x, y, possible_loc = locate_with_one_possible_error(m, history, v=v)

    return num_matches, x, y, possible_loc


def locate_with_movement_and_error_fallback(m: np.ndarray, history_method: callable, v: vehicle.Vehicle, retries: int):
    """
    DOES NOT WORK YET. Would require the vehicle to continuously generate a history with errors.

    Try locating with the primary algorithm and fall back to the algorithm that can handle errors if necessary.
    If this doesn't help, move the vehicle.
    :param m: map (numpy array)
    :param history_method: vehicle history (numpy array)
    :param v: vehicle for debugging purposes
    :param retries: how many times the vehicle should be moved and relocated if the previous attempts fail
    :return: number of possible locations, loc_x, loc_y, array of possible locations
    """
    if not retries > 1:
        raise ValueError("Invalid retry count")

    num_matches, x, y, possible_loc = locate_with_error_fallback(m, history_method())

    movement_count = 0
    for movement_count in range(retries+1):
        if num_matches == 1:
            break
        else:
            log.debug("Locating did not succeed. Moving the vehicle.")
            v.move_unbound()
        num_matches, x, y, possible_loc = locate_with_error_fallback(m, history_method)

    return num_matches, x, y, possible_loc, movement_count
