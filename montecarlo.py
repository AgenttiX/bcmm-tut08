import numpy as np
import matplotlib.pyplot as plt
import os

import locator
import mapgrid
import plotter
import vehicle
import typing as tp


import logger
log = logger.getLogger(__name__, level="DEBUG", disabled=False, colors=True)

#import matplotlib.pyplot as plt


def run_MC(gridsize:int, steps:int, MC_iterations:int, error=False) -> float:
    """
    Does Monte Carlo-simulation with given parametes.
    """
    
    numFound_correct = 0
    numFound_incorrect = 0
    numNotFound = 0
    
    height = gridsize
    width = gridsize
    
    # Runs simulation in loop
    for run_idx in range(MC_iterations):
        m = mapgrid.generate_map(width=width, height=height)
        v = vehicle.Vehicle(m)
        for i in range(steps):
            v.move_unbound()
        
        if error:
            num_found, x, y = locator.locate(v.map(), v.history_error(iteration_for_seed=run_idx))
        else:
            num_found, x, y = locator.locate(v.map(), v.history())
            
        if num_found == 1:
            loc_x, loc_y, dir = v.location()
            if ((x==loc_x) and (y==loc_y)):
                numFound_correct += 1
            else:
                numFound_incorrect += 1
        elif num_found == 0:
            numNotFound += 1
            if not error:
                log.warning("Not found!, gridsize:", gridsize, "steps", steps, "error", error)
        
        
    log.debug("    correct match:{:7.3f}".format(numFound_correct/(MC_iterations)) + \
                 ",  incorrect match:{:7.3f}".format(numFound_incorrect/(MC_iterations)) ) 
    
    return np.array((numFound_correct/MC_iterations, numFound_incorrect/MC_iterations, numNotFound/MC_iterations ))



def plot_curves_gridsizes(steps=10, num_runs=10, iterations=1000, plot=True, use_stored_results=False, error=False) \
    -> tp.Tuple[np.ndarray, np.ndarray]:
    """
    Does multiple Monte Carlo simulations with different values for gridsize. 
    Repeats every simulation num_runs times to get a standard error in simulation.
    //Also plots probabilities to find location in function of maps size.
    
    Calculations are stored, and they can be used instead of calulating everything again. 
    Parameters (steps,iterations) must match.
    """
    gridsizes = np.arange(10,60,5)
    # precentages [0-1] of single matches so that location is corrent / incorrect
        # zeroth dimension ~ 10 repeated MC_runs
        # first dimension variating values
        # second dimension: corrent / incorrect / not-found-at-all
    found_one = np.zeros((num_runs, len(gridsizes), 3))

    
    if not use_stored_results:
        log.debug("\nRunning Monte Carlo with different gridsizes. There are "+
                  str(num_runs)+"*"+str(iterations)+" iterations, it may take a while.")
        
        for run_idx in range(num_runs):
            log.debug("\nRun", run_idx+1, "out of", num_runs)
            for i, gs in enumerate(gridsizes):
                log.debug("Process:", str(i)+"/"+str(len(gridsizes)-1), " gridsize:", gs)
                
                found_one[run_idx,i,:]= run_MC(gs, steps, iterations, error=error)
            
            dir = "calulated_results/var_map_size__itr"+str(iterations)+"_st"+str(steps)+"_err"+str(int(error))
            create_directory_if_it_doesnt_exist_already(dir)
            np.save(dir+"/idx"+str(run_idx)+".npy", found_one[run_idx,:,:])
    # get pre calculated data
    else:
        dir = "calulated_results/var_map_size__itr"+str(iterations)+"_st"+str(steps)+"_err"+str(int(error))
        if not os.path.exists(dir):
            raise Exception("No calulations exists (yet) with these parameters")
        
        for run_idx in range(num_runs):
            found_one[run_idx,:,:] = np.load(dir+"/idx"+str(run_idx)+".npy")
    
    
    return gridsizes, found_one



def plot_curves_steps(gridsize=20, num_runs=10, iterations=1000, plot=True, use_stored_results=False, error=False) \
    -> tp.Tuple[np.ndarray, np.ndarray]:
    """
    Does multiple Monte Carlo simulations with different values for steps. 
    Repeats every simulation num_runs times to get a standard error in simulation.
    //Also plots probabilities to find location in function of steps.
    
    Calculations are stored, and they can be used instead of calulating everything again. 
    Parameters (gridsize,iterations) must match.
    """
    
    steps = np.arange(1,10+1)
    
    # precentages [0-1] of single matches so that location is corrent / incorrect
        # zeroth dimension ~ 10 repeated MC_runs
        # first dimension variating values
        # second dimension: corrent / incorrect / not-found-at-all
    found_one = np.zeros((num_runs, len(steps), 3))
    
    # Run or get the pre-calculated data
    if not use_stored_results:
        log.debug("\nRunning Monte Carlo with different number of steps. There are "+
                  str(num_runs)+"*"+str(iterations)+" iterations, it may take a while.")
        
        for run_idx in range(num_runs):
            log.debug("\nRun", run_idx+1, "out of", num_runs)
            for i, st in enumerate(steps):
                log.debug("    Process:", str(i)+"/"+str(len(steps)-1), " steps:", st)
                
                found_one[run_idx,i,:] = run_MC(gridsize, st, iterations, error=error)
            
            dir = "calulated_results/var_steps__itr"+str(iterations)+"_gs"+str(gridsize)+"_err"+str(int(error))
            create_directory_if_it_doesnt_exist_already(dir)
            np.save(dir+"/idx"+str(run_idx)+".npy", found_one[run_idx,:,:])
    # get pre calculated data
    else:
        dir = "calulated_results/var_steps__itr"+str(iterations)+"_gs"+str(gridsize)+"_err"+str(int(error))
        if not os.path.exists(dir):
            raise Exception("No calulations exists (yet) with these parameters, change to 'use_stored_results=[False, False]'")
        
        for run_idx in range(num_runs):
            found_one[run_idx,:,:] = np.load(dir+"/idx"+str(run_idx)+".npy")
    
    return steps, found_one


def create_directory_if_it_doesnt_exist_already(directory:str):
    if not os.path.exists(directory):
        os.makedirs(directory)


def log_stuff():
    print("printing is not good")
    log.debug("D")
    log.info("I")
    log.warning("W")
    log.error("E")
    log.critical("C")

def debug_my_stuff():
    run_MC(gridsize=20, steps=10, MC_iterations=1000, error=True)
    """
    for itr in range(1000):
        l = 7
        
        vec=np.random.randint(3, size=l)
        
        np.random.seed(2**16+itr) #np.mod(int(id(self)), 2**16)) # seed can not be too large (memory address) :P
        rnd_colors = np.random.randint(3, size=10) # Note error can not be same color (so therefore 0,1,2)
        rnd_prob = (np.random.random(10) < 0.001).astype(int) # vector [0,0,...0,1,0,..0]
        np.random.seed(None)
        
        # altered_history
        vec = np.mod(vec + (rnd_colors*rnd_prob)[0 : l], 4)
        if np.sum(rnd_prob) > 0 :
            print("REMOVE vec", vec, "rnd_prob", rnd_prob)
    """
    
    
    
