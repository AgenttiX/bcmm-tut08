import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from matplotlib2tikz import save as tikz_save
#import color
import locator
import mapgrid
import plotter
import vehicle
import typing as tp


import logger;
log = logger.getLogger(__name__, level="DEBUG", disabled=False, colors=True)

#import matplotlib.pyplot as plt


def run_MC(gridsize:int, steps:int, MC_iterations:int) -> float:
    """
    Does Monte Carlo-simulation with given parametes.
    """
    
    numNotFound = 0
    numFound = 0
    numMultFound = 0
    
    height = gridsize
    width = gridsize
    m = mapgrid.generate_map(width=width, height=height)
    v = vehicle.Vehicle(m)
    
    # Runs simulation in loop
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
    #log.debug("MC RUN: gridsize:", gridsize, " steps:", steps, " MC_iterations:", MC_iterations)
    log.debug("    one match:{:7.3f}%".format(numFound/(MC_iterations)) + \
                 ",  multi-match:{:7.3f}%".format(numMultFound/(MC_iterations)) ) 
    #log.debug("    one match:{:7d}".format(numFound) + ",   multi-match:{:7d}".format(numMultFound) + 
    #             ",   no matches:{:7d}".format(numNotFound))
    
    return numFound/(MC_iterations)



def plot_curves_gridsizes(steps=10, num_runs=10, iterations=1000, plot=True, use_stored_results=False) \
    -> tp.Tuple[np.ndarray, np.ndarray]:
    """
    Does multiple Monte Carlo simulations with different values for gridsize. 
    Repeats every simulation num_runs times to get a standard error in simulation.
    Also plots probabilities to find location in function of maps size.
    
    Calculations are stored, and they can be used instead of calulating everything again. 
    Parameters (steps,iterations) must match.
    """
    gridsizes = np.arange(10,60,5)
    single_matches = np.zeros((num_runs, len(gridsizes)))

    
    if not use_stored_results:
        log.debug("\nRunning Monte Carlo with different gridsizes. There are "+
                  str(num_runs)+"*"+str(iterations)+" iterations, it may take a while.")
        
        for run_idx in range(num_runs):
            log.debug("\nRun", run_idx, "out of", num_runs)
            for i, gs in enumerate(gridsizes):
                log.debug("Process:", str(i)+"/"+str(len(gridsizes)-1), " gridsize:", gs)
                
                single_matches[run_idx,i] = run_MC(gs, steps, iterations)
                
            np.save("calulated_results/var_map_size__itr"+str(iterations)+"st"+str(steps)+"_idx"+str(run_idx)+".npy", single_matches[run_idx,:])
    # get pre calculated data
    else:
        for run_idx in range(num_runs):
            single_matches[run_idx,:] = np.load("calulated_results/var_map_size__itr"+str(iterations)+"st"+str(steps)+"_idx"+str(run_idx)+".npy")
    
    if plot:
        mean_vec = np.mean(single_matches, axis=0)
        err_vec = np.std(single_matches, axis=0)
        
        plt.figure(123)
        plt.errorbar(gridsizes, mean_vec, yerr=err_vec, capsize=5)
        plt.xlabel("kartan koko")
        plt.ylabel("P")
        
        block_print()
        tikz_save('figures/gridsizes.tikz')
        enable_print()
        
    
    return gridsizes, single_matches



def plot_curves_steps(gridsize=20, num_runs=10, iterations=1000, plot=True, use_stored_results=False) \
    -> tp.Tuple[np.ndarray, np.ndarray]:
    """
    Does multiple Monte Carlo simulations with different values for steps. 
    Repeats every simulation num_runs times to get a standard error in simulation.
    Also plots probabilities to find location in function of steps.
    
    Calculations are stored, and they can be used instead of calulating everything again. 
    Parameters (gridsize,iterations) must match.
    """
    
    steps = np.arange(3,10+1)
    single_matches = np.zeros((num_runs, len(steps)))
    
    # Run or get the pre-calculated data
    if not use_stored_results:
        log.debug("\nRunning Monte Carlo with different number of steps. There are "+
                  str(num_runs)+"*"+str(iterations)+" iterations, it may take a while.")
        
        for run_idx in range(num_runs):
            log.debug("\nRun", run_idx, "out of", num_runs)
            for i, st in enumerate(steps):
                log.debug("    Process:", str(i)+"/"+str(len(steps)-1), " steps:", st)
                
                single_matches[run_idx,i] = run_MC(gridsize, st, iterations)
                
            np.save("calulated_results/var_steps__itr"+str(iterations)+"gs"+str(gridsize)+"_idx"+str(run_idx)+".npy", single_matches[run_idx,:])
    # get pre calculated data
    else:
        for run_idx in range(num_runs):
            single_matches[run_idx,:] = np.load("calulated_results/var_steps__itr"+str(iterations)+"gs"+str(gridsize)+"_idx"+str(run_idx)+".npy")
    
    if plot:
        mean_vec = np.mean(single_matches, axis=0)
        err_vec = np.std(single_matches, axis=0)
                
        plt.figure(124)
        plt.errorbar(steps, mean_vec, yerr=err_vec, capsize=5)
        plt.xlabel("askelten lukumäärä")
        plt.ylabel("P")
        
        block_print()
        tikz_save('figures/steps.tikz')
        enable_print()

        
    
    return steps, single_matches



def block_print(): 
    sys.stdout = open(os.devnull, 'w')


    
def enable_print():
    sys.stdout = sys.__stdout__



def log_stuff():
    log.debug("D")
    log.info("I")
    log.warning("W")
