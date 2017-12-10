"""
This file contains all Monte Carlo simulation calculation functions.
"""
import numpy as np
import matplotlib.pyplot as plt
import os

import locator
import mapgrid
import plotter
import vehicle
import typing as tp


import logger
log = logger.get_logger(__name__, level="DEBUG", disabled=False, colors=True)

# import matplotlib.pyplot as plt


def run_MC(gridsize: int, steps: int, MC_iterations: int, error=False) -> np.ndarray:
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
            num_found, x, y = locator.locate(v.map(), v.history_error(iteration_for_seed=run_idx))[0:3]
        else:
            num_found, x, y = locator.locate(v.map(), v.history())[0:3]
            
        if num_found == 1:
            loc_x, loc_y, dir = v.location()
            if ((x == loc_x) and (y == loc_y)):
                numFound_correct += 1
            else:
                numFound_incorrect += 1
        elif num_found == 0:
            numNotFound += 1
            if not error:
                log.warning("Not found!, gridsize:", gridsize, "steps", steps, "error", error)
        
        
    log.debug("    correct match:{:7.3f}".format(numFound_correct/(MC_iterations)) + \
              ",  incorrect match:{:7.3f}".format(numFound_incorrect/(MC_iterations)) ) 
    
    return np.array((numFound_correct/MC_iterations, numFound_incorrect/MC_iterations, numNotFound/MC_iterations))



def run_MC_2(gridsize: int, steps: int, MC_iterations: int, error=0.001) -> np.ndarray:
    """
    Does Monte Carlo-simulation with given parametes.
    Sensitivity and specificity, confusion 4-matrix,
    
    return 2*2*2 np.ndarray, in which [0,:,:] is mean values and [1,:,:] is error
    """
    
    # all confusion matrices (like ...0100,0010...)
    results_mat = np.zeros((MC_iterations, 2, 2), dtype=int)
    
    height = gridsize
    width = gridsize
    
    # Runs simulation in loop
    for run_idx in range(MC_iterations):
        m = mapgrid.generate_map(width=width, height=height)
        v = vehicle.Vehicle(m)
        for i in range(steps):
            v.move_unbound()
        

        num_found_exact, x, y    = locator.locate(v.map(), v.history_error(iteration_for_seed=run_idx, error=error))[0:3]
        num_found_inextact, x, y = locator.locate(v.map(), v.history())[0:3]
        
        true_pos = 0
        true_neg = 0
        false_pos = 0
        false_neg = 0
        
        if (num_found_exact == 1) and (num_found_inextact == 1):
            true_pos += 1
        elif (num_found_exact != 1) and (num_found_inextact != 1):
            true_neg += 1
        elif (num_found_exact == 1) and (num_found_inextact != 1):
            false_neg += 1
        elif (num_found_exact != 1) and (num_found_inextact == 1):
            false_pos += 1
        
        confusion_mat = np.array(((true_pos, false_neg), (false_pos, true_neg)))
        results_mat[run_idx,:,:] = confusion_mat
    
    #confusion mat
    mean_mat = np.mean(results_mat, axis=0)
    err_mat = np.std(results_mat,axis=0) / np.sqrt(MC_iterations)
    
    return np.array((mean_mat, err_mat))



