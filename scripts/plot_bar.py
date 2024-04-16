#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter
import sys

plt.rcParams['axes.axisbelow'] = True
target_color = "#e69f00"
source_color = "#0072B2"
colors = ["#0072B2","#009e73","#e69f00","#009e73","#0072B2","#e69f00","#009e73","#D55E00","grey"]
colors_2 = ["#e69f00","#0072B2","#009e73","#009e73","#0072B2","#e69f00","#009e73","#D55E00","grey"]
font = {'size'   : 16}
plt.rc('font', **font)
plt.rcParams["figure.figsize"] = (12.8,6.4)

res_MCA=[3.575308527,1.37196715,13.10565074,7.080814605,5.922154256,5.146213921]

qws_MCA=[0.7126971259]

if (len(sys.argv) != 2):
   print("ERROR : incorrect usage: ./plot_bar.py <results_projection_file>")
   exit(1)

inputdf = pd.read_csv(sys.argv[1])


def plot_barchart_validation(res,title,filename):
    
    list_appli = res["Appli"].unique()
    n_ticks =len(list_appli)
    N = len(res)
    width = 0.5
    x = np.arange(0,5*n_ticks,5)
    int_width = 0.2
    maxi = 0
    labeled=False
    
    plt.grid(visible=True,axis="y")
    for j in range(n_ticks):
        cursor_app = res[res["Appli"] == list_appli[j]]
        targets = cursor_app["Target"].unique() 
        n_targets = len(targets)
        interval = 2
        target_centers = [x[j] - 3*width,x[j],x[j] + 3*width]
            
        for k in range(3):
            to_plot = []
            cursor_app_target = cursor_app[cursor_app["Target"] == targets[k]]
            for index,row in cursor_app_target.iterrows():
                to_plot.append([row["L1"],row["L2"],row["DRAM"]])
            if not np.isnan(row["gem5"]):
                to_plot.append([row["gem5"]])
            n_bar = len(to_plot)
            if n_bar == 1:
                centers = [target_centers[k]]
            elif n_bar == 2:
                centers = [target_centers[k] - width/2,target_centers[k] + width/2]
            elif n_bar == 3:
                centers = [target_centers[k] - width,target_centers[k],target_centers[k] + width]
            for index in range(n_bar):
                center = centers[index]
                textcenter = center-0.2
                textanchor=max(1,max(to_plot[index]))+0.2
                font={  "size":10,
                        "rotation":90}
                if (max(to_plot[index]) - min(to_plot[index])) > 0.01:  # Its an interval
                    plt.bar(center,np.median(to_plot[index])-1,bottom=1,color=colors[index],width=width)
                    plt.vlines(center,min(to_plot[index]),max(to_plot[index]),colors="black")
                    plt.hlines(min(to_plot[index]),center-int_width,center+int_width,colors="black")
                    plt.hlines(max(to_plot[index]),center-int_width,center+int_width,colors="black")
                    plt.text(textcenter,textanchor,"["+"%.2f" %min(to_plot[index])+","+"%.2f" %max(to_plot[index])+"]x",fontdict=font)
                else:
                    plt.bar(center,np.median(to_plot[index])-1,bottom=1,color=colors[index],width=width)
                    plt.text(textcenter,textanchor,"%.2f" %min(to_plot[index])+"x",fontdict=font)
       
    plt.bar(x[0],0,color=colors[0],label ="Projected interval median")
    plt.bar(x[0],0,color=colors[1],label ="Projected median with scaling")
    plt.bar(x[0],0,color=colors[1],label ="gem5 speedup")
    plt.hlines(x[0],0,0,color="black",label="Projected speedup interval")
    plt.ylabel("Speedup")
    plt.xlabel("Applications")
    plt.title(title)
    plt.xticks(x,list_appli)
    plt.yscale('log')
    plt.vlines([(x[i] + x[i+1])/2 for i in range(len(x)-1)],0.4,12,colors="black",linestyles="dashed")
    yticks = [0.4,0.6,0.8,1,2,3,4,8,12] 
    plt.yticks(yticks,[str(k) for k in yticks])
    plt.scatter(x,res_MCA,marker="^",color="black",s=80,label="MCA speedup")
    for k in range(6):
        if k in [0,4,5]:
            plt.text(x[k]-1,res_MCA[k]+0.2*res_MCA[k],"%.2f"%res_MCA[k]+"x")
        else:
            plt.text(x[k]-1,res_MCA[k]-0.2*res_MCA[k],"%.2f"%res_MCA[k]+"x")
    plt.xlim(-2.5,27.5)
    plt.legend(prop={'size':13},loc='lower right')#,bbox_to_anchor=(0.2,-0.2),loc='upper left')
    plt.savefig(filename,bbox_inches='tight')   
    plt.clf()

