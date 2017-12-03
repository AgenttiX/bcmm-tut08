import matplotlib.pyplot as plt

import color
import locator
import mapgrid
import plotter
import vehicle
import logger
log = logger.getLogger(__name__, level="DEBUG", disabled=False)  # Root logger
import montecarlo


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
    if found == 1:
        log.info("Found on location", x, y)
    else:
        log.warning("Location not found!")
    
    plot.show()


def main():
    plot_single_run()
    
    montecarlo.plot_curves_gridsizes(steps=10, num_runs=10, iterations=200, use_stored_results=True)
    
    montecarlo.plot_curves_steps(gridsize=20, num_runs=10, iterations=1000, use_stored_results=True)
        
    plt.show()
    
# main()
plot_single_run()

