# author: jeff calkins
# date: 06-09-2020
# objective: plot time series of DSL modem and router stats, providing insight
# into how-well the DSL modem and plant are performing
# the datasets are dirty, and the data was cleaned-up by capping datapoints to
# a threshold
# 
# threshold(aDF,cap):
# the threshold outliers, exceeding the cap variable,  were reset to the
# previous datapoint:
# X(n) = X(n+1) where the X(n) data point exceeded the threshold
# 
# cappeak(aDF,cap):
# the threshold outliers, exceeding the cap varialbe, were reset to NaN
#
# derivative(aDF):
# the first derivative was used to calculate the rate of a time series.
# simply plotting, increasing packet counts, is not a helpful visualization
# however plotting the packet rate increases and decreases, are a view into
# bandwidth usage.  This algorith also looked at the rates and when exceeding
# an anecdotal threshold were capped.  This "rate cap" was a filter, removing
# many data spikes.
# there is likelihood, the spike data is real, and not attributed to the
# modem/router firmware, or slow sample rates

# environment: raspberry pi 2 model B v 1.1 ... 2014
# Raspbian GNU/Linux 10 (buster) - debian

import pandas as pd
import numpy as np
import os
import csv
import matplotlib as mpl

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

def derivative(aDF):
    # function takes a 'series' (column) and calculates the first derivative, leaving
    # the derivative in a list
    # as the function iterates through the series, a derivative threshold caps
    # spurious data points.  these spurious data points are likely a modem
    # firmware issue, but they could be symptomatic of a plant-modem issue
    # the function returns the capped derivative list

    std_deviation =  aDF.std()
    alist = list(aDF)
    #print('aDF', type(aDF), aDF.name)

    derivative_list = []
    derivative_list.insert(0, 0.0)
    i = 1
    length = len(alist)
    while i < length:
        delta = alist[i] - alist[i-1]
        if delta < 0.0:
            delta = 0.0
        elif delta > .5 * std_deviation:
            delta = 0.0

        derivative_list.insert(i, delta)
        i += 1
    return derivative_list

def threshold(aDF,cap):
    # function takes a 'series' (column) and replaces data points exceeding
    # a threshold, with the previous datapoint
    # after the function iterates through the series (list), capping
    # spurious data points.  
    # these spurious data points are likely a modem
    # firmware issue, but they could be symptomatic of a plant-modem issue
    # the function returns the capped derivative list

    #print( aDF.mean(), aDF.name)
    alist = list(aDF)

    threshold_list = []
    threshold_list.insert(0, alist[0])
    i = 1
    cap_ctr = 0
    length = len(alist)
    while i < length:
        if alist[i] < 0.0:
            alist[i] = np.nan
        if alist[i] > cap:
            cap_ctr += 1
            #print("over cap", aDF.name, i, cap_ctr, "value:",  alist[i], "cap:", cap, aDF.mean(), aDF.std())
            fix_value = alist[i-1]
        else:
            fix_value = alist[i]

        threshold_list.insert(i, fix_value)
        i += 1

    print(aDF.name, "threshold fixed record ct:", cap_ctr)
    return threshold_list

def cappeak(aDF,cap):
    # function takes a 'series' (column) and replaces data points exceeding
    # a threshold, with NaN 

    #print( aDF.mean(), aDF.name)
    alist = list(aDF)

    threshold_list = []
    i = 0
    cap_ctr = 0
    length = len(alist)
    while i < length:
        fix_value = alist[i]
        if alist[i] > cap:
            fix_value = np.nan
            fix_value = cap
            cap_ctr += 1
            #print("over cap", aDF.name, i, cap_ctr, "value:",  alist[i], "cap:", cap)

        threshold_list.insert(i, fix_value)
        i += 1
    print(aDF.name, "over cap fixed data pts:", cap_ctr)

    return threshold_list

modem_stats = pd.read_csv('out.csv',index_col=0,error_bad_lines=False)
modem_stats.index = pd.to_datetime((modem_stats.index.values), unit = 'ms')