def plot_barchart_bigapp(res,title,filename,add_MCA=False):
    list_appli = res["Appli"].unique()
    n_ticks =len(list_appli)
    N = len(res)
    width = 0.5
    x = np.arange(0,5*n_ticks,5)
    int_width = 0.2
    maxi = 0
    labeled=False
    
    plt.grid(visible=True,axis="y")
    for j in range(n_ticks):
        cursor_app = res[res["Appli"] == list_appli[j]]
        targets = cursor_app["Target"].unique() 
        n_targets = len(targets)
        interval = 2
        target_centers = [x[j] - 3*width,x[j],x[j] + 3*width]
            
        for k in range(3):
            to_plot = []
            cursor_app_target = cursor_app[cursor_app["Target"] == targets[k]]
            for index,row in cursor_app_target.iterrows():
                to_plot.append([row["L1"],row["L2"],row["DRAM"]])
            if not np.isnan(row["gem5"]):
                to_plot.append([row["gem5"]])
            n_bar = len(to_plot)
            if n_bar == 1:
                centers = [target_centers[k]]
            elif n_bar == 2:
                centers = [target_centers[k] - width/2,target_centers[k] + width/2]
            elif n_bar == 3:
                centers = [target_centers[k] - width,target_centers[k],target_centers[k] + width]
            for index in range(n_bar):
                center = centers[index]
                textcenter = center-0.2
                textanchor=max(1,max(to_plot[index]))+0.2
                font={  "size":10,
                        "rotation":90}
                if (max(to_plot[index]) - min(to_plot[index])) > 0.01:  # Its an interval
                    plt.bar(center,np.median(to_plot[index])-1,bottom=1,color=colors[index],width=width)
                    plt.vlines(center,min(to_plot[index]),max(to_plot[index]),colors="black")
                    plt.hlines(min(to_plot[index]),center-int_width,center+int_width,colors="black")
                    plt.hlines(max(to_plot[index]),center-int_width,center+int_width,colors="black")
                    plt.text(textcenter,textanchor,"["+"%.2f" %min(to_plot[index])+","+"%.2f" %max(to_plot[index])+"]x",fontdict=font)
                else:
                    plt.bar(center,np.median(to_plot[index])-1,bottom=1,color=colors[index],width=width)
                    plt.text(textcenter,textanchor,"%.2f" %min(to_plot[index])+"x",fontdict=font)

    plt.bar(x[0],0,color=colors[0],label ="Projected interval median")
    #plt.bar(x[0],0,color=colors[1],label ="Projected median with scaling")
    #plt.bar(x[0],0,color=colors[1],label ="gem5 speedup")
    plt.hlines(x[0],0,0,color="black",label="Projected speedup interval")
    plt.ylabel("Speedup")
    plt.xlabel("Applications")
    plt.title(title)
    plt.xticks(x,list_appli)
    plt.yscale('log')
    plt.vlines([(x[i] + x[i+1])/2 for i in range(len(x)-1)],0.4,12,colors="black",linestyles="dashed")
    plt.ylim((0.68,5.8))
    #yticks = [0.4,0.6,0.8,1,2,3,4,8,12] 
    yticks = [0.8,1,2,3,4] 
    #yticks = [1,2,3,4]
    plt.yticks(yticks,[str(k) for k in yticks])
    plt.scatter(x[0],qws_MCA[0],marker="^",color="black",s=80,label="MCA speedup")
    plt.text(x[0]-0.5,qws_MCA[0]+0.1*qws_MCA[0],"%.2f"%qws_MCA[0]+"x")
  
    plt.legend(prop={'size':13},loc='lower right')#,bbox_to_anchor=(0.2,-0.2),loc='upper left')

    plt.savefig(filename,bbox_inches='tight')
    plt.clf()

