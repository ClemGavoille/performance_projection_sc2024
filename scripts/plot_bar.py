#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter

plt.rcParams['axes.axisbelow'] = True
target_color = "#e69f00"
source_color = "#0072B2"
colors = ["#0072B2","#009e73","#e69f00","#009e73","#0072B2","#e69f00","#009e73","#D55E00","grey"]
#colors = ["#e69f00","#0072B2","#009e73","#009e73","#0072B2","#e69f00","#009e73","#D55E00","grey"]
#font = {'size'   : 16}
#plt.rc('font', **font)
#plt.rcParams["figure.figsize"] = (12.8,6.4)

res_MCA=[5.146213921,13.10565074,5.922154256,7.080814605,1.37196715,3.575308527]
res_MCA=[3.575308527,1.37196715,13.10565074,7.080814605,5.922154256,5.146213921]

qws_MCA=[0.7126971259]
inputdf = pd.read_csv("results_projection.csv")

def plot_barchart(res,labels,title,filename,add_MCA=False):
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
        #    if j == 0:
        #        if (max(res[w]) - min(res[w])) > 0.01:
        #            if (min(res[w]) <= 1 and max(res[w]) <= 1):
        #                plt.bar(center,min(res[w])-1,bottom=1,color=colors[k],width=width,alpha=0.5,hatch="/",label=labels[k])
        #                plt.bar(center,max(res[w])-1,bottom=1,color=colors[k],width=width)
        #            elif (min(res[w]) > 1 and max(res[w]) > 1):
        #                #plt.bar(center,max(res[w])-1,bottom=1,color=colors[k],width=width,alpha=0.5,hatch="/",label=labels[k])
        #                plt.bar(center,np.median(res[w])-1,bottom=1,color=colors[k],width=width,label=labels[k])
        #                plt.vlines(center,min(res[w]),max(res[w]),colors="black",label="Projection interval")
        #                plt.hlines(min(res[w]),center-int_width,center+int_width,colors="black")
        #                plt.hlines(max(res[w]),center-int_width,center+int_width,colors="black")
        #            else:
        #                plt.bar(center,max(res[w])-min(res[w]),bottom=min(res[w]),color=colors[k],width=width,alpha=0.5,hatch="/",label=labels[k])
        #            plt.text(textcenter,textanchor,"["+"%.2f" %min(res[w])+","+"%.2f" %max(res[w])+"]x",fontdict=font)

        #        else :
        #            plt.bar(center,res[w][1]-1,bottom=1,color=colors[k],width=width,label=labels[k])
        #            plt.text(textcenter,textanchor,"%.2f" %max(res[w])+"x",fontdict=font)
        #    else:
        #        if (max(res[w]) - min(res[w])) > 0.01:
        #            if (min(res[w]) <= 1 and max(res[w]) <= 1):
        #                plt.bar(center,min(res[w])-1,bottom=1,color=colors[k],width=width,alpha=0.5,hatch="/")
        #                plt.bar(center,max(res[w])-1,bottom=1,color=colors[k],width=width)
        #            elif (min(res[w]) > 1 and max(res[w]) > 1):
        #                #plt.bar(center,max(res[w])-1,bottom=1,color=colors[k],width=width,alpha=0.5,hatch="/")
        #                plt.bar(center,np.median(res[w])-1,bottom=1,color=colors[k],width=width)
        #                plt.vlines(center,min(res[w]),max(res[w]),colors="black")
        #                plt.hlines(min(res[w]),center-int_width,center+int_width,colors="black")
        #                plt.hlines(max(res[w]),center-int_width,center+int_width,colors="black")
        #            else:
        #                plt.bar(center,max(res[w])-min(res[w]),bottom=min(res[w]),color=colors[k],width=width,alpha=0.5,hatch="/")
        #            plt.text(textcenter,textanchor,"["+"%.2f" %min(res[w])+","+"%.2f" %max(res[w])+"]x",fontdict=font)

        #        else :
        #            plt.bar(center,res[w][1]-1,bottom=1,color=colors[k],width=width)
        #            plt.text(textcenter,textanchor,"%.2f" %max(res[w])+"x",fontdict=font)

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
    if (add_MCA):
        plt.scatter(x,res_MCA,marker="^",color="black",s=80,label="MCA speedup")
        for k in range(6):
            if k in [0,4,5]:
                plt.text(x[k]-1,res_MCA[k]+0.2*res_MCA[k],"%.2f"%res_MCA[k]+"x")
            else:
                plt.text(x[k]-1,res_MCA[k]-0.2*res_MCA[k],"%.2f"%res_MCA[k]+"x")

    #plt.xlim(-2.5,27.5)
    plt.legend(prop={'size':8},loc='lower right')#,bbox_to_anchor=(0.2,-0.2),loc='upper left')
    #plt.bar_label(rects1)
    #plt.bar_label(rects2)
    #plt.show()
    plt.savefig(filename,bbox_inches='tight')
    #plt.savefig(filename+".pdf",bbox_inches='tight')
    plt.clf()

selected_applis = ["CG-OMP","FT-OMP"]
#plot_barchart(inputdf[inputdf["Run"] == "validation"],["HEY"],"Comparison between model projections, gem5 and MCA \n simulations on the predicted speedup","projection_validation.svg",add_MCA=True)
#plot_barchart(inputdf[(inputdf["Appli"] =="CG-OMP") | (inputdf["Appli"] == "FT-OMP")],["HEY"],"Comparison of projection with and with scaling \n of the source thread input on CG-OMP and FT-OMP","projection_scaling.svg")

plot_barchart(inputdf[inputdf["Run"] == "bigapp_study"],["HEY"],"Projections on QWS_small, QWS_large, and genesis \n on three target configurations","projection_qws.svg")
#plot_barchart_qws_gen(res_QWS,["A64FX_S","LARC_C","LARC_A","A64FX_S","LARC_C","LARC_A","A64FX_S","LARC_C","LARC_A"],["Projected speedup median"],"Projected speedup of QWS (small), QWS (large), and genesis \n on 3 target configurations","projection_qws.svg")

