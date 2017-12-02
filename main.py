import color
import locator
import mapgrid
import plotter
import vehicle

import logger
import montecarlo

log = logger.getLogger(__name__, level="DEBUG", disabled=False)  # Root logger


def plot_single_run():
    height = 10
    width = 10

    m = mapgrid.generate_map(width=width, height=height)
    v = vehicle.Vehicle(m)

    plot = plotter.LocatorPlot(v)
    plot.plot_map()

    # The placement of the vehicle need not be shown
    # plot.plot_vehicle()

    log.info("Start location:", str(v.location()))
    log.info("Start color:", v.color())

    for i in range(6):
        v.move_unbound()
        plot.plot_vehicle()

    # found, x, y = locator.locate(v.map(), v.history(), v)
    found, x, y = locator.locate(v.map(), v.history())

    log.info("End location:", v.location())
    log.info("End color:", v.color())
    if found==0:
        log.info("Found on location", x, y)
    else:
        log.warning("Location not found!")
    
    plot.show()


def main():
    plot_single_run()
    
    montecarlo.plot_curves_gridsizes(steps=10, iterations=1000, plot=True, use_stored_results=True)
    
main()


