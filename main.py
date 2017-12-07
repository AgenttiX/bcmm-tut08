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
    num_matches, x, y = locator.locate(v.map(), v.history())
    


    log.info("End location:", v.location())
    log.info("End color:", v.color())
    if num_matches == 1:
        loc_x, loc_y, dir = v.location()
        log.info("Found on location", x, y, " and it is "+str((num_matches==1) and (x==loc_x) and (y==loc_y)))
    else:
        log.warning("Location not found!")
    
    plot.show()


def plot_monte_carlos(num_runs=20, iterations=1000, use_stored_results=[True,True]):
    
    # first with no error

    gridsizes_0, Prob_MC_matrix_gs_0 = montecarlo.plot_curves_gridsizes(steps=10, 
                                                                        num_runs=num_runs, 
                                                                        iterations=iterations, 
                                                                        use_stored_results=use_stored_results[0],
                                                                        error=False)

    steps_0, Prob_MC_matrix_st_0 = montecarlo.plot_curves_steps(gridsize=20, 
                                                                num_runs=num_runs, 
                                                                iterations=iterations, 
                                                                use_stored_results=use_stored_results[0], 
                                                                error=False)
                                                                
    
    # then with 0.001 error in measurement of color
    gridsizes_1, Prob_MC_matrix_gs_1 = montecarlo.plot_curves_gridsizes(steps=10, 
                                                                        num_runs=num_runs, 
                                                                        iterations=iterations, 
                                                                        use_stored_results=use_stored_results[1], 
                                                                        error=True)
    steps_1, Prob_MC_matrix_st_1 = montecarlo.plot_curves_steps(gridsize=20, 
                                                                num_runs=num_runs, 
                                                                iterations=iterations, 
                                                                use_stored_results=use_stored_results[1], 
                                                                error=True)
    
    plotter.plot_gridsizes_error(gridsizes_0, Prob_MC_matrix_gs_0, gridsizes_1, Prob_MC_matrix_gs_1, num_runs)
    plotter.plot_steps_error(steps_0, Prob_MC_matrix_st_0, steps_1, Prob_MC_matrix_st_1, num_runs)
    
    plt.show()

def main():
    #plot_single_run()
    plot_monte_carlos(num_runs=10, iterations=3000, use_stored_results=[True, True])
    #montecarlo.log_stuff()
    #montecarlo.debug_my_stuff()
    

    
main()
#plot_single_run()

