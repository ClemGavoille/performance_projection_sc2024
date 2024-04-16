#!/usr/bin/python3

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import click

gem5_reference_speedup = [[1.98301018,2.317177553,2.85341747],[1.98301018,2.317177553,2.85341747],[0.5641579249,1.326995397,2.263423799],[0.5641579249,1.326995397,2.263423799]]
#gem5_reference_speedup = [[0.5641579249,1.326995397,2.263423799]]
#gem5_reference_speedup = [[1.7256691,1.716761727,2.498146883],[1.98301018,2.317177553,2.85341747],[1.315648689,2.028681755,4.643247341],[0.5641579249,1.326995397,2.263423799],[2.667094105,2.671090575,2.671095742],[46.957/17.505,46.957/16.493,46.957/16.050]]

#gem5_reference_speedup = [[46.957/17.505,46.957/16.493,46.957/16.050]]
############### Metrics computation functions ##################

"""Return the TID of the thread of the source application with the closest OI to the considered target application thread"""
def find_reference_thread(source_app,current_app):
    ref_TID = 0
    delta_OI = 100000000
    current_app_OI = float((current_app["Flops"]/current_app["Bytes"]).values[0])
    for TID in sorted(source_app["TID"].unique()):
        cursor_TID = source_app[source_app["TID"] == TID]
        cursor_OI = float((cursor_TID["Flops"]/cursor_TID["Bytes"]).values[0])
        if abs(cursor_OI - current_app_OI) < delta_OI:
            delta_OI = abs(cursor_OI - current_app_OI)
            ref_TID = TID
    return ref_TID

def find_reference_thread_IF(source_app,current_app):
    ref_TID = 0
    delta_OI = 100000000
    current_app_OI = ((current_app["Flops"] + current_app["Intops"])/current_app["Bytes"]).values[0]
    for TID in source_app["TID"].unique():
        cursor_TID = source_app[source_app["TID"] == TID]
        cursor_OI = ((cursor_TID["Flops"] + current_app["Intops"])/cursor_TID["Bytes"]).values[0]
        if abs(cursor_OI - current_app_OI) < delta_OI:
            delta_OI = abs(cursor_OI - current_app_OI)
            ref_TID = TID
    return ref_TID

def find_reference_thread_int(source_app,current_app):
    ref_TID = 0
    delta_OI = 100000000
    current_app_OI = (current_app["Intops"]/current_app["Bytes"]).values[0]
    for TID in source_app["TID"].unique():
        cursor_TID = source_app[source_app["TID"] == TID]
        cursor_OI = (cursor_TID["Intops"]/cursor_TID["Bytes"]).values[0]
        if abs(cursor_OI - current_app_OI) < delta_OI:
            delta_OI = abs(cursor_OI - current_app_OI)
            ref_TID = TID
    return ref_TID

def compute_L1_BW(current_app,current_machine,n_core):
    tot = current_app["L1_hit"] + current_app["L2_hit"] +  current_app["DRAM_hit"]
    L1_BW = current_app["L1_hit"]/(current_machine["L1"].values[0]/n_core)
    L2_BW = current_app["L2_hit"]/(current_machine["L2"].values[0]/n_core)
    DRAM_BW = current_app["DRAM_hit"]/(current_machine["Stream"].values[0]/n_core)
    return ((tot/(L1_BW + L2_BW  + DRAM_BW)).values[0])

def compute_L2_BW(current_app,current_machine,n_core):
    tot = current_app["L2_hit"] + current_app["DRAM_hit"]
    L2_BW = current_app["L2_hit"]/(current_machine["L2"].values[0]/n_core)
    DRAM_BW = current_app["DRAM_hit"]/(current_machine["Stream"].values[0]/n_core)
    return (tot/(L2_BW  + DRAM_BW)).values[0]

def compute_L3_BW(current_app,current_machine,n_core):
    tot = current_app["L3_hit"] + current_app["DRAM_hit"]
    L3_BW = current_app["L3_hit"]/(current_machine["L3"].values[0]/n_core)
    DRAM_BW = current_app["DRAM_hit"]/(current_machine["Stream"].values[0]/n_core)
    return (tot/(L3_BW + DRAM_BW)).values[0]

def compute_DRAM_BW(current_app,current_machine,n_core):
    tot = current_app["DRAM_hit"]
    DRAM_BW = current_app["DRAM_hit"]/(current_machine["Stream"].values[0]/n_core)
    return (tot/DRAM_BW).values[0]

def compute_L1_OI(current_app):
    return float(current_app["Flops"].values[0]/current_app["Bytes"].values[0])

def compute_L2_OI(current_app):
    L2_Bytes = current_app["Bytes"] * (current_app["L2_hit"] +  current_app["DRAM_hit"])/100
    return (current_app["Flops"]/L2_Bytes).values[0]

def compute_L3_OI(current_app):
    L3_Bytes = current_app["Bytes"] * ( current_app["L3_hit"] + current_app["DRAM_hit"])/100
    return (current_app["Flops"]/L3_Bytes).values[0]

def compute_DRAM_OI(current_app):
    DRAM_Bytes = current_app["Bytes"] * (current_app["DRAM_hit"])/100
    return (current_app["Flops"]/DRAM_Bytes).values[0]

def compute_L1_OI_IF(current_app):
    return ((current_app["Intops"] + current_app["Flops"])/current_app["Bytes"]).values[0]

def compute_L2_OI_IF(current_app):
    L2_Bytes = current_app["Bytes"] * (current_app["L2_hit"] +  current_app["DRAM_hit"])/100
    return ((current_app["Intops"] + current_app["Flops"])/L2_Bytes).values[0]

def compute_DRAM_OI_IF(current_app):
    DRAM_Bytes = current_app["Bytes"] * (current_app["DRAM_hit"])/100
    return ((current_app["Intops"] + current_app["Flops"])/DRAM_Bytes).values[0]

def compute_L1_OI_int(current_app):
    return (current_app["Intops"]/current_app["Bytes"]).values[0]

def compute_L2_OI_int(current_app):
    L2_Bytes = current_app["Bytes"] * (current_app["L2_hit"] +  current_app["DRAM_hit"])/100
    return (current_app["Intops"]/L2_Bytes).values[0]

def compute_DRAM_OI_int(current_app):
    DRAM_Bytes = current_app["Bytes"] * (current_app["DRAM_hit"])/100
    return (current_app["Intops"]/DRAM_Bytes).values[0]

def compute_HPL_ponderated(current_app,current_machine,n_core):
    HPL_core = (current_machine["HPL"].values[0])/n_core
    return (HPL_core/( 2 *8 )) * (current_app["Flops"].values[0]/current_app["FPINS"]).values[0]

def compute_HPL_ponderated_IF(current_app,current_machine,n_core):
    HPL_core = (current_machine["HPL"].values[0])/n_core
    return (HPL_core/( 2 * 8 )) * ((current_app["Intops"].values[0] + current_app["Flops"])/(current_app["INTINS"] + current_app["FPINS"])).values[0]

def compute_HPL_ponderated_int(current_app,current_machine,n_core):
    HPL_core = (current_machine["HPL"].values[0])/n_core
    return (HPL_core/( 2 * 8 )) * (current_app["Intops"]/current_app["INTINS"]).values[0]

