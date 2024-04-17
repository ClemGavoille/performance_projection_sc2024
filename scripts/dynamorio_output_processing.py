#!/usr/bin/python3

import sys
import pandas as pd
import numpy as np

applis = pd.read_csv(sys.stdin)
print("Run TID L1_hit L2_hit DRAM_hit N_accesses")
for run in applis["Run"].unique():
    current_app = applis.loc[applis["Run"] == run]
    for core in current_app["Core"].unique():
        if np.isnan(core):
            break
        L2_value = current_app[(current_app["Cache"]=="L2")]["Missrate"].values[0]
        L1_miss = current_app.loc[(current_app["Core"] == core) & (current_app["Cache"] == "L1")]["Missrate"].values[0]
        L1_hit = 100 - L1_miss
        L2_hit = L1_miss * (100 - L2_value)/100
        print(run,core,L1_hit,L2_hit,100 - (L1_hit + L2_hit),(current_app.loc[(current_app["Core"] == core)]["Hits"] + current_app.loc[(current_app["Core"] == core)]["Misses"]).values[0])


