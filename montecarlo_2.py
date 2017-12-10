"""
Orginal Monte Carlo file got bloated and this file contains only calculations of error analysis
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


def run_MC_3(gridsize: int, steps: int, MC_iterations: int, error=0.001) -> np.ndarray:
    """
    Does Monte Carlo-simulation with given parametes.
    Meant fo error correction and error analysis
    
    This time this function returns full array of results, so that can be used again
    
    return 
        results_mat (N*2*2 np.ndarray)   in which [n,:,:] one confusion 4-matrix of single MC_simulation n
        error_info   
            #   0: number of found locations without error, 
            #   1: number of found locations with error, 
            #   2: if two both of those are equal to 1, 
            #           1 if the answer in error is correct, 0 else
        results_mat_corr with error correction
    """
    
    # all confusion matrices (like ...0100,0010...)
    results_mat = np.zeros((MC_iterations, 2, 2), dtype=int)
    
    error_info = np.zeros((MC_iterations, 3), dtype=int) 
    
    results_mat_corr = np.zeros((MC_iterations, 2, 2), dtype=int)
            
    
    height = gridsize
    width = gridsize
    
    # Runs simulation in loop
    for run_idx in range(MC_iterations):
        m = mapgrid.generate_map(width=width, height=height)
        v = vehicle.Vehicle(m)
        for i in range(steps):
            v.move_unbound()
        
        
        err_hist = v.history_error(iteration_for_seed=run_idx, error=error)
        
        num_found_exact, x_ext, y_ext = locator.locate(v.map(), v.history())[0:3]
        num_found_inexact, x_err, y_err = locator.locate(v.map(), err_hist)[0:3]
        num_found_corrected, x_corr, y_corr = locator.locate_with_error_fallback(v.map(), err_hist)[0:3]
        
        true_pos = 0
        true_neg = 0
        false_pos = 0
        false_neg = 0
        
        true_pos_corr = 0
        true_neg_corr = 0
        false_pos_corr = 0
        false_neg_corr = 0
        
        error_info[run_idx, 0] = num_found_exact
        error_info[run_idx, 1] = num_found_inexact
        
        if (num_found_exact == 1) and (num_found_inexact == 1):
            true_pos += 1
            if not (x_err == x_ext) and (y_err == y_ext):
                error_info[run_idx, 2] = 1
                log.debug("Incorrect TP! args:", gridsize,steps,error)
                
        elif (num_found_exact != 1) and (num_found_inexact != 1):
            true_neg += 1
        elif (num_found_exact == 1) and (num_found_inexact != 1):
            false_neg += 1
        elif (num_found_exact != 1) and (num_found_inexact == 1):
            false_pos += 1
        
        # corrected
        if (num_found_exact == 1) and (num_found_corrected == 1):
            true_pos_corr += 1
        elif (num_found_exact != 1) and (num_found_corrected != 1):
            true_neg_corr += 1
        elif (num_found_exact == 1) and (num_found_corrected != 1):
            false_neg_corr += 1
        elif (num_found_exact != 1) and (num_found_corrected == 1):
            false_pos_corr += 1
        
        confusion_mat = np.array(((true_pos, false_neg), (false_pos, true_neg)))
        results_mat[run_idx,:,:] = confusion_mat
        
        conf_mat_corr = np.array(((true_pos_corr, false_neg_corr), (false_pos_corr, true_neg_corr)))
        results_mat_corr[run_idx,:,:] = confusion_mat

    return results_mat, error_info, results_mat_corr



def run_MC_4(gridsize: int, steps: int, MC_iterations: int, error=0.001) -> np.ndarray:
    """
    Yet another way to run calculations. This time thi just returns all values
    """
    # num found vector for every simulation in MC
    num_found_exact    = np.zeros((MC_iterations), dtype=int)
    num_found_inexact   = np.zeros((MC_iterations), dtype=int)
    num_found_corrected = np.zeros((MC_iterations), dtype=int)
    num_found_corrected_move = np.zeros((MC_iterations), dtype=int)
    
    # if TP then if location correct
    found_correct_exact    = np.zeros((MC_iterations), dtype=int)
    found_correct_inexact   = np.zeros((MC_iterations), dtype=int)
    found_correct_corrected = np.zeros((MC_iterations), dtype=int)
    found_correct_corrected_move = np.zeros((MC_iterations), dtype=int)
    
    
    
    
    min_moves = 9
    max_moves = 30
    required_moves = np.zeros(max_moves+1, dtype=int)

                
    
    height = gridsize
    width = gridsize
    
    # Runs simulation in loop
    for run_idx in range(MC_iterations):
        m = mapgrid.generate_map(width=width, height=height)
        v = vehicle.Vehicle(m)
        for i in range(steps):
            v.move_unbound()
        
        
        err_hist = v.history_error(iteration_for_seed=run_idx, error=error)
        
        num_found_exact[run_idx], x_ext, y_ext = locator.locate(v.map(), v.history())[0:3]
        num_found_inexact[run_idx], x_err, y_err = locator.locate(v.map(), err_hist)[0:3]
        num_found_corrected[run_idx], x_corr, y_corr = locator.locate_with_error_fallback(v.map(), err_hist)[0:3]
        
        if num_found_exact[run_idx] == 1:
            found_correct_exact[run_idx] = 1
            
            if x_err == x_ext and y_err == y_ext:
                found_correct_inexact[run_idx] = 1
        
        if num_found_inexact[run_idx] == 1:
            if x_corr == x_ext and y_corr == y_ext:
                found_correct_corrected[run_idx] = 1
    
        if num_found_corrected[run_idx] == 1:
            if x_err == x_ext and y_err == y_ext:
                found_correct_inexact[run_idx] = 1
    
    
        # now the moving error correction from 'movement.py'
        
        v2 = vehicle.Vehicle(m, 10, error=error)
        num_found_corrected_move[run_idx], x_mov, y_mov, possible_loc, movements = \
            locator.locate_with_movement_and_error_fallback(m, v2, max_moves, min_moves=min_moves)

        if num_found_corrected_move[run_idx] == 1:
            correct_x, correct_y, direction = v2.location()
            if x_mov == correct_x and y_mov == correct_y:
                found_correct_corrected_move[run_idx] = 1
                required_moves[movements] += 1
        
    return num_found_exact, num_found_inexact, num_found_corrected, num_found_corrected_move, \
            found_correct_exact, found_correct_inexact, found_correct_corrected, found_correct_corrected_move, required_moves
        

def run_MC_5_REMOVE(gridsize: int, steps: int, MC_iterations: int, error=0.001) -> np.ndarray:
    """
    Yet another way to run calculations. This time thi just returns all values
    """
    # num found vector for every simulation in MC
    num_found_exact    = np.zeros((MC_iterations), dtype=int)
    
    # if TP then if location correct
    found_correct_exact    = np.zeros((MC_iterations), dtype=int)
    
    
    height = gridsize
    width = gridsize
    
    # Runs simulation in loop
    for run_idx in range(MC_iterations):
        m = mapgrid.generate_map(width=width, height=height)
        v = vehicle.Vehicle(m)
        for i in range(steps):
            v.move_unbound()
        
        
        err_hist = v.history_error(iteration_for_seed=run_idx, error=error)
        
        num_found_exact[run_idx], x_ext, y_ext = locator.locate(v.map(), v.history())[0:3]
        
        if num_found_exact[run_idx] == 1:
            found_correct_exact[run_idx] = 1
            
    return found_correct_exact


def calc_or_load_simulation(gridsize=-1, steps=10, error=0.001, 
                             iterations=1000, dirname="Unnamed", use_stored_results=False):
    """
    Calulates the confusion matrices (and errorbars) for given arguments.
    Varites either gridsize or steps or error
    IF gridsize is -1 then variate gridsize over a range
    IF steps is -1 then variate that
    IF error is 'nan'
    
    in a nutchell: this function calls 'run_MC_2()' iteratively
    
    return
        x_axis      values for variating value   
        res_vec     mean and errors of confusion mat, see below
    """
    # res_vec (result vector) dimensions: 
    #       0: variating value, ~10-20
    #       1: MC single simulation index ~0-1000
    #       2: positive, negative (measurement error)
    #       3: true, false (no measurement error)
    x_axis = None  #gridsizes, or steps
    res_vec = None  # np.empty((10,2,2,2))
    error_info = None
    res_vec_corr = None  # np.empty((10,2,2,2))
    
    dir_base = "calulated_results/"+dirname+"__itr"+str(iterations)
    create_directory_if_it_doesnt_exist_already(dir_base)
    filename = dir_base+"/gs"+str(gridsize)+"_st"+str(steps)+".npz"
    
    if not use_stored_results:
        
        log.debug("Number of Monte Carlo iterations with every calulation: "+ str(iterations))

        if gridsize == -1:
            gridsize_vec = np.arange(10,60,5)
            x_axis = gridsize_vec
            res_vec = np.zeros((len(gridsize_vec),iterations,2,2), dtype=int)
            error_info = np.zeros((len(gridsize_vec),iterations,3), dtype=int)
            res_vec_corr = np.zeros((len(gridsize_vec),iterations,2,2), dtype=int)
            
            for i, gs in enumerate(gridsize_vec):
                res_vec[i,:,:,:], error_info[i,:,:], res_vec_corr[i,:,:,:] = run_MC_3(gs, steps, iterations, error=error)
                log.debug("    Process:", str(i+1)+"/"+str(len(gridsize_vec)), " gridsize:", gs)
            

        elif steps == -1:
            steps_vec = np.arange(1,10+1)
            x_axis = steps_vec
            res_vec = np.zeros((len(steps_vec),iterations,2,2), dtype=int)
            error_info = np.zeros((len(steps_vec),iterations,3), dtype=int)
            res_vec_corr = np.zeros((len(gridsize_vec),iterations,2,2), dtype=int)
            
            for i, st in enumerate(steps_vec):
                res_vec[i,:,:,:], error_info[i,:,:], res_vec_corr[i,:,:,:] = run_MC_3(gridsize, st, iterations, error=error)
                log.debug("    Process:", str(i+1)+"/"+str(len(steps_vec)), " steps", st)
        
        elif np.isnan(error): #float('nan')
            err_vec = np.logspace(-4,0,10)
            x_axis = err_vec
            res_vec = np.zeros((len(err_vec),iterations,2,2), dtype=int)
            error_info = np.zeros((len(err_vec),iterations,3), dtype=int)
            res_vec_corr = np.zeros((len(gridsize_vec),iterations,2,2), dtype=int)
            
            for i, er in enumerate(err_vec):
                res_vec[i,:,:,:], error_info[i,:,:], res_vec_corr[i,:,:,:] = run_MC_3(gridsize, steps, iterations, error=er)
                log.debug("    Process:", str(i+1)+"/"+str(len(err_vec)), " error", er)
        else:
            raise Exception("You have to variate gridsize or steps, set that value to -1 to do that")
        
        np.savez(filename, x_axis=x_axis, res_vec=res_vec, error_info=error_info, res_vec_corr=res_vec_corr)
                
    # get pre calculated data
    else:        
        if not os.path.isfile(filename):
            raise Exception("No calulations exists (yet) with these parameters\n" + filename)
        
        npzfile = np.load(filename)
        
        log.debug("npzfile", npzfile.files)
        
        x_axis     = npzfile['x_axis']
        res_vec    = npzfile['res_vec']
        error_info = npzfile['error_info']
    
    return x_axis, res_vec, error_info
        
    
def plot_TP_error(iterations=1000, use_stored_results=False):
    """
    TP does not mean that single location with error correct. This function checks that
    """
    x_axis, res_vec, error_info = calc_or_load_simulation(gridsize=20, steps=-1, error=0.001, 
                                                          iterations=iterations, dirname="loc_err_in_TP", 
                                                          use_stored_results=use_stored_results)
    
   
    num_1_1_matches = np.sum(res_vec[:,:,0,0], axis=1)  # sum TP
    num_1_1_incorrect = np.sum(error_info[:,:,2], axis=1) # sum(TP) - sum(correct)
    
    dividor = num_1_1_matches #+ (num_1_1_matches==0)*1
    
    log.debug(num_1_1_incorrect, dividor)
    
    pres = num_1_1_incorrect / dividor
    
    plotter.plot_one(x_axis, pres, xlabel="askelten lukumäärä", ylim=None, log_scale=False, savename="loc_err_in_TP")
    
def compare_algorithms_var_error(iterations=1000):
        
    x_axis = np.logspace(-4,0,10) # Error
    
    y_axis_1 = np.zeros(len(x_axis))
    y_axis_2 = np.zeros(len(x_axis))
    y_axis_3 = np.zeros(len(x_axis))
    y_axis_4 = np.zeros(len(x_axis))
    
    y_err_1 = np.zeros(len(x_axis))
    y_err_2 = np.zeros(len(x_axis))
    y_err_3 = np.zeros(len(x_axis))
    y_err_4 = np.zeros(len(x_axis))
    
    
    dir_base = "calulated_results/compare_algorithms__itr"+str(iterations)
    create_directory_if_it_doesnt_exist_already(dir_base)
    filename = dir_base+"/gs"+str(20)+"_st"+str(10)+".npz"
    
    if not os.path.isfile(filename):
        for i, er in enumerate(x_axis):    
            log.debug("progress", i+1 ,"/", len(x_axis))
            num_found_exact, \
                num_found_inexact, \
                num_found_corrected, \
                num_found_corrected_move, \
                found_correct_exact, \
                found_correct_inexact, \
                found_correct_corrected, \
                found_correct_corrected_move, \
                required_moves \
                            = run_MC_4(20, 10, iterations, error=er)
            
            y_axis_1[i] = np.mean(found_correct_exact)
            y_axis_2[i] = np.mean(found_correct_inexact)
            y_axis_3[i] = np.mean(found_correct_corrected)
            y_axis_4[i] = np.mean(found_correct_corrected_move)
            
            y_err_1[i] = np.std(found_correct_exact) / np.sqrt(iterations)
            y_err_2[i] = np.std(found_correct_inexact) / np.sqrt(iterations)
            y_err_3[i] = np.std(found_correct_corrected) / np.sqrt(iterations)
            y_err_4[i] = np.std(found_correct_corrected_move) / np.sqrt(iterations)
        
        np.savez(filename, y_axis_1=y_axis_1, y_axis_2=y_axis_2, y_axis_3=y_axis_3, y_axis_4=y_axis_4, \
            y_err_1=y_err_1, y_err_2=y_err_2, y_err_3=y_err_3, y_err_4=y_err_4)
        
    else:
        
        npzfile = np.load(filename)
        
        y_axis_1 = npzfile['y_axis_1']
        y_axis_2 = npzfile['y_axis_2']
        y_axis_3 = npzfile['y_axis_3']
        y_axis_4 = npzfile['y_axis_4']
        
        y_err_1 = npzfile['y_err_1']
        y_err_2 = npzfile['y_err_2']
        y_err_3 = npzfile['y_err_3']
        y_err_4 = npzfile['y_err_4']
        
    
    plotter.plot_multiple_errorbar(  x_axis, 
                            [y_axis_1,y_axis_2,y_axis_3,y_axis_4], 
                            list_yerr = [y_err_1,y_err_2,y_err_3,y_err_4],
                            xlabel="havaintovirhe", 
                            list_label=["tarkka mittaus (referenssi)", "ei virheenkorjausta", "virheenkorjaus", "virheenkorjaus lisäaskelilla"],
                            linestyles=["-","--",":",":",],
                            log_scale=True, 
                            savename="virheenkorjaus",
                            ylim=(-0.05,1.05))

        
    
    
    
def create_directory_if_it_doesnt_exist_already(directory:str):
    if not os.path.exists(directory):
        os.makedirs(directory)
    