def compute_L1_average_latency(current_app,current_machine):
    return (current_app["L1_hit"].values[0] * current_machine["L1_latency"].values[0] + current_app["L2_hit"].values[0] * current_machine["L2_latency"].values[0] + current_app["DRAM_hit"].values[0] * current_machine["DRAM_latency"].values[0])/100

def compute_L2_average_latency(current_app,current_machine):
    return (current_app["L2_hit"].values[0]/(current_app["L2_hit"].values[0] + current_app["DRAM_hit"].values[0]) * current_machine["L2_latency"].values[0] + current_app["DRAM_hit"].values[0]/(current_app["L2_hit"].values[0] + current_app["DRAM_hit"].values[0]) * current_machine["DRAM_latency"].values[0])/100

def compute_DRAM_average_latency(current_app,current_machine):
    return current_machine["DRAM_latency"].values[0]

def compute_L1_access_cycles(current_app,current_machine):
    return (current_app["N_accesses"] * compute_L1_average_latency(current_app,current_machine)).values[0]

def compute_L2_access_cycles(current_app,current_machine):
    return (current_app["N_accesses"] * (1 - current_app["L1_hit"]/100) * compute_L2_average_latency(current_app,current_machine)).values[0]

def compute_DRAM_access_cycles(current_app,current_machine):
    return (current_app["N_accesses"] * current_app["DRAM_hit"]/100 * compute_DRAM_average_latency(current_app,current_machine)).values[0]

def compute_L1_mem_overlap(current_app,current_machine):
    return (current_app["N_mem_stalls"]/(current_app["L1_cycles"].values[0] + current_app["L2_cycles"].values[0] +current_app["DRAM_cycles"].values[0])).values[0]

def compute_L2_mem_overlap(current_app,current_machine):
    return ((current_app["N_L2_mem_stalls"] + current_app["N_L2_miss_mem_stalls"])/(current_app["L2_cycles"].values[0] +current_app["DRAM_cycles"].values[0])).values[0]

def compute_DRAM_mem_overlap(current_app,current_machine):
    return (current_app["N_L2_miss_mem_stalls"]/current_app["DRAM_cycles"].values[0]).values[0]

def compute_L1_ov_deltamem(source_app,source_machine,target_app,target_machine):
    return compute_L1_mem_overlap(source_app,source_machine) * (compute_L1_access_cycles(target_app,target_machine) - compute_L1_access_cycles(source_app,source_machine))

def compute_L2_ov_deltamem(source_app,source_machine,target_app,target_machine):
    return compute_L2_mem_overlap(source_app,source_machine) * (compute_L2_access_cycles(target_app,target_machine) - compute_L2_access_cycles(source_app,source_machine))

def compute_DRAM_ov_deltamem(source_app,source_machine,target_app,target_machine):
    return compute_DRAM_mem_overlap(source_app,source_machine) * (compute_DRAM_access_cycles(target_app,target_machine) - compute_DRAM_access_cycles(source_app,source_machine))

def compute_latency_efficiency(source_app,source_machine,source_times,target_app,target_machine,source_roof,source_perf,ov_deltamem):
    N_cycles_src = source_times["Time"].values[0] * source_machine["Frequency"].values[0] * 10**9
    N_stalls_src = (1 - source_perf/source_roof) * N_cycles_src
    return 1 - ((N_stalls_src + ov_deltamem)/(N_cycles_src + ov_deltamem))

def compute_L2_mem_stall_efficiency(source_app,source_machine,source_times,target_app,target_machine):
    overlap = compute_L2_mem_overlap(source_app,source_machine)
    delta_mem = compute_L2_access_cycles(target_app,target_machine)  - compute_L2_access_cycles(source_app,source_machine) 
    return (overlap * delta_mem)/((source_times["Time"].values[0] * source_machine["Frequency"].values[0] * 10**9) + overlap * delta_mem)

def compute_DRAM_mem_stall_efficiency(source_app,source_machine,source_times,target_app,target_machine):
    overlap = compute_DRAM_mem_overlap(source_app,source_machine)
    delta_mem = compute_DRAM_access_cycles(target_app,target_machine)  - compute_DRAM_access_cycles(source_app,source_machine) 
    return (overlap * delta_mem)/((source_times["Time"].values[0] * source_machine["Frequency"].values[0] * 10**9) + overlap * delta_mem)

def compute_perf_IF(current_app,current_times):
    return (((current_app["Intops"] + current_app["Flops"]).values[0]/current_times["Time"].values[0])*10**-9)

def compute_perf_int(current_app,current_times):
    return ((current_app["Intops"].values[0]/current_times["Time"].values[0])*10**-9)

def compute_perf(current_app,current_times):
    return ((current_app["Flops"]/current_times["Time"].values[0])*10**-9).values[0]

def compute_roofline(BW,HPL,OI):
    return min(BW * OI, HPL)

########### Prediction functions ###########

""" Compute the prediction of a single thread """
def compute_prediction(applis,machines,times,source_run,target_run,source_machine,target_machine,TID):
    prediction_list = []

    n_core_source = applis.loc[(applis["Run"] == source_run)]["TID"].nunique()
    n_core_target = applis.loc[(applis["Run"] == target_run)]["TID"].nunique()
    # Get source metrics
    target_current_app = applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)] 
    source_current_app = applis.loc[(applis["Run"] == source_run) & (applis["TID"] == find_reference_thread(applis.loc[(applis["Run"] == source_run)],target_current_app))] 
    source_current_time = times.loc[times["Run"] == source_run]
    source_machine = machines.loc[machines["Machine"] == source_machine]
    source_BW = [compute_L1_BW(source_current_app,source_machine,n_core_source),compute_L2_BW(source_current_app,source_machine,n_core_source),compute_DRAM_BW(source_current_app,source_machine,n_core_source)]
    source_OI = [compute_L1_OI(source_current_app),compute_L2_OI(source_current_app),compute_DRAM_OI(source_current_app)]
    
    source_HPL = compute_HPL_ponderated(source_current_app,source_machine,n_core_source) 
    source_Perf = compute_perf(source_current_app,source_current_time)

    # Get target metrics
    target_machine = machines.loc[machines["Machine"] == target_machine]
    target_BW = [compute_L1_BW(target_current_app,target_machine,n_core_target),compute_L2_BW(target_current_app,target_machine,n_core_target),compute_DRAM_BW(target_current_app,target_machine,n_core_target)]
    target_OI = [compute_L1_OI(target_current_app),compute_L2_OI(target_current_app),compute_DRAM_OI(target_current_app)]
    target_HPL = compute_HPL_ponderated(target_current_app,target_machine,n_core_target) 

    # Projection for each OI/memory level
    for cursor in range(len(source_BW)):
        source_roof = compute_roofline(source_BW[cursor],source_HPL,source_OI[cursor])
        target_roof = compute_roofline(target_BW[cursor],target_HPL,target_OI[cursor])
        prediction_list.append((source_Perf/source_roof) * target_roof)
    return prediction_list

