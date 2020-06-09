# scrape_dsl_modem_stats
scrape C1100T DSL modem stats with the python selenium module.  the applcation is: c1100t_get.py

#### Logged Data  
everytime the c1100t_get.py application successfully runs and scrapes the dsl modem data, the data will be logged as a JSON record, and appended to the **json_c1100t.txt** file.  The following is a single JSON dataset example:  

*`{"1586973621148": {"SNR_downstream": 10.4, "SNR_upstream": 7.9, "Power_downstream": 16.9, "Power_upstream": 8.3, "Packets_Downstream": 14184969, "Packets_Upstream": 7311236, "Total_Usage_Downstream": 142108.65, "Total_Usage_Upstream": 8267.947, "dslUpstreamElement": 0.895, "dslDownstreamElement": 23.103, "dslLineStatusElement": "GOOD", "LinkUptime": "3 Days,0H:29M:55S", "LinkTrainErrors": 1, "RS_FEC": 242868, "CRC_Errors": 0}}`*  

The record is key'd to epoch time in milliseconds (ms).  In this example, the 1586973621148 time is: 03/12/52259 @ 5:52am (UTC)  
The following variables are available, along with recently scrapped dls modem data:
1586973621148 (timestamp key for the following variables  
1. SNR_downstream 10.4  
2. SNR_upstream 7.9  
3. Power_downstream 16.9  
4. Power_upstream 8.3  
5. Packets_Downstream 14184969  
6. Packets_Upstream 7311236  
7. Total_Usage_Downstream 142108.65  
8. Total_Usage_Upstream 8267.947  
9. dslUpstreamElement 0.895  
10. dslDownstreamElement 23.103  
11. dslLineStatusElement GOOD  
12. LinkUptime 3 Days,0H:29M:55S  
13. LinkTrainErrors 1  
14. RS_FEC 242868  
15. CRC_Errors 0  

Will be publishing a JSON to CSV application, **c1100t_json2csv.py**.  The application will convert **json_c1100t.txt** to **out.txt**  

the following is a 4 record snippet of the out.txt CSV file:  
`ts,SNR_downstream,SNR_upstream,Power_downstream,Power_upstream,Packets_Downstream,Packets_Upstream,Total_Usage_Downstream,Total_Usage_Upstream,dslDownstreamElement,dslUpstreamElement,dslLineStatusElement,LinkTrainErrors,RS_FEC,CRC_Errors
1586713519097,10.3,8.5,16.9,8.6,47770,24521,475.615,29.162,23.103,0.895,GOOD,1,331,0
1586714418799,10.3,8.4,16.9,8.6,80778,46330,805.77,46.372,23.103,0.895,GOOD,1,893,0
1586715321058,10.3,8.3,16.9,8.6,153647,75193,1592.121,76.125,23.103,0.895,GOOD,1,1332,0
1586716219264,10.3,8.4,16.9,8.6,203270,93556,2136.278,96.844,23.103,0.895,GOOD,1,2026,0`

#### the following installation is for a Raspberry Pi (RPI)
Am currently running this on an older RPI 2  

#### Environmental Assumptions:  
1. RPI OS installed was: "Raspbian GNU/Linux 10 (buster)"
1. The desktop was installed, with the default chromium web browser
2. You should be able to browse to and login to the C1100T DSL CenturyLink modem from the RPI  
3. the RPI basic install includes:  
+ python3 Python 3.7.3 (default, Dec 20 2019, 18:57:59  
+ pip3  

#### Background on "headless" operations:  

This install will allow you to run your RPI in a headless manner. The RPI has an HDMI and analog video, but this application doesn't require video out hardware, or video monitors. The headless environment is applicable when implementing this application on a server, without video hardware e.g. a cloud server.  

<https://en.wikipedia.org/wiki/Xvfb> (a dummy X11 display server)  
<http://elementalselenium.com/tips/38-headless> an xvfb reference  

This application controls the RPI chromium web browser, as if a user were surfing, using the keyboard and mouse. The chromedriver is a google chrome API, that allows programmatic control over their browser.  

If you want to turn-off headless operations, you can watch the application start the browser, go the modem (site) and navigate to the page holding the DSL variables, then logout. It's fun to watch the application take control of the browser. Watching the application, is often helpful when troubleshooting issues.  

#### Install the applicaton
ssh into the pi account, or use the desktop terminal to:

`sudo apt-get update`  
`sudo apt-get upgrade`   
`sudo apt-get install xvfb`      
`sudo pip3 install pyvirtualdisplay`      
`sudo apt-get install chromium-chromedriver`     
`pip3 install -U selenium`
 
#### Download the code
goto this link and hit the clone or download button:  
https://github.com/jearlcalkins/scrape_dsl_modem_stats  

or
 
from a terminal session, run the following cmd:  
`wget https://github.com/jearlcalkins/scrape_dsl_modem_stats/blob/master/c1100t_get.py`  

#### a tweak to the code
if you want to put your password, in the application code, you won't have to pass the password, when you call the application  

edit the c1100t_get.py file  
1. go to line 521
2. edit the line and enter your modem admin password, where it says "CHANGEMETO ..."  

#### how-to run examples  
view the pass variable options:
`python3 c1100t_get.py -h`  

run the application, taking default modem IP, username: admin, password: (what is on line 24)  
`python3 c1100t_get.py`

run the application, passing the modem's password 'G0CUBz':  
`python3 c1100t_get.py -p G0CUBz`  

run the application from the crontab
`0,30 * * * * python3 c1100t_get.py -i 192.168.0.1`
`2,32 * * * * python3 c1100t_json2csv.py`
`35 1 * * * python3 c1100t_getv3.py -r yes -c yes` 
The modem will be scraped at the top (0) and bottom half (30) of the hour, every hour (c1100t_get.py)
The json log file (json_c1100t.txt) will be converted to a csv file (out.csv) at 2 minutes and 32 minutes after the hour, every hour (c110t_json2csv.py)
The modem will be restarted (-r yes) and the modem-router stats will be cleared to 0s (-c yes) (c1100t_get.py) 

BTW, I found a bash shell issue when passing a password, that happened to contain a '!' (aka a bang), followed by a number.  When passing a password like: 'Clxy!123', bash passed the application 'Clxy', then looked-up the 123rd line of bash history, and passed that command to the python applicaton. The application was confused and crashed, when it was passed 'Clxy' and a historical bash command.  Because I like '!' special characters in my passwords, this caused problems and led me to hardcoding the password, in the application code.

#### TimeSeries for packets, SNR and power

The plant or DSLAM equipment, or possibly the DSLAM modem configs could be problematic.  There are periodic outages, seemingly tied to drops in SNR and power, during days of rain.  The packet data is quite bursty, suggesting possible times where there are excessive packet retries. The FEC (forward error correction) counts can see 80K daily counts, before the modem is rebooted nightly. Some days the modem will see FEC bursts and >150K FEC counts a day. 

![TimeSeries packet, SNR, power](https://github.com/jearlcalkins/scrape_dsl_modem_stats/blob/master/DSLmodemstats.png)

