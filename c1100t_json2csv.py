import os
import json
import csv

# author: jeff calkins
# date: 04-15-2020
# objective: parse a json file, where each object is indexed by a millisecond (ms)
# timestamp (ts), and is written to a CSV file
# JSON input file: json_c1100t.txt
# CSV output file: out.csv

# the application is hard coded, to recover all the variables in the list 'use'
# the initial list 'use' is complete, and one can remove variables, one at a time
# using the list.remove() method.  see the remove example below

# use the following data columns, and use in this order
use = ['SNR_downstream',
       'SNR_upstream',
       'Power_downstream',
       'Power_upstream',
       'Packets_Downstream',
       'Packets_Upstream',
       'Total_Usage_Downstream',
       'Total_Usage_Upstream',
       'dslDownstreamElement',
       'dslUpstreamElement',
       'dslLineStatusElement',
       'LinkUptime',
       'LinkTrainErrors',
       'RS_FEC',
       'CRC_Errors'
]
use.remove('LinkUptime')

def build_header(columns):

    heading = list()
    heading.append("ts")
    
    for column in columns:
        heading.append(column)

    return heading
    
with open ("json_c1100t.txt", "r") as fh, open("out.csv", "w", newline="") as fcsv:
    writer = csv.writer(fcsv)

    heading = build_header(use)
    writer.writerow(heading)
    #print("heading", heading)
    
    for line in fh:        
        result = json.loads(line)
        ts = list(result)[0]
        samples = result[ts]
        
        row = list()
        row.append(ts)

        for column_name in use:
            row.append(samples[column_name])
            
        writer.writerow(row)            