""" Compute the IF prediction of a single thread """
def compute_prediction_IF(applis,machines,times,source_run,target_run,source_machine,target_machine,TID):
    prediction_list = []

    n_core_source = applis.loc[(applis["Run"] == source_run)]["TID"].nunique()
    n_core_target = applis.loc[(applis["Run"] == target_run)]["TID"].nunique()
    # Get source metrics
    target_current_app = applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)] 
    source_current_app = applis.loc[(applis["Run"] == source_run) & (applis["TID"] == find_reference_thread_IF(applis.loc[(applis["Run"] == source_run)],target_current_app))] 
    source_current_time = times.loc[times["Run"] == source_run]
    source_machine = machines.loc[machines["Machine"] == source_machine]
    source_BW = [compute_L1_BW(source_current_app,source_machine,n_core_source),compute_L2_BW(source_current_app,source_machine,n_core_source),compute_DRAM_BW(source_current_app,source_machine,n_core_source)]
    source_OI = [compute_L1_OI_IF(source_current_app),compute_L2_OI_IF(source_current_app),compute_DRAM_OI_IF(source_current_app)]
    
    source_HPL = compute_HPL_ponderated_IF(source_current_app,source_machine,n_core_source) 
    source_Perf = compute_perf_IF(source_current_app,source_current_time)

    # Get target metrics
    target_machine = machines.loc[machines["Machine"] == target_machine]
    target_BW = [compute_L1_BW(target_current_app,target_machine,n_core_target),compute_L2_BW(target_current_app,target_machine,n_core_target),compute_DRAM_BW(target_current_app,target_machine,n_core_target)]
    target_OI = [compute_L1_OI_IF(target_current_app),compute_L2_OI_IF(target_current_app),compute_DRAM_OI_IF(target_current_app)]
    target_HPL = compute_HPL_ponderated_IF(target_current_app,target_machine,n_core_target) 

    # Projection for each OI/memory level
    for cursor in range(len(source_BW)):
        source_roof = compute_roofline(source_BW[cursor],source_HPL,source_OI[cursor])
        target_roof = compute_roofline(target_BW[cursor],target_HPL,target_OI[cursor])
        prediction_list.append( (source_Perf/source_roof)* target_roof)
    return prediction_list

""" Compute the IF prediction of a single thread """
def compute_latency_prediction_IF(applis,machines,times,source_run,target_run,source_machine,target_machine,TID):
    prediction_list = []

    n_core_source = applis.loc[(applis["Run"] == source_run)]["TID"].nunique()
    n_core_target = applis.loc[(applis["Run"] == target_run)]["TID"].nunique()
    # Get source metrics
    target_current_app = applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)] 
    source_current_app = applis.loc[(applis["Run"] == source_run) & (applis["TID"] == find_reference_thread_IF(applis.loc[(applis["Run"] == source_run)],target_current_app))] 
    source_current_time = times.loc[times["Run"] == source_run]
    source_machine = machines.loc[machines["Machine"] == source_machine]
    source_BW = [compute_L1_BW(source_current_app,source_machine,n_core_source),compute_L2_BW(source_current_app,source_machine,n_core_source),compute_DRAM_BW(source_current_app,source_machine,n_core_source)]
    source_OI = [compute_L1_OI_IF(source_current_app),compute_L2_OI_IF(source_current_app),compute_DRAM_OI_IF(source_current_app)]
    
    source_HPL = compute_HPL_ponderated_IF(source_current_app,source_machine,n_core_source) 
    source_Perf = compute_perf_IF(source_current_app,source_current_time)

    # Get target metrics
    target_machine = machines.loc[machines["Machine"] == target_machine]
    target_BW = [compute_L1_BW(target_current_app,target_machine,n_core_target),compute_L2_BW(target_current_app,target_machine,n_core_target),compute_DRAM_BW(target_current_app,target_machine,n_core_target)]
    target_OI = [compute_L1_OI_IF(target_current_app),compute_L2_OI_IF(target_current_app),compute_DRAM_OI_IF(target_current_app)]
    target_HPL = compute_HPL_ponderated_IF(target_current_app,target_machine,n_core_target) 
    ov_deltamems = [compute_L1_ov_deltamem(source_current_app,source_machine,target_current_app,target_machine),compute_L2_ov_deltamem(source_current_app,source_machine,target_current_app,target_machine),compute_DRAM_ov_deltamem(source_current_app,source_machine,target_current_app,target_machine)]

    # Projection for each OI/memory level
    for cursor in range(len(source_BW)):
        source_roof = compute_roofline(source_BW[cursor],source_HPL,source_OI[cursor])
        target_roof = compute_roofline(target_BW[cursor],target_HPL,target_OI[cursor])
        eff = compute_latency_efficiency(source_current_app,source_machine,source_current_time,target_current_app,target_machine,source_roof,source_Perf,ov_deltamems[cursor])
        prediction_list.append(eff * target_roof)
    return prediction_list

""" Compute the latency prediction of a single thread """
def compute_latency_prediction(applis,machines,times,source_run,target_run,source_machine,target_machine,TID):
    prediction_list = []

    n_core_source = applis.loc[(applis["Run"] == source_run)]["TID"].nunique()
    n_core_target = applis.loc[(applis["Run"] == target_run)]["TID"].nunique()
    # Get source metrics
    target_current_app = applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)] 
    if TID == 0:
        source_current_app = applis.loc[(applis["Run"] == source_run) & (applis["TID"] == 0)] 
    else:
        source_current_app = applis.loc[(applis["Run"] == source_run) & (applis["TID"] == find_reference_thread(applis.loc[(applis["Run"] == source_run)],target_current_app))] 

    source_current_time = times.loc[times["Run"] == source_run]
    source_machine = machines.loc[machines["Machine"] == source_machine]
    source_BW = [compute_L1_BW(source_current_app,source_machine,n_core_source),compute_L2_BW(source_current_app,source_machine,n_core_source),compute_DRAM_BW(source_current_app,source_machine,n_core_source)]
    source_OI = [compute_L1_OI(source_current_app),compute_L2_OI(source_current_app),compute_DRAM_OI(source_current_app)]
    
    source_HPL = compute_HPL_ponderated(source_current_app,source_machine,n_core_source) 
    source_Perf = compute_perf(source_current_app,source_current_time)

    # Get target metrics
    target_machine = machines.loc[machines["Machine"] == target_machine]
    target_BW = [compute_L1_BW(target_current_app,target_machine,n_core_target),compute_L2_BW(target_current_app,target_machine,n_core_target),compute_DRAM_BW(target_current_app,target_machine,n_core_target)]
    target_OI = [compute_L1_OI(target_current_app),compute_L2_OI(target_current_app),compute_DRAM_OI(target_current_app)]
    target_HPL = compute_HPL_ponderated(target_current_app,target_machine,n_core_target) 
    ov_deltamems = [compute_L1_ov_deltamem(source_current_app,source_machine,target_current_app,target_machine),compute_L2_ov_deltamem(source_current_app,source_machine,target_current_app,target_machine),compute_DRAM_ov_deltamem(source_current_app,source_machine,target_current_app,target_machine)]

    # Projection for each OI/memory level
    for cursor in range(len(source_BW)):
        source_roof = compute_roofline(source_BW[cursor],source_HPL,source_OI[cursor])
        target_roof = compute_roofline(target_BW[cursor],target_HPL,target_OI[cursor])
        eff = compute_latency_efficiency(source_current_app,source_machine,source_current_time,target_current_app,target_machine,source_roof,source_Perf,ov_deltamems[cursor])
        prediction_list.append( eff * target_roof)
    return prediction_list