def calc_confusion_mat(gridsize=-1, steps=10, iterations=1000, dirname="Unnamed", use_stored_results=False, var_error=False):
    """
    Calulates the confusion matrices (and errorbars) for given arguments.
    Varites either gridsize or steps or error
    IF gridsize is -1 then variate gridsize over a range
    IF steps is -1 then variate that
    IF var_error the variate error
    
    in a nutchell: this function calls 'run_MC_2()' iteratively
    
    return
        x_axis      values for variating value   
        res_vec     mean and errors of confusion mat, see below
    """
    # res_vec (result vector) dimensions: 
    #       0: variating value, ~10-20
    #       1: mean and std-error 0, 1
    #       2: positive, negative (measurement error)
    #       3: true, false (no measurement error)
    res_vec = None  # np.empty((10,2,2,2))
    x_axis = None  #gridsizes, or steps
    
    dir_base = "calulated_results/"+dirname+"__itr"+str(iterations)
    create_directory_if_it_doesnt_exist_already(dir_base)
    filename = dir_base+"/gs"+str(gridsize)+"_st"+str(steps)+".npy"
    
    if not use_stored_results:
        
        log.debug("Number of Monte Carlo iterations with every calulation: "+ str(iterations))

        if gridsize == -1:
            gridsize_vec = np.arange(10,60,5)
            x_axis = gridsize_vec
            res_vec = np.zeros((len(gridsize_vec),2,2,2))
            
            for i, gs in enumerate(gridsize_vec):
                res_vec[i,:,:,:] = run_MC_2(gs, steps, iterations)
                log.debug("    Process:", str(i+1)+"/"+str(len(gridsize_vec)), " gridsize:", gs)
            

        elif steps == -1:
            steps_vec = np.arange(1,10+1)
            x_axis = steps_vec
            res_vec = np.zeros((len(steps_vec),2,2,2))
            
            for i, st in enumerate(steps_vec):
                res_vec[i,:,:,:] = run_MC_2(gridsize, steps, iterations)
                log.debug("    Process:", str(i+1)+"/"+str(len(steps_vec)), " steps", st)
        
        elif var_error:
            err_vec = np.logspace(-4,0,10)
            x_axis = err_vec
            res_vec = np.zeros((len(err_vec),2,2,2))
            
            for i, er in enumerate(err_vec):
                res_vec[i,:,:,:] = run_MC_2(gridsize, steps, iterations, error=er)
                log.debug("    Process:", str(i+1)+"/"+str(len(err_vec)), " error", er)
        else:
            raise Exception("You have to variate gridsize or steps, set that value to -1 to do that")
        
        
        np.save(filename, res_vec)
                
    # get pre calculated data
    else:
        if gridsize == -1:
            x_axis = np.arange(10,60,5)
        elif steps == -1:
            x_axis = np.arange(1,10+1)
        elif var_error:
            x_axis = np.logspace(-4,0,10)
        else:
            raise Exception("You have to variate gridsize or steps, set that value to -1 to do that")
        
        if not os.path.isfile(filename):
            raise Exception("No calulations exists (yet) with these parameters")
        
        res_vec = np.load(filename)
    
    return x_axis, res_vec


def calc_TPR_TNR_ACC(res_vec, iterations):
    """
    Calulates the TPR TNR ACC
    """
    
    TP = res_vec[:,0,0,0] * iterations
    FN = res_vec[:,0,1,0] * iterations
    FP = res_vec[:,0,0,1] * iterations
    TN = res_vec[:,0,1,1] * iterations

    TP_err = res_vec[:,1,0,0] * iterations
    FN_err = res_vec[:,1,1,0] * iterations
    FP_err = res_vec[:,1,0,1] * iterations
    TN_err = res_vec[:,1,1,1] * iterations
    
    TPR = TP / (TP+FN)
    # SPC is it same as TNR?
    TNR = TN / (TN + FP)
    ACC = (TP + TN) / (TP + FN + TN + FP)

    return TPR, TNR, ACC



def create_directory_if_it_doesnt_exist_already(directory:str):
    if not os.path.exists(directory):
        os.makedirs(directory)



def plot_classification_and_erros(iterations=1000, use_stored_results=False, map_steps_err=[True, True, True]):
    """
    Confusion matrix calulations and plots, "herkkyysanalyysi" in english.
    """
    # map
    if map_steps_err[0]:
        x_axis_map, var_map = calc_confusion_mat(
                gridsize=-1, steps=10, iterations=iterations, dirname="variate_map", use_stored_results=use_stored_results)
        
        plotter.plot_conf_mat(x_axis_map, var_map, xlabel="kartan koko")#, ylim=(0,1))
        
        TPR_gs, TNR_gs, AAC_gs = calc_TPR_TNR_ACC(var_map, iterations)
        plotter.plot_TPR_TNR_ACC(x_axis_map, TPR_gs, TNR_gs, AAC_gs, xlabel="kartan koko", ylim=None)
        
    # steps
    if map_steps_err[1]:
        x_axis_steps, var_steps = calc_confusion_mat(
                gridsize=20, steps=-1, iterations=iterations, dirname="variate_steps", use_stored_results=use_stored_results)
        
        plotter.plot_conf_mat(x_axis_steps, var_steps, xlabel="askelten lukumäärä")#, ylim=(0,1))
        
        TPR_st, TNR_st, AAC_st = calc_TPR_TNR_ACC(var_steps, iterations)
        plotter.plot_TPR_TNR_ACC(x_axis_steps, TPR_st, TNR_st, AAC_st, xlabel="askelten lukumäärä", ylim=None)
        
    if map_steps_err[2]:
        x_axis_err, var_err = calc_confusion_mat(
                gridsize=20, steps=10, iterations=iterations, dirname="variate_error", use_stored_results=use_stored_results, var_error=True)
        plotter.plot_conf_mat(x_axis_err, var_err, xlabel="havaintovirhe", log_scale=True)
        
        TPR_er, TNR_er, AAC_er = calc_TPR_TNR_ACC(var_err, iterations)
        plotter.plot_TPR_TNR_ACC(x_axis_err, TPR_er, TNR_er, AAC_er, xlabel="havaintovirhe", ylim=None, log_scale=True)
    
    
    
    plt.show()
    