modem_stats.rename(columns = {'RS_FEC':'FECs'}, inplace = True)
modem_stats.rename(columns = {'CRC_Errors':'CRCs'}, inplace = True)
modem_stats.rename(columns = {'LinkTrainErrors':'TRAINerrs'}, inplace = True)
modem_stats.rename(columns = {'SNR_downstream':'SNRD'}, inplace = True)
modem_stats.rename(columns = {'SNR_upstream':'SNRU'}, inplace = True)
modem_stats.rename(columns = {'Power_downstream':'PowerD'}, inplace = True)
modem_stats.rename(columns = {'Power_upstream':'PowerU'}, inplace = True)
modem_stats.rename(columns = {'Total_Usage_Downstream':'TotalD'}, inplace = True)
modem_stats.rename(columns = {'Total_Usage_Upstream':'TotalU'}, inplace = True)
modem_stats.rename(columns = {'Packets_Downstream':'PktsD'}, inplace = True)
modem_stats.rename(columns = {'Packets_Upstream':'PktsU'}, inplace = True)
modem_stats.rename(columns = {'packetsReceived':'pktsR'}, inplace = True)
modem_stats.rename(columns = {'packetsSent':'pktsS'}, inplace = True)

#print("shape:", modem_stats.shape)
#print(modem_stats.head(2))
#print(modem_stats.tail(3))
#print('dtypes:', modem_stats.dtypes)
#print('index:', modem_stats.index)

#print('SNRU ***', modem_stats['SNRU'].mean(), modem_stats['SNRU'].std(), modem_stats['SNRU'].describe() )
cap = modem_stats['SNRU'].mean() + modem_stats['SNRU'].std() * 3.0
modem_stats['SNRU'] = threshold(modem_stats['SNRU'], cap )

#print('pktsR ***', modem_stats['pktsR'].mean(), modem_stats['pktsR'].std(), modem_stats['pktsR'].describe() )
cap = modem_stats['pktsR'].mean() + modem_stats['pktsR'].std() * 3.0
modem_stats['pktsR'] = threshold(modem_stats['pktsR'], cap )

#print('PktsD ***', modem_stats['PktsD'].mean(), modem_stats['PktsD'].std(), modem_stats['PktsD'].describe() )
cap = modem_stats['PktsD'].mean() + modem_stats['PktsD'].std() * 3.0
modem_stats['PktsD'] = threshold(modem_stats['PktsD'], cap )

#print('pktsS ***', modem_stats['pktsS'].mean(), modem_stats['pktsS'].std(), modem_stats['pktsS'].describe() )
cap = modem_stats['pktsS'].mean() + modem_stats['pktsS'].std() * 3.0
modem_stats['pktsS'] = threshold(modem_stats['pktsS'], cap )

#print('PktsU ***', modem_stats['PktsU'].mean(), modem_stats['PktsU'].std(), modem_stats['PktsU'].describe() )
cap = modem_stats['PktsU'].mean() + modem_stats['PktsU'].std() * 3.0
modem_stats['PktsU'] = threshold(modem_stats['PktsU'], cap )

#print('TotalD ***', modem_stats['TotalD'].mean(), modem_stats['TotalD'].std(), modem_stats['TotalD'].describe() )
cap = modem_stats['TotalD'].mean() + modem_stats['TotalD'].std() * 3.0
modem_stats['TotalD'] = threshold(modem_stats['TotalD'], cap )

modem_stats['FECs'] = cappeak(modem_stats['FECs'], 150000 )

modem_stats['TotalD'] = derivative(modem_stats['TotalD'])
modem_stats['pktsR'] = derivative(modem_stats['pktsR'])
modem_stats['PktsD'] = derivative(modem_stats['PktsD'])
modem_stats['TotalU'] = derivative(modem_stats['TotalU'])
modem_stats['pktsS'] = derivative(modem_stats['pktsS'])
modem_stats['PktsU'] = derivative(modem_stats['PktsU'])

#print(modem_stats.describe())

sns.set(rc={'figure.figsize':(10, 16)})       # screen size here

#             'FECs', 'CRCs', 'TRAINerrs',
cols_plot = [
             'TotalD', 'PktsD', 'SNRD', 'PowerD', 
             'TotalU', 'PktsU', 'SNRU', 'PowerU', 'FECs'
]

fig, axes = plt.subplots(len(cols_plot), 1, figsize=(15,25), sharex=True)
modem_stats[cols_plot].plot(subplots=True, ax=axes)

for ax, col in zip(axes, cols_plot):
    #ax.axhline(0, color='k', linestyle='-', linewidth=1) # the 0 horizontal line
    #ax.set_title("C1100T stats: "+col)
    # add axis labels
    ax.set_xlabel("time"+"\n"+"C1100T Technicolor stats")
    # add legend
    ax.legend(loc='upper left', fontsize=11, frameon=True).get_frame().set_edgecolor('blue')

plt.tight_layout()
plt.show()