""" Compute the IF prediction of a single thread """
def compute_prediction_int(applis,machines,times,source_run,target_run,source_machine,target_machine,TID):
    prediction_list = []

    n_core_source = applis.loc[(applis["Run"] == source_run)]["TID"].nunique()
    n_core_target = applis.loc[(applis["Run"] == target_run)]["TID"].nunique()
    # Get source metrics
    target_current_app = applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)] 
    source_current_app = applis.loc[(applis["Run"] == source_run) & (applis["TID"] == find_reference_thread_int(applis.loc[(applis["Run"] == source_run)],target_current_app))] 
    source_current_time = times.loc[times["Run"] == source_run]
    source_machine = machines.loc[machines["Machine"] == source_machine]
    source_BW = [compute_L1_BW(source_current_app,source_machine,n_core_source),compute_L2_BW(source_current_app,source_machine,n_core_source),compute_DRAM_BW(source_current_app,source_machine,n_core_source)]
    source_OI = [compute_L1_OI_int(source_current_app),compute_L2_OI_int(source_current_app),compute_DRAM_OI_int(source_current_app)]
    
    source_HPL = compute_HPL_ponderated_int(source_current_app,source_machine,n_core_source) 
    source_Perf = compute_perf_int(source_current_app,source_current_time)

    # Get target metrics
    target_machine = machines.loc[machines["Machine"] == target_machine]
    target_BW = [compute_L1_BW(target_current_app,target_machine,n_core_target),compute_L2_BW(target_current_app,target_machine,n_core_target),compute_DRAM_BW(target_current_app,target_machine,n_core_target)]
    target_OI = [compute_L1_OI_int(target_current_app),compute_L2_OI_int(target_current_app),compute_DRAM_OI_int(target_current_app)]
    target_HPL = compute_HPL_ponderated_int(target_current_app,target_machine,n_core_target) 

    # Projection for each OI/memory level
    for cursor in range(len(source_BW)):
        source_roof = compute_roofline(source_BW[cursor],source_HPL,source_OI[cursor])
        target_roof = compute_roofline(target_BW[cursor],target_HPL,target_OI[cursor])
        prediction_list.append((source_Perf/source_roof) * target_roof)
    return prediction_list


""" Compute the IF prediction of a single thread """
def compute_latency_prediction_int(applis,machines,times,source_run,target_run,source_machine,target_machine,TID):
    prediction_list = []

    n_core_source = applis.loc[(applis["Run"] == source_run)]["TID"].nunique()
    n_core_target = applis.loc[(applis["Run"] == target_run)]["TID"].nunique()
    # Get source metrics
    target_current_app = applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)] 
    source_current_app = applis.loc[(applis["Run"] == source_run) & (applis["TID"] == find_reference_thread_int(applis.loc[(applis["Run"] == source_run)],target_current_app))] 
    source_current_time = times.loc[times["Run"] == source_run]
    source_machine = machines.loc[machines["Machine"] == source_machine]
    source_BW = [compute_L1_BW(source_current_app,source_machine,n_core_source),compute_L2_BW(source_current_app,source_machine,n_core_source),compute_DRAM_BW(source_current_app,source_machine,n_core_source)]
    source_OI = [compute_L1_OI_int(source_current_app),compute_L2_OI_int(source_current_app),compute_DRAM_OI_int(source_current_app)]
    
    source_HPL = compute_HPL_ponderated_int(source_current_app,source_machine,n_core_source) 
    source_Perf = compute_perf_int(source_current_app,source_current_time)

    # Get target metrics
    target_machine = machines.loc[machines["Machine"] == target_machine]
    target_BW = [compute_L1_BW(target_current_app,target_machine,n_core_target),compute_L2_BW(target_current_app,target_machine,n_core_target),compute_DRAM_BW(target_current_app,target_machine,n_core_target)]
    target_OI = [compute_L1_OI_int(target_current_app),compute_L2_OI_int(target_current_app),compute_DRAM_OI_int(target_current_app)]
    target_HPL = compute_HPL_ponderated_int(target_current_app,target_machine,n_core_target) 
    ov_deltamems = [compute_L1_ov_deltamem(source_current_app,source_machine,target_current_app,target_machine),compute_L2_ov_deltamem(source_current_app,source_machine,target_current_app,target_machine),compute_DRAM_ov_deltamem(source_current_app,source_machine,target_current_app,target_machine)]

    # Projection for each OI/memory level
    for cursor in range(len(source_BW)):
        source_roof = compute_roofline(source_BW[cursor],source_HPL,source_OI[cursor])
        target_roof = compute_roofline(target_BW[cursor],target_HPL,target_OI[cursor])
        eff = compute_latency_efficiency(source_current_app,source_machine,source_current_time,target_current_app,target_machine,source_roof,source_Perf,ov_deltamems[cursor])
        prediction_list.append( eff * target_roof)
    return prediction_list


############################################################# ITERATION FUNCTIONS ################################################### 


