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

use_internet = ['internetConnection',
                'sessionTime',
                'packetsSent',
                'packetsReceived'
]
use += use_internet
use.remove('LinkUptime')

# {"1587659403469": {"SNR_downstream": 10.3, "SNR_upstream": 7.4, "Power_downstream": 17.0, "Power_upstream": 7.9, "Packets_Downstream": 10147868, "Packets_Upstream": 6454110, "Total_Usage_Downstream": 104506.279, "Total_Usage_Upstream": 6230.998, "dslUpstreamElement": 0.895, "dslDownstreamElement": 23.103, "dslLineStatusElement": "GOOD", "LinkUptime": "1 Days,13H:21M:3S", "LinkTrainErrors": 1, "RS_FEC": 118118, "CRC_Errors": 5, "internetConnection": "CONNECTED", "sessionTime": "1 Days, 12H:48M:51S", "packetsSent": 443713, "packetsReceived": 432835}}

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
    
    for line in fh:        
        result = json.loads(line)
        ts = list(result)[0]
        samples = result[ts]
        
        row = list()
        row.append(ts)

        value_previous = -1
        for column_name in use:
            try:
                value = samples[column_name]
                row.append(value)
            except KeyError as Exception:
                row.append("NaN")
            
        writer.writerow(row)            