def single_four_table(iterations=1000):
    """
    Confusion matrix things, single calculation, print values
    """
    
    mat = run_MC_2(20, 10, iterations)
    
    mean = mat[0,:,:]
    err = mat[1,:,:]
    
    # lazy latex table
    for i in [0,1]:
        for j in [0,1]:
            m = str(mean[i,j])
            e = str(err[i,j])
            print("${} \pm {}$".format(m, e), end="")
            
            if j != 1:
                print(" & ", end="")
            else:
                print(" \\\\")
    
    TP = mat[0,0,0]
    FN = mat[0,1,0]
    FP = mat[0,0,1]
    TN = mat[0,1,1]
    
    TPR = TP / (TP+FN)
    # SPC is it same as TNR?
    TNR = TN / (TN + FP)
    ACC = (TP + TN) / (TP + FN + TN + FP)
    
    print("TPR", TPR, "TNR", TNR, "ACC", ACC)
    
    # TP_mean = mat[0,0,0]
    # FN_mean = mat[0,1,0]
    # FP_mean = mat[0,0,1]
    # TN_mean = mat[0,1,1]
    
    # TP_err = mat[1,0,0]
    # FN_err = mat[1,1,0]
    # FP_err = mat[1,0,1]
    # TN_err = mat[1,1,1]




























# These are old functions and not used anymore. They work well, so they are not removed.

def plot_monte_carlos(num_runs=20, iterations=1000, use_stored_results=[True,True]):
    
    # first with no error

    gridsizes_0, Prob_MC_matrix_gs_0 = calc_curves_gridsizes(steps=10, 
                                                                        num_runs=num_runs, 
                                                                        iterations=iterations, 
                                                                        use_stored_results=use_stored_results[0],
                                                                        error=False)

    steps_0, Prob_MC_matrix_st_0 = calc_curves_steps(gridsize=20, 
                                                                num_runs=num_runs, 
                                                                iterations=iterations, 
                                                                use_stored_results=use_stored_results[0], 
                                                                error=False)
                                                                
    
    # then with 0.001 error in measurement of color
    gridsizes_1, Prob_MC_matrix_gs_1 = calc_curves_gridsizes(steps=10, 
                                                                        num_runs=num_runs, 
                                                                        iterations=iterations, 
                                                                        use_stored_results=use_stored_results[1], 
                                                                        error=True)
    steps_1, Prob_MC_matrix_st_1 = calc_curves_steps(gridsize=20, 
                                                                num_runs=num_runs, 
                                                                iterations=iterations, 
                                                                use_stored_results=use_stored_results[1], 
                                                                error=True)
    
    plotter.plot_gridsizes_error(gridsizes_0, Prob_MC_matrix_gs_0, gridsizes_1, Prob_MC_matrix_gs_1, num_runs)
    plotter.plot_steps_error(steps_0, Prob_MC_matrix_st_0, steps_1, Prob_MC_matrix_st_1, num_runs)
    
    plt.show()


def calc_curves_gridsizes(steps=10, num_runs=10, iterations=1000, plot=True, use_stored_results=False, error=False) \
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



def calc_curves_steps(gridsize=20, num_runs=10, iterations=1000, plot=True, use_stored_results=False, error=False) \
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
    
    
    