def plot_barchart_scaling(res,title,filename,add_MCA=False):
    list_appli = res["Appli"].unique()
    n_ticks =len(list_appli)
    N = len(res)
    width = 0.5
    x = np.arange(0,5*n_ticks,5)
    int_width = 0.2
    maxi = 0
    labeled=False
    
    plt.grid(visible=True,axis="y")
    for j in range(n_ticks):
        cursor_app = res[res["Appli"] == list_appli[j]]
        targets = cursor_app["Target"].unique() 
        n_targets = len(targets)
        interval = 2
        target_centers = [x[j] - 3*width,x[j],x[j] + 3*width]
            
        for k in range(3):
            to_plot = []
            cursor_app_target = cursor_app[cursor_app["Target"] == targets[k]]
            for index,row in cursor_app_target.iterrows():
                to_plot.append([row["L1"],row["L2"],row["DRAM"]])
            if not np.isnan(row["gem5"]):
                to_plot.append([row["gem5"]])
            n_bar = len(to_plot)
            if n_bar == 1:
                centers = [target_centers[k]]
            elif n_bar == 2:
                centers = [target_centers[k] - width/2,target_centers[k] + width/2]
            elif n_bar == 3:
                centers = [target_centers[k] - width,target_centers[k],target_centers[k] + width]
            for index in range(n_bar):
                center = centers[index]
                textcenter = center-0.2
                textanchor=max(1,max(to_plot[index]))+0.2
                font={  "size":10,
                        "rotation":90}
                if (max(to_plot[index]) - min(to_plot[index])) > 0.01:  # Its an interval
                    plt.bar(center,np.median(to_plot[index])-1,bottom=1,color=colors_2[index],width=width)
                    plt.vlines(center,min(to_plot[index]),max(to_plot[index]),colors="black")
                    plt.hlines(min(to_plot[index]),center-int_width,center+int_width,colors="black")
                    plt.hlines(max(to_plot[index]),center-int_width,center+int_width,colors="black")
                    plt.text(textcenter,textanchor,"["+"%.2f" %min(to_plot[index])+","+"%.2f" %max(to_plot[index])+"]x",fontdict=font)
                else:
                    plt.bar(center,np.median(to_plot[index])-1,bottom=1,color=colors_2[index],width=width)
                    plt.text(textcenter,textanchor,"%.2f" %min(to_plot[index])+"x",fontdict=font)

    plt.bar(x[0],0,color=colors_2[0],label ="Projected interval median")
    plt.bar(x[0],0,color=colors_2[1],label ="Projected median with scaling")
    plt.bar(x[0],0,color=colors_2[1],label ="gem5 speedup")
    plt.hlines(x[0],0,0,color="black",label="Projected speedup interval")
    plt.ylabel("Speedup")
    plt.xlabel("Applications")
    plt.title(title)
    plt.xticks(x,list_appli)
    plt.yscale('log')
    plt.vlines([(x[i] + x[i+1])/2 for i in range(len(x)-1)],0.4,12,colors="black",linestyles="dashed")
    plt.ylim((0.68,5.8))
    yticks = [0.4,0.6,0.8,1,2,3,4,8,12] 
    plt.yticks(yticks,[str(k) for k in yticks])
    plt.legend(prop={'size':13},loc='lower right')#,bbox_to_anchor=(0.2,-0.2),loc='upper left')

    plt.savefig(filename,bbox_inches='tight')
    plt.clf()

plot_barchart_scaling(inputdf[(inputdf["Appli"] =="CG-OMP") | (inputdf["Appli"] == "FT-OMP")],"Comparison of projection with and with scaling \n of the source thread input on CG-OMP and FT-OMP","figures/projection_scaling.svg")
plot_barchart_bigapp(inputdf[inputdf["Run"] == "bigapp_study"],"Projections on QWS_small, QWS_large, and genesis \n on three target configurations","figures/projection_qws.svg")
plot_barchart_validation(inputdf[inputdf["Run"] == "validation"],"Comparison between model projections, gem5 and MCA \n simulations on the predicted speedup","figures/projection_validation.svg")

