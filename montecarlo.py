import numpy as np
import matplotlib.pyplot as plt
#import color
import locator
import mapgrid
import plotter
import vehicle
import typing as tp


import logger;
log = logger.getLogger(__name__, level="DEBUG", disabled=False, colors=True)

#import matplotlib.pyplot as plt


def run(gridsize:int=10, steps:int =6, MC_iterations:int=10) -> float: #
    
    numNotFound = 0
    numFound = 0
    numMultFound = 0
    
    height = gridsize
    width = gridsize
    m = mapgrid.generate_map(width=width, height=height)
    v = vehicle.Vehicle(m)

    for run_idx in range(MC_iterations):
        for i in range(steps):
            v.move_unbound()
        
        num_found, x, y = locator.locate(v.map(), v.history())
        
        
        if num_found > 1:
            numMultFound += 1
        elif num_found == 1: 
            numFound += 1
        elif num_found == 0:
            numNotFound += 1
            logger.warning("Not found!, gridsize:", gridsize, "steps", steps)
        
        
    #logger.debug("Monte Carlo run with parameters:")
    log.debug("MC RUN: gridsize:", gridsize, " steps:", steps, " MC_iterations:", MC_iterations)
    log.debug("    one match:{:7.3f}%".format(numFound/(MC_iterations)) + \
                 ",  multi-match:{:7.3f}%".format(numMultFound/(MC_iterations)) ) 
    log.debug("    one match:{:7d}".format(numFound) + ",   multi-match:{:7d}".format(numMultFound) + 
                 ",   no matches:{:7d}".format(numNotFound))
    
    return numFound/(MC_iterations)


def plot_curves_gridsizes(steps=6, iterations=1000, plot=True, use_stored_results=False) -> tp.Tuple[np.ndarray, np.ndarray]:
    gridsizes = np.arange(10,60,2)
    single_matches = np.zeros(len(gridsizes))
    
    if not use_stored_results:
        for i, gs in enumerate(gridsizes):
            log.debug("Process:", str(i)+"/"+str(len(gridsizes)), " gridsize:", gs)
            single_matches[i] = run(gs, steps, iterations)
            
        np.save("calulated_results/var_map_size__itr"+str(iterations)+".npy", single_matches)
    else:
        single_matches = np.load("calulated_results/var_map_size__itr"+str(iterations)+".npy")
    
    if plot:
        plt.figure(123)
        plt.plot(gridsizes,single_matches)
        plt.xlabel("kartan koko")
        plt.ylabel("P")
        plt.show()
    
    return gridsizes, single_matches
    
    

def log_stuff():
    log.debug("D")
    log.info("I")
    log.warning("W")