""" Iterate the single thread prediction over every threads """
def compute_prediction_whole_appli(applis,machines,times,source_run,target_run,source_machine,target_machine):

    # Assertion wall 

    assert source_run in applis["Run"].unique(), "Source application identifier does not match with any found in the input analysis files"
    assert source_run in times["Run"].unique(), "Source application identifier does not match with any found in the input times files"
    assert target_run in applis["Run"].unique(), "Target application identifier does not match with any found in the input analysis files"
    assert source_machine in machines["Machine"].unique(), "Source machine identifier does not match with any found in the input machines files"
    assert target_machine in machines["Machine"].unique(), "Target machine identifier does not match with any found in the input machines files"
    
    n_core_target = applis[applis["Run"] == target_run]["TID"].nunique()
    n_core_source = applis[applis["Run"] == source_run]["TID"].nunique()

    # Iterate prediction over every thread
    results_list=[compute_prediction(applis,machines,times,source_run,target_run,source_machine,target_machine,i) for i in range(n_core_target)]
    source_perf = sum([compute_perf(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)],times.loc[times["Run"] == source_run]) for TID in range(n_core_source)])
    print("Source perf: ","%.2f" %source_perf)

    OI_list = [ sum([compute_L1_OI(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L2_OI(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_DRAM_OI(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L1_OI(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_L2_OI(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_DRAM_OI(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target]

    min_pred = 0
    max_pred = 0
    pred_list = [0,0,0]
    for j in range(n_core_target):
        min_pred += min(results_list[j])
        max_pred += max(results_list[j])
        for k in range(len(pred_list)):
            pred_list[k] += results_list[j][k]

    target_FLOPS = applis.loc[(applis["Run"] == target_run)]["Flops"].sum()
    source_FLOPS = applis.loc[(applis["Run"] == source_run)]["Flops"].sum()
    source_time = source_FLOPS/source_perf*10**-9
    print("Source Time: ","%.2f" %source_time)
    speedup_list = [k/source_perf for k in pred_list]
    print("Prediction Interval : ","[","%.2f" %min_pred,";","%.2f" %max_pred,"]")
    print("Prediction time Interval : ","[","%.4f" %(target_FLOPS/min_pred*10**-9),";","%.4f" %(target_FLOPS/max_pred*10**-9),"]")
    print("Prediction speedup : ","[","%.4f" %(min(speedup_list)),";","%.4f" %(max(speedup_list)),"]")

    print("===================================")
    return OI_list,pred_list,source_perf,[min_pred,max_pred],[min_pred/source_perf,max_pred/source_perf],speedup_list

""" Iterate the single thread prediction over every threads """
def compute_prediction_whole_appli_IF(applis,machines,times,source_run,target_run,source_machine,target_machine):

    # Assertion wall 

    assert source_run in applis["Run"].unique(), "Source application identifier does not match with any found in the input analysis files"
    assert source_run in times["Run"].unique(), "Source application identifier does not match with any found in the input times files"
    assert target_run in applis["Run"].unique(), "Target application identifier does not match with any found in the input analysis files"
    assert source_machine in machines["Machine"].unique(), "Source machine identifier does not match with any found in the input machines files"
    assert target_machine in machines["Machine"].unique(), "Target machine identifier does not match with any found in the input machines files"
    
    n_core_target = applis[applis["Run"] == target_run]["TID"].nunique()
    n_core_source = applis[applis["Run"] == source_run]["TID"].nunique()

    # Iterate prediction over every thread
    results_list=[compute_prediction_IF(applis,machines,times,source_run,target_run,source_machine,target_machine,i) for i in range(n_core_target)]
    source_perf = sum([compute_perf_IF(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)],times.loc[times["Run"] == source_run]) for TID in range(n_core_source)])
    print("Source perf: ","%.2f" %source_perf)

    OI_list = [ sum([compute_L1_OI_IF(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L2_OI_IF(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_DRAM_OI_IF(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L1_OI_IF(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_L2_OI_IF(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_DRAM_OI_IF(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target]


    min_pred = 0
    max_pred = 0
    pred_list = [0,0,0]
    for j in range(n_core_target):
        min_pred += min(results_list[j])
        max_pred += max(results_list[j])
        for k in range(len(pred_list)):
            pred_list[k] += results_list[j][k]

    print("Prediction Interval : ","[","%.2f" %min_pred,";","%.2f" %max_pred,"]")
    target_FLOPS = applis.loc[(applis["Run"] == target_run)]["Flops"].sum() + applis.loc[(applis["Run"] == target_run)]["Intops"].sum()
    print("Prediction time Interval : ","[","%.4f" %(target_FLOPS/min_pred*10**-9),";","%.4f" %(target_FLOPS/max_pred*10**-9),"]")
    speedup_list = [k/source_perf for k in pred_list]
    print("Prediction speedup : ","[","%.4f" %(min_pred/source_perf),";","%.4f" %(max_pred/source_perf),"]")

    print("===================================")
    #return OI_list,pred_list,source_perf,[min_pred,max_pred],[((times.loc[times["Run"] == source_run])["Time"].values[0]/(target_FLOPS/min_pred*10**-9)),((times.loc[times["Run"] == source_run])["Time"].values[0]/(target_FLOPS/max_pred*10**-9))]
    return OI_list,pred_list,source_perf,[min_pred,max_pred],[min_pred/source_perf,max_pred/source_perf],speedup_list


""" Iterate the single thread prediction over every threads """
def compute_latency_prediction_whole_appli(applis,machines,times,source_run,target_run,source_machine,target_machine):

    # Assertion wall 

    assert source_run in applis["Run"].unique(), "Source application identifier does not match with any found in the input analysis files"
    assert source_run in times["Run"].unique(), "Source application identifier does not match with any found in the input times files"
    assert target_run in applis["Run"].unique(), "Target application identifier does not match with any found in the input analysis files"
    assert source_machine in machines["Machine"].unique(), "Source machine identifier does not match with any found in the input machines files"
    assert target_machine in machines["Machine"].unique(), "Target machine identifier does not match with any found in the input machines files"
    
    n_core_target = applis[applis["Run"] == target_run]["TID"].nunique()
    n_core_source = applis[applis["Run"] == source_run]["TID"].nunique()

    # Iterate prediction over every thread
    results_list=[compute_latency_prediction(applis,machines,times,source_run,target_run,source_machine,target_machine,i) for i in range(n_core_target)]
    source_perf = sum([compute_perf(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)],times.loc[times["Run"] == source_run]) for TID in range(n_core_source)])
    print("Source perf: ","%.2f" %source_perf)


    OI_list = [ sum([compute_L1_OI(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L2_OI(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_DRAM_OI(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L1_OI(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_L2_OI(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_DRAM_OI(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target]

    min_pred = 0
    max_pred = 0
    pred_list = [0,0,0]
    for j in range(n_core_target):
        min_pred += min(results_list[j])
        max_pred += max(results_list[j])
        for k in range(len(pred_list)):
            pred_list[k] += results_list[j][k]

    #print("(","%.2f" % target_perf,",","%.2f" % target_perf,")","(","%.2f" %min_pred,",","%.2f" %max_pred,")")
    target_FLOPS = applis.loc[(applis["Run"] == target_run)]["Flops"].sum()
    speedup_list = [k/source_perf for k in pred_list]
    print("Prediction Interval : ","[","%.2f" %min_pred,";","%.2f" %max_pred,"]")
    print("Prediction time Interval : ","[","%.4f" %(target_FLOPS/min_pred*10**-9),";","%.4f" %(target_FLOPS/max_pred*10**-9),"]")
    print("Prediction speedup : ","[","%.4f" %(min_pred/source_perf),";","%.4f" %(max_pred/source_perf),"]")

    print("===================================")
    return OI_list,pred_list,source_perf,[min_pred,max_pred],[min_pred/source_perf,max_pred/source_perf],speedup_list
    
""" Iterate the single thread prediction over every threads """
def compute_latency_prediction_whole_appli_IF(applis,machines,times,source_run,target_run,source_machine,target_machine):

    # Assertion wall 

    assert source_run in applis["Run"].unique(), "Source application identifier does not match with any found in the input analysis files"
    assert source_run in times["Run"].unique(), "Source application identifier does not match with any found in the input times files"
    assert target_run in applis["Run"].unique(), "Target application identifier does not match with any found in the input analysis files"
    assert source_machine in machines["Machine"].unique(), "Source machine identifier does not match with any found in the input machines files"
    assert target_machine in machines["Machine"].unique(), "Target machine identifier does not match with any found in the input machines files"
    
    n_core_target = applis[applis["Run"] == target_run]["TID"].nunique()
    n_core_source = applis[applis["Run"] == source_run]["TID"].nunique()

    # Iterate prediction over every thread
    results_list=[compute_latency_prediction_IF(applis,machines,times,source_run,target_run,source_machine,target_machine,i) for i in range(n_core_target)]
    source_perf = sum([compute_perf_IF(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)],times.loc[times["Run"] == source_run]) for TID in range(n_core_source)])
    print("Source perf: ","%.2f" %source_perf)


    OI_list = [ sum([compute_L1_OI_IF(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L2_OI_IF(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_DRAM_OI_IF(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L1_OI_IF(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_L2_OI_IF(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_DRAM_OI_IF(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target]


    


    min_pred = 0
    max_pred = 0
    pred_list = [0,0,0]
    for j in range(n_core_target):
        min_pred += min(results_list[j])
        max_pred += max(results_list[j])
        for k in range(len(pred_list)):
            pred_list[k] += results_list[j][k]

    
    #print("(","%.2f" % target_perf,",","%.2f" % target_perf,")","(","%.2f" %min_pred,",","%.2f" %max_pred,")")
    print("Prediction Interval : ","[","%.2f" %min_pred,";","%.2f" %max_pred,"]")
    target_FLOPS = applis.loc[(applis["Run"] == target_run)]["Flops"].sum() + applis.loc[(applis["Run"] == target_run)]["Intops"].sum()
    print("Prediction time Interval : ","[","%.4f" %(target_FLOPS/min_pred*10**-9),";","%.4f" %(target_FLOPS/max_pred*10**-9),"]")
    speedup_list = [k/source_perf for k in pred_list]
    print("Prediction speedup : ","[","%.4f" %(min_pred/source_perf),";","%.4f" %(max_pred/source_perf),"]")

    print("===================================")
    #return OI_list,pred_list,source_perf,[min_pred,max_pred],[((times.loc[times["Run"] == source_run])["Time"].values[0]/(target_FLOPS/min_pred*10**-9)),((times.loc[times["Run"] == source_run])["Time"].values[0]/(target_FLOPS/max_pred*10**-9))]
    return OI_list,pred_list,source_perf,[min_pred,max_pred],[min_pred/source_perf,max_pred/source_perf],speedup_list


""" Iterate the single thread prediction over every threads """
def compute_prediction_whole_appli_int(applis,machines,times,source_run,target_run,source_machine,target_machine):

    # Assertion wall 

    assert source_run in applis["Run"].unique(), "Source application identifier does not match with any found in the input analysis files"
    assert source_run in times["Run"].unique(), "Source application identifier does not match with any found in the input times files"
    assert target_run in applis["Run"].unique(), "Target application identifier does not match with any found in the input analysis files"
    assert source_machine in machines["Machine"].unique(), "Source machine identifier does not match with any found in the input machines files"
    assert target_machine in machines["Machine"].unique(), "Target machine identifier does not match with any found in the input machines files"
    
    n_core_target = applis[applis["Run"] == target_run]["TID"].nunique()
    n_core_source = applis[applis["Run"] == source_run]["TID"].nunique()

    # Iterate prediction over every thread
    results_list=[compute_prediction_int(applis,machines,times,source_run,target_run,source_machine,target_machine,i) for i in range(n_core_target)]
    source_perf = sum([compute_perf_int(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)],times.loc[times["Run"] == source_run]) for TID in range(n_core_source)])
    print("Source perf: ","%.2f" %source_perf)

    OI_list = [ sum([compute_L1_OI_int(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L2_OI_int(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_DRAM_OI_int(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L1_OI_int(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_L2_OI_int(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_DRAM_OI_int(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target]


    


    min_pred = 0
    max_pred = 0
    pred_list = [0,0,0]
    for j in range(n_core_target):
        min_pred += min(results_list[j])
        max_pred += max(results_list[j])
        for k in range(len(pred_list)):
            pred_list[k] += results_list[j][k]

    #print("(","%.2f" % target_perf,",","%.2f" % target_perf,")","(","%.2f" %min_pred,",","%.2f" %max_pred,")")
    print("INT Prediction Interval : ","[","%.2f" %min_pred,";","%.2f" %max_pred,"]")
    target_FLOPS = applis.loc[(applis["Run"] == target_run)]["Intops"].sum()
    print("INT Prediction time Interval : ","[","%.4f" %(target_FLOPS/min_pred*10**-9),";","%.4f" %(target_FLOPS/max_pred*10**-9),"]")
    speedup_list = [k/source_perf for k in pred_list]
    print("INT Prediction speedup : ","[","%.4f" %(min_pred/source_perf),";","%.4f" %(max_pred/source_perf),"]")

    print("===================================")
    #return OI_list,pred_list,source_perf,[min_pred,max_pred],[((times.loc[times["Run"] == source_run])["Time"].values[0]/(target_FLOPS/min_pred*10**-9)),((times.loc[times["Run"] == source_run])["Time"].values[0]/(target_FLOPS/max_pred*10**-9))]
    return OI_list,pred_list,source_perf,[min_pred,max_pred],[min_pred/source_perf,max_pred/source_perf],speedup_list

""" Iterate the single thread prediction over every threads """
def compute_latency_prediction_whole_appli_int(applis,machines,times,source_run,target_run,source_machine,target_machine):

    # Assertion wall 

    assert source_run in applis["Run"].unique(), "Source application identifier does not match with any found in the input analysis files"
    assert source_run in times["Run"].unique(), "Source application identifier does not match with any found in the input times files"
    assert target_run in applis["Run"].unique(), "Target application identifier does not match with any found in the input analysis files"
    assert source_machine in machines["Machine"].unique(), "Source machine identifier does not match with any found in the input machines files"
    assert target_machine in machines["Machine"].unique(), "Target machine identifier does not match with any found in the input machines files"
    
    n_core_target = applis[applis["Run"] == target_run]["TID"].nunique()
    n_core_source = applis[applis["Run"] == source_run]["TID"].nunique()

    # Iterate prediction over every thread
    results_list=[compute_latency_prediction_int(applis,machines,times,source_run,target_run,source_machine,target_machine,i) for i in range(n_core_target)]
    source_perf = sum([compute_perf_int(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)],times.loc[times["Run"] == source_run]) for TID in range(n_core_source)])
    print("Source perf: ","%.2f" %source_perf)

    OI_list = [ sum([compute_L1_OI_int(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L2_OI_int(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_DRAM_OI_int(applis.loc[(applis["Run"] == source_run) & (applis["TID"] == TID)]) for TID in range(n_core_source)])/n_core_source,
                sum([compute_L1_OI_int(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_L2_OI_int(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target,
                sum([compute_DRAM_OI_int(applis.loc[(applis["Run"] == target_run) & (applis["TID"] == TID)]) for TID in range(n_core_target)])/n_core_target]


    


    min_pred = 0
    max_pred = 0
    pred_list = [0,0,0]
    for j in range(n_core_target):
        min_pred += min(results_list[j])
        max_pred += max(results_list[j])
        for k in range(len(pred_list)):
            pred_list[k] += results_list[j][k]

    #print("(","%.2f" % target_perf,",","%.2f" % target_perf,")","(","%.2f" %min_pred,",","%.2f" %max_pred,")")
    print("INT Prediction Interval : ","[","%.2f" %min_pred,";","%.2f" %max_pred,"]")
    target_FLOPS = applis.loc[(applis["Run"] == target_run)]["Intops"].sum()
    print("INT Prediction time Interval : ","[","%.4f" %(target_FLOPS/min_pred*10**-9),";","%.4f" %(target_FLOPS/max_pred*10**-9),"]")
    speedup_list = [k/source_perf for k in pred_list]
    print("INT Prediction speedup : ","[","%.4f" %(min_pred/source_perf),";","%.4f" %(max_pred/source_perf),"]")

    print("===================================")
    #return OI_list,pred_list,source_perf,[min_pred,max_pred],[((times.loc[times["Run"] == source_run])["Time"].values[0]/(target_FLOPS/min_pred*10**-9)),((times.loc[times["Run"] == source_run])["Time"].values[0]/(target_FLOPS/max_pred*10**-9))]
    return OI_list,pred_list,source_perf,[min_pred,max_pred],[min_pred/source_perf,max_pred/source_perf],speedup_list

def compute_prediction_craypat(applis,machines,source_run,source_machine,target_machine):
    source_FLOPS = applis.loc[(applis["Run"] == source_run)]["Flops"].sum()
    source_Bytes = applis.loc[(applis["Run"] == source_run)]["Bytes"].sum() * ((applis.loc[(applis["Run"] == source_run)]["DRAM_hit"].mean())/100)
    DRAM_OI = source_FLOPS/source_Bytes
    source_BW = machines[machines["Machine"] == source_machine]["Stream"].values[0]
    target_BW = machines[machines["Machine"] == target_machine]["Stream"].values[0]
    source_HPL = machines[machines["Machine"] == source_machine]["HPL"].values[0]
    target_HPL = machines[machines["Machine"] == target_machine]["HPL"].values[0]
    predicted_time = applis.loc[(applis["Run"] == source_run)]["Time"] * source_BW/target_BW
    print("%.2f" % (source_FLOPS/applis.loc[(applis["Run"] == source_run)]["Time"].values[0]*10**-9), "%.2f" % (source_FLOPS/predicted_time.values[0]*10**-9))
    print("("+"%.2f" % (source_FLOPS/predicted_time.values[0]*10**-9)+","+"%.2f" % (source_FLOPS/predicted_time.values[0]*10**-9)+")")


########################## PLOT FUNCTIONS ################################

def plot_roof(BW,HPL,start,end,color,label,print_label,style):
    x = np.arange(start,end,0.001)
    roof = [min(BW*i,HPL) for i in x] 
    if (print_label):
        plt.plot(x,roof,color=color,label=label,linestyle=style)
    else:
        plt.plot(x,roof,color=color,linestyle=style)
        

def plot_hardware_roof(machines,machine,start,end,color,label,print_label,style):
    current_machine = machines.loc[machines["Machine"] == machine]
    plot_roof(current_machine["L1"].values[0],current_machine["HPL"].values[0],start,end,color,label,print_label,style)
    plot_roof(current_machine["L2"].values[0],current_machine["HPL"].values[0],start,end,color,label,False,style)
    plot_roof(current_machine["Stream"].values[0],current_machine["HPL"].values[0],start,end,color,label,False,style)

def plot_ponderated_roof(machines,applis,machine,appli,start,end,color,label,print_label,style):
    current_machine = machines.loc[machines["Machine"] == machine]
    n_core = applis.loc[(applis["Run"] == appli)]["TID"].nunique()
    sum_ponderated_HPL = 0
    sum_ponderated_L1_BW = 0
    sum_ponderated_L2_BW = 0
    sum_ponderated_DRAM_BW = 0
    for TID in range(n_core):
        current_app = applis.loc[(applis["Run"] == appli) & (applis["TID"] == TID)]  
        sum_ponderated_HPL += compute_HPL_ponderated(current_app,current_machine,n_core)
        sum_ponderated_L1_BW += compute_L1_BW(current_app,current_machine,n_core)
        sum_ponderated_L2_BW += compute_L2_BW(current_app,current_machine,n_core)
        sum_ponderated_DRAM_BW += compute_DRAM_BW(current_app,current_machine,n_core)

    plot_roof(sum_ponderated_L1_BW,sum_ponderated_HPL,start,end,color,label,print_label,style)
    plot_roof(sum_ponderated_L2_BW,sum_ponderated_HPL,start,end,color,label,False,style)
    plot_roof(sum_ponderated_DRAM_BW,sum_ponderated_HPL,start,end,color,label,False,style)
    print(machine,current_machine["HPL"].values[0],sum_ponderated_HPL)
    

def plot_roof_set_format():
    plt.xscale('log', base=2)
    plt.yscale('log', base=2)
    plt.grid(visible=True)
    plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
    plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.xlabel("Operational Intensity (FLOP/Bytes)")
    plt.ylabel("Performance (GFLOPS)")
    plt.legend(prop={'size': 6})

def plot_barchart(res,ticklabels,labels):
    colors = ["#e69f00","#D55E00","#009e73"]
    n_ticks = len(ticklabels)
    N_per_tick = len(labels)
    loop = n_ticks * N_per_tick
    x = np.arange(0,2*n_ticks,2)
    width = 0.5
    for k in range(len(res)):
        pred_interval=res[k][1]
        if k == 0:
            plt.bar(x[k]-width/2,res[k][0],color=colors[0],width=width,label=labels[0])
            if pred_interval[0] != pred_interval[1]:
                plt.bar(x[k]+width/2,pred_interval[1],color=colors[2],width=width)
            plt.bar(x[k]+width/2,pred_interval[0],color=colors[1],width=width,label=labels[1])
        else:
            plt.bar(x[k]-width/2,res[k][0],color=colors[0],width=width)
            if pred_interval[0] != pred_interval[1]:
                plt.bar(x[k]+width/2,pred_interval[1],color=colors[2],width=width)
            plt.bar(x[k]+width/2,pred_interval[0],color=colors[1],width=width)

    shortened_labels = []
    for i in ticklabels:
        shortened_labels.append(i[:2])

    plt.ylabel("Speedup")
    plt.xlabel("Applications")
    plt.xticks(x,shortened_labels)
    plt.legend()

def plot_speedup_barchart(res,ticklabels,labels):
    colors = ["#e69f00","#D55E00","#009e73"]
    n_ticks = len(ticklabels)
    N_per_tick = len(labels)
    loop = n_ticks * N_per_tick
    x = np.arange(0,2*n_ticks,2)
    width = 0.5
    for k in range(len(res)):
        pred_interval=res[k][1]
        if k == 0:
            plt.bar(x[k]-width/2,res[k][0],color=colors[0],width=width,label=labels[0])
            if pred_interval[0] != pred_interval[1]:
                plt.bar(x[k]+width/2,pred_interval[1],color=colors[2],width=width)
            plt.bar(x[k]+width/2,pred_interval[0],color=colors[1],width=width,label=labels[1])
        else:
            plt.bar(x[k]-width/2,res[k][0],color=colors[0],width=width)
            if pred_interval[0] != pred_interval[1]:
                plt.bar(x[k]+width/2,pred_interval[1],color=colors[2],width=width)
            plt.bar(x[k]+width/2,pred_interval[0],color=colors[1],width=width)


    plt.ylabel("Speedup")
    plt.xlabel("Applications")
    plt.xticks(x,ticklabels)
    plt.legend()


########## CLI Options ##########
@click.command()
@click.argument('files',nargs=-1,type=click.Path(exists=True))
@click.option('--sm',type=str,help="Identifier of source machine, can list more than 1 by separating with a comma and no spaces (ex: machine_a,machine_b)",required=True)
@click.option('--sa',type=str,help="Identifier of source application, can list more than 1 by separating with a comma and no spaces (ex: appli_a,appli_b)",required=True)
@click.option('--tm',type=str,help="Identifier of target machine, can list more than 1 by separating with a comma and no spaces (ex: machine_a,machine_b)",required=True)
@click.option('--ta',type=str,help="Identifier of target application, can list more than 1 by separating with a comma and no spaces (ex: appli_a,appli_b)",required=True)
@click.option('--plot_roof/--no_plot_roof', default=False,help="Plot source and target machine rooflines with projection for each OI, generate an svg file in your current directury for each application, disabled by default")
@click.option('--int_only/--no_int_only', default=False,help="INT prediction (in beta)")
@click.option('--int_float/--no_int_float', default=False,help="IF prediction (in beta)")
@click.option('--latency/--no_latency', default=False,help="IF prediction with latency ponderation (in beta)")
@click.option('--plot_bar/--no_plot_bar', default=False,help="Aggregate all the projection and plot them in a barchart with source performance as a reference, generate one svg file per execution in your current directory, disabled by default")


########## Kinda the main function ########

def compute_prediction_app_click(sa,ta,sm,tm,files,plot_roof,int_only,int_float,latency,plot_bar):
    pd.options.mode.chained_assignment = None
    applis = pd.DataFrame()
    machines = pd.DataFrame()
    times = pd.DataFrame()

    labels_pred = ["L1 Prediction","L2 Prediction","DRAM Prediction"]
    labels_perf = ["L1 Source Performance","L2 Source Performance","DRAM Source Performance"]
    start = 0
    end = 64
    target_color = "#e69f00"
    source_color = "#0072B2"

    for i in files:
        cursor = pd.read_csv(i)
        if "Run" in cursor.columns:  # Applications stats
            if "TID" in cursor.columns:
                for app in cursor["Run"].unique():
                    TID_list = list(cursor["TID"][cursor["Run"] == app].unique())
                    TID_list.sort()
                    for j in TID_list:
                        cursor["TID"][(cursor["TID"] == j) & (cursor["Run"] == app)] = TID_list.index(j)
                if applis.empty:
                    applis = cursor
                else:
                    applis = pd.merge(applis,cursor,on=["Run","TID"],left_index=False,right_index=False) 
            if "Time" in cursor.columns:   # Runtime of applis
                if times.empty:
                    times = cursor
                else:
                    times = pd.concat([times,cursor])
        if "Machine" in cursor.columns:  # Machines
            if machines.empty:
                machines = cursor
            else:
                machines = pd.concat([machines,cursor]) 

    sa = sa.split(",")
    ta = ta.split(",")
    sm = sm.split(",")
    tm = tm.split(",")

    assert len(sm) == len(tm), "Not the same number of source and target machine was requested"
    assert len(sm) == 1,"Current version can only use one source/target machine couple"
    
    aggregated_results = []
    aggregated_speedup_results= []
    aggregated_speedup_list= []
    mach_index = 0
    if ("A64FX_32" in tm[0]):
        mach_index = 0
    if ("LARC_C" in tm[0]):
        mach_index = 1
    if ("LARC_A" in tm[0]):
        mach_index = 2

    for index in range(len(sa)):
        #click.echo("Projection from "+ sm[0] + " / " + sa[index] + " to " + tm[0] + " / " + ta[index])
        if int_float:
            if latency:
                OI_list, pred_list, source_perf, pred_interval, speedup_interval, speedup_list = compute_latency_prediction_whole_appli_IF(applis,machines,times,sa[index],ta[index],sm[0],tm[0])
            else:
                OI_list, pred_list, source_perf, pred_interval, speedup_interval,speedup_list = compute_prediction_whole_appli_IF(applis,machines,times,sa[index],ta[index],sm[0],tm[0])
        elif int_only:
            if latency:
                OI_list, pred_list, source_perf, pred_interval, speedup_interval, speedup_list = compute_latency_prediction_whole_appli_int(applis,machines,times,sa[index],ta[index],sm[0],tm[0])
            else:
                OI_list, pred_list, source_perf, pred_interval, speedup_interval,speedup_list = compute_prediction_whole_appli_int(applis,machines,times,sa[index],ta[index],sm[0],tm[0])
        else:
            if latency:
                OI_list, pred_list, source_perf, pred_interval, speedup_interval, speedup_list = compute_latency_prediction_whole_appli(applis,machines,times,sa[index],ta[index],sm[0],tm[0])
            else:
                OI_list, pred_list, source_perf, pred_interval, speedup_interval,speedup_list = compute_prediction_whole_appli(applis,machines,times,sa[index],ta[index],sm[0],tm[0])

        aggregated_speedup_results.append((gem5_reference_speedup[index][mach_index],speedup_interval))
        aggregated_speedup_list.append(speedup_list)
        aggregated_results.append(speedup_interval)

        if plot_roof:
            plot_hardware_roof(machines,sm[0],start,end,source_color,sm[0]+" hardware roofline",True,"-")
            plot_ponderated_roof(machines,applis,sm[0],sa[index],start,end,source_color,sm[0],True,"--")
            plot_hardware_roof(machines,tm[0],start,end,target_color,tm[0]+" hardware roofline",True,"-")
            plot_ponderated_roof(machines,applis,tm[0],ta[index],start,end,target_color,tm[0],True,"--")
            for k in range(len(labels_pred)):
                plt.scatter(OI_list[k],source_perf,marker="x",label=labels_perf[k])
                plt.scatter(OI_list[k + len(labels_pred)],pred_list[k],marker="+",label=labels_pred[k])
            plot_roof_set_format()
            plt.title(sm[0] + " / " + sa[index] + " to " + tm[0] + " / " + ta[index])
            plt.savefig(sa[index]+"_"+ta[index]+"_projection_roofline.svg")
            plt.clf()
        if plot_bar:
            aggregated_results.append((source_perf,pred_interval))
    if plot_bar:
        plot_barchart(aggregated_speedup_results,ta,["gem5 reference","Projected performance"])
        plt.title(sm[0] + " to " + tm[0])
        plt.savefig(sm[0]+"_"+tm[0]+"_projection_barchart.svg")
        plt.clf()
    print(ta[0],tm[0],aggregated_speedup_list[0][0],aggregated_speedup_list[0][1],aggregated_speedup_list[0][2])
    #print(aggregated_results)
    #print(np.corrcoef(np.array(aggregated_results)[:,0],np.array(gem5_reference_speedup)[:,2]))
    #print(np.corrcoef(np.array(aggregated_results)[:,1],np.array(gem5_reference_speedup)[:,2]))



if __name__ == '__main__':
    compute_prediction_app_click()
    

