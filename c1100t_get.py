from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display
import os
import re
import time
import json
import argparse

#
# author: jeff calkins
# date: 04-13-2020
# objective: via an automated browser, log into a Technicolor C1100T DSL Modem
# navigate to the the DSL statistics page, scrape specific statistics, and
# write the variables and statistics to a JSON record and log the record for
# future CSV export, visualization and analysis
# 
# environment: raspberry pi 2 model B v 1.1 ... 2014
# Raspbian GNU/Linux 10 (buster) - debian

def refp(astr):
    pfp = re.compile('([-+]?[0-9]*\.?[0-9]+).+')
    result = pfp.search(astr)
    return result.group(1)

def maybe_goheadless(monitor):
    if monitor == 'no':
        display = Display(visible=0, size=(800, 600))
        display.start()

def get_modem(ip):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.binary_location = "/usr/bin/chromium-browser"
    driver = webdriver.Chrome(options=options)
    url = 'http://' + ip
    driver.get(url)
    return driver

def enter_pw(pw):
    ctr = 1
    while ctr < 6:
        try:
            passwordElement = driver.find_element_by_xpath("//input[@id='admin_password']")
            passwordElement.send_keys(pw)
            ctr = 0
            break
        except NoSuchElementException as Exception:
            #print("admin_password  is NOT yet there")
            ctr += 1
            time.sleep(1)
    #showpw_button = driver.find_element_by_id("show_password").click()

def misc():
    #this is misc, data referencing code, i wanted to hang onto (hoard)
    print("attribute('value'):", passwordElement.get_attribute('value'))
    #passwordElement.clear()
    #print("attribute('value'):",usernameElement.get_attribute('value'))
    #showpw_button = driver.find_element_by_xpath("//input[@id='show_password']").click()
    #for a in driver.find_elements_by_xpath('//a'):
        #print(a.get_attribute('href'))
    #print(driver.page_source)

def enter_user(user):
    usernameElement = driver.find_element_by_id("admin_username")
    if usernameElement.get_attribute('value') == user:
        return
    else:
        usernameElement.clear()
        usernameElement.send_keys(user)

def get_dsl_status():
    # the data in the <p> DSL Status and its <table> holds summary information 
    # the DSL Line Status, simply tells you GOOD, POOR, and ???
    # the DSL Downstream and DSL Upstream tell you the configured caps
    # there is SNR, CRC and attenuation stats (dB) also available
    # i'll get these summary stats from other paragraphs.
    #dslUpstream: 0.895 Mbps
    #dslDownstream: 23.103 Mbps
    #dslLineStatus: GOOD
    #print("dslUpstream:",refp(dslUpstreamElement.text), " Mbps")
    #print("dslDownstream:",refp(dslDownstreamElement.text), " Mbps")
    #print("dslLineStatus:", dslLineStatusElement.text)

    ctr = 1
    sample = {}
    while ctr < 4:
        try:
            dslUpstreamElement = driver.find_element_by_xpath("//td[@id='UpStream']")
            sample['dslUpstreamElement'] = float(refp(dslUpstreamElement.text)) 
            ctr = 0
            break
        except NoSuchElementException as Exception:
            #print("transport is NOT yet there")
            ctr += 1
            time.sleep(1)

    if ctr == 0:
        dslDownstreamElement = driver.find_element_by_xpath("//td[@id='DownStream']")
        sample['dslDownstreamElement'] = float(refp(dslDownstreamElement.text))

        dslLineStatusElement = driver.find_element_by_xpath("//td[@id='LineStatus']")
        sample['dslLineStatusElement'] = dslLineStatusElement.text

        return sample
    else:
        sample['dslUpstreamElement'] = -1.0 
        sample['dslDownstreamElement'] = -1.0 
        sample['dslLineStatusElement'] = 'NULL' 
        return sample 

def get_dsl_transport():
    # the data in the <p> DSL Transport </p> and its <table> holds
    # downstream and upstream packet stats, refreshed every ~6 seconds
    # it also holds a calculated downstream and upstream bandwidth usage
    # in Mbits per samples rate???
    # it also holds the network side traffic per minute in Mbps, as well as
    # total traffic over 24 hours.  it may make sense, to come back and recover
    # these data points
    # depending on when one tries to read the tables elements <tr id> & 
    # <td id>, the data may not exist, due to a race condition.  we get
    # around this problem by a "try" to read the <td>, and if the element 
    # is missing, wait for 1 second, and retry to read teh <td> element

    #print("Packets Downstream:", Packets_Downstream.text)
    #print("Packets Upsteam:", Packets_Upstream.text)
    #print("Total_Usage_Downstream:", refp(Total_Usage_Downstream.text))
    #print("Total_Usage_Upstream:", refp(Total_Usage_Upstream.text))
    #Total_Usage: 3185.579 Mbits
    #Packets: 2831756

    sample = {}
    ctr = 1
    while ctr < 4:
        try:
            Packets_Downstream = driver.find_element_by_xpath("//td[@id='msDslTransportTble_@Packets_1']")
            sample['Packets_Downstream'] = int(Packets_Downstream.text)
            ctr = 0
            break
        except NoSuchElementException as Exception:
            #print("transport is NOT yet there")
            ctr += 1
            time.sleep(1)

    if ctr == 0:
        Packets_Upstream = driver.find_element_by_xpath("//td[@id='msDslTransportTble_@Packets_2']")
        sample['Packets_Upstream'] = int(Packets_Upstream.text)

        Total_Usage_Downstream = driver.find_element_by_xpath("//td[@id='msDslTransportTble_@Total_Usage_1']")
        sample['Total_Usage_Downstream'] =  float(refp(Total_Usage_Downstream.text))

        Total_Usage_Upstream = driver.find_element_by_xpath("//td[@id='msDslTransportTble_@Total_Usage_2']")
        sample['Total_Usage_Upstream'] = float(refp(Total_Usage_Upstream.text))

        return sample 
    else:
        sample['Packets_Downstream'] = -1.0 
        sample['Packets_Upstream'] = -1.0 
        sample['Total_Usage_Downstream'] = -1.0 
        sample['Total_Usage_Upstream'] = -1.0 

        return sample 

def get_dsl_channel():
    # the <p>DS Channel</p> and it's table holds CRC and FEC Correction stats for the 
    # near and far end.  I'm not certain, the far end stats are meaningful, as the
    # CMTS would need to transfer this information, to the customer premise modem
    # at this point, i hae only seen near end data
    # this refresh could be every 6-7 seconds
    #RS_FEC: 34992
    #CRC_Errors: 0
    #print("RS_FEC:", RS_FEC.text)
    #print("CRC_Errors:", CRC_Errors.text)

    # this is only Near End ... we're droppying the Far End data

    # this code does NOT wait for find_element_by_xpath, to find an element ... maybe lucky so far???

    sample = {} 

    RS_FEC = driver.find_element_by_xpath("//td[@id='msDslChannelTble_@RS_FEC_Correction_1']")
    sample['RS_FEC'] = int(RS_FEC.text)

    CRC_Errors = driver.find_element_by_xpath("//td[@id='msDslChannelTble_@CRC_Errors_1']")
    sample['CRC_Errors'] =  int(CRC_Errors.text)

    return sample 

def get_dsl_power():
    # the <p> DSL Power paragraph and its <tr> table holds SNR, Power, which
    # are captured, whereas three attenuation stats are available.
    # this dataset appears to refresh every 6 seconds
    #print("SNR_downstream:", refp(SNR_downstream.text),"dB")
    #print("SNR_upstream:", refp(SNR_upstream.text),"dB")
    #print("Power_downstream:", refp(Power_downstream.text),"dbm")
    #print("Power_upstream:", refp(Power_upstream.text),"dbm")

    sample = {}
    ctr = 1
    while ctr < 6:
        try:
            SNR_downstream = driver.find_element_by_xpath("//td[@id='msDslPowerTble_@SNR_1']")
            sample['SNR_downstream'] = float(refp(SNR_downstream.text))
            ctr = 0
            break
        except NoSuchElementException as Exception:
            #print("dsl_power is NOT yet there")
            ctr += 1
            time.sleep(1)

    if ctr == 0:
        SNR_upstream = driver.find_element_by_xpath("//td[@id='msDslPowerTble_@SNR_2']")
        sample['SNR_upstream'] =  float(refp(SNR_upstream.text))

        Power_downstream = driver.find_element_by_xpath("//td[@id='msDslPowerTble_@Power_1']")
        sample['Power_downstream'] = float(refp(Power_downstream.text))

        Power_upstream = driver.find_element_by_xpath("//td[@id='msDslPowerTble_@Power_2']")
        sample['Power_upstream'] =  float(refp(Power_upstream.text))

        return sample 
    else:
        sample['SNR_downstream'] = -1.0 
        sample['SNR_upstream'] =-1.0
        sample['Power_downstream'] = -1.0 
        sample['Power_upstream'] = -1.0

        return sample 

def get_dsl_link():
    # the <p> DSL Link </p> and table holds uptime, train errors and configuration
    # the table appears to refresh, every ~6 seconds
    # am capturing the Link Train Errors, as a likely indicator of line problems
    # also capturing an uptime string in a 12 Days,4H:27M:23S format.
    # not yet parsing the string into a python elapsed time object

    #LinkUptime: 0 Days,13H:14M:21S
    #LinkTrainErrors: 1
    #print("LinkUptime:", LinkUptime.text)
    #print("LinkTrainErrors:", LinkTrainErrors.text)
    
    sample = {}
    ctr = 1
    while ctr < 4:
        try:
            LinkUptime = driver.find_element_by_xpath("//td[@id='LinkUptime']")
            sample['LinkUptime'] =  LinkUptime.text
            ctr = 0
            break
        except NoSuchElementException as Exception:
            #print("LinkUptime is NOT yet there")
            ctr += 1
            time.sleep(1)

    if ctr == 0:
        LinkTrainErrors = driver.find_element_by_xpath("//td[@id='LinkTrainErrors']")
        sample['LinkTrainErrors'] = int(LinkTrainErrors.text)
        return sample
    else:
        sample['LinkUptime'] = 'NULL' 
        sample['LinkTrainErrors'] = -1 
        return sample 

def get_internet_settings():
    # the <p> Internet Settings </p> and table holds Session Time, Packets Sent, Packets Received 
    # 
    # the table appears to refresh, every ~6 seconds
    # //td[@id='sessionTime']
    # 0 Days, 1H:19M:57S
    # //td[@id='packetsSent']
    # 	22938
    # //td[@id='packetsReceived']
    #   61851

    #//td[@id='internetConnection']
    #CONNECTED

    internet_status = ''
    sample = {}
    ctr = 1
    while ctr < 6:
        try:
            internetConnection = driver.find_element_by_xpath("//td[@id='internetConnection']")
            sample['internetConnection'] =  internetConnection.text
            internet_status =  internetConnection.text
            while internetConnection.text != 'CONNECTED':
                time.sleep(1)
                sample['internetConnection'] =  internetConnection.text
                internet_status =  internetConnection.text
            ctr = 0
            break
        except NoSuchElementException as Exception:
            ctr += 1
            time.sleep(1)

    time.sleep(2)
    if ctr == 0 :
        sessionTime = driver.find_element_by_xpath("//td[@id='sessionTime']")
        sample['sessionTime'] =  sessionTime.text

        packetsSent = driver.find_element_by_xpath("//td[@id='packetsSent']")
        sample['packetsSent'] = int(packetsSent.text)
        
        packetsReceived = driver.find_element_by_xpath("//td[@id='packetsReceived']")
        sample['packetsReceived'] = int(packetsReceived.text)

        return sample
    else:
        sample['internetConnection'] = 'NULL' 
        sample['sessionTime'] = 'NULL' 
        sample['packetsSent'] = -1 
        sample['packetsReceived'] = -1 
        return sample 

def gotoInternet():
    ctr = 1
    while ctr < 4:
        try:
            goDsl1Status_button = driver.find_element_by_xpath("//a[@id='internetstatus']").click()
            return 1
        except NoSuchElementException as Exception:
            ctr += 1
            time.sleep(1)
            print("waiting on Internet to load")

    return -1

def gotoUtilities():
    ctr = 1
    while ctr < 4:
        try:
            goDsl1Status_button = driver.find_element_by_xpath("//a[@id='utilitiesMain']").click()
            return 1
        except NoSuchElementException as Exception:
            ctr += 1
            time.sleep(1)
    return -1

def domodemStatusMain():
    ctr = 1
    while ctr < 6:
        try:
            goDsl1Status_button = driver.find_element_by_xpath("//a[@id='modemStatusMain']").click()
            return 1
        except NoSuchElementException as Exception:
            print("waiting for modemStatusMain to become available")
            ctr += 1
            time.sleep(1)
    return -1

def gotoDsl1():
    ctr = 1
    while ctr < 4:
        try:
            goDsl1Status_button = driver.find_element_by_xpath("//a[@id='dslstatus-1']").click()
            return 1
        except NoSuchElementException as Exception:
            ctr += 1
            time.sleep(1)
    return -1

def gotoMain():
    ctr = 1
    while ctr < 6:
        try:
            gomain_button = driver.find_element_by_xpath("//a[@id='ms_mainmenu']").click()
            return 1
        except NoSuchElementException as Exception:
            ctr += 1
            time.sleep(1)
    return -1

def maybeClearDsl1(clear):
    # this button is in the DSL1 screen
    #//a[@class='btn clear-btn']
    # this button is the popup acknowledgement ...
    #//a[@id='popup_ok_btn']

    if clear == 'yes':
        clear_button = driver.find_element_by_xpath("//a[@class='btn clear-btn']").click()
        time.sleep(2)
        popup_ok_button = driver.find_element_by_xpath("//a[@id='popup_ok_btn']").click()
        #print("just cleared DSL1 cumulated stats")
        return 1
    else:
        return 0

def maybeClearInternet(clear):
    # this button is in the INTERNET screen
    #//div[@class='btn clr_btn']
    # this button is the popup acknowledgement ...
    #//a[@id='popup_ok_btn']

    if clear == 'yes':
        clear_button = driver.find_element_by_xpath("//div[@class='btn clr_btn']").click()
        time.sleep(2)
        popup_ok_button = driver.find_element_by_xpath("//a[@id='popup_ok_btn']").click()
        #print("just cleared Internet cumulated stats")
        return 1
    else:
        return 0

def maybeReboot(reboot):
    # this function wings it, in regards to buttons, being loaded.  the click function is waiting on a time.sleep()
    time.sleep(1)
    if reboot == 'yes':
        reboot_button = driver.find_element_by_xpath("//div[@id='reboot_btn']").click()
        time.sleep(2)
        popup_ok_button = driver.find_element_by_xpath("//a[@id='popup_ok_btn']").click()
        return 1
    else:
        return 0

def doLoginButton():
    #don't bother waiting, the usesrname and passwords have waits
    login_button = driver.find_element_by_xpath("//a[@id='login_apply_btn']").click()

def doLogoutButton(reboot):
    if reboot == 'now':
        return 1
    else:
        logout_button = driver.find_element_by_xpath("//a[@id='logout_btn']").click()
        return 0

def gotoResourcetable():
    ctr = 1
    while ctr < 4:
        try:
            goresourcetable_button = driver.find_element_by_xpath("//a[@id='resourcetable']").click()
            return 1
        except NoSuchElementException as Exception:
            ctr += 1
            time.sleep(1)
    return -1
# //a[@id='resourcetable']
# //tbody[@id='device_log_tablebody']
# //td[@id='device_log_table_3125_0']    device
# //td[@id='device_log_table_3125_1']    protocol
# //td[@id='device_log_table_3125_2']    destination_ip 
# //td[@id='device_log_table_3125_3']    sessions 
# //td[@id='device_log_table_3125_4']    packets_tx
# //td[@id='device_log_table_3125_5']    packets_rx
# 

def get_resourcetable(ts):


    time.sleep(5)
    # the device_log_tablebody seems to load immediately, it is however
    # empty, immediately after going into the resourcetable screen
    thing_size = 0
    counter = 0
    while thing_size == 0:
        counter += 1
        aThing = driver.find_element_by_xpath("//p[contains(text(),'LAN Device Log')]")
        thing_size = len(aThing.text)
        time.sleep(1)

    aTable = driver.find_element_by_xpath("//tbody[@id='device_log_tablebody']")

    hey = aTable.text
    stuff = list(hey.splitlines())
    #print("found x rows:", len(stuff))
    
    keys = ['device', 'protocol', 'destinationIp', 'sessions', 'pcktTx', 'pcktRx']
    stats = {}
    allEps = list()
    json_fname = "jsonEndpoint.txt"
    fo = open(json_fname, "a+")

    i = 0
    for row in stuff:
        arow = list()
        arow = row.split(" ")
        j = 0
        for varx in arow:
            stats[keys[j]] = varx  
            j += 1
        #print(i, row, arow, stats,  "******"), 
        data = {}
        data[ts0] = stats
        data_json = json.dumps(data) + '\n'
        fo.write(data_json)
        i += 1

    # //a[@id='resourcetable']
    # //tbody[@id='device_log_tablebody']
    # //td[@id='device_log_table_3125_0']    device

    # iterate over all the rows
    # this is very compute intensive, finding each row and
    # parsing the text result ... giving-up on this
    #i = 0
    #raw = list()
    #for row in aTable.find_elements_by_xpath(".//tr"):
        #print("row:", i, row.text)
        #raw[i] = row.text
        #i += 1
        #raw.append(row.text)
        #print([td.text for td in row.find_elements_by_xpath(".//td[@class='dddefault'][1]"])
        #print([td.text for td in row.xpath(".//td[@id='device_log_table_*']"[text()]))

    fo.close()
    #print("waited for endpoints for ", counter, "seconds and got: ", i, "rows" )
    return i 

# .............................................................................

json_fname = "jsonTest.txt"
json_fname = "json_c1100t.txt"

data = {}
samples = {}

# change the below, and they become your passline defaults.  you can always 
# override these variables on the passline
# from a security perspective, you can hard code your password here, or you
# can call this application, and pass the password on the command line
# your call
password = 'CHANGEMETOYOURMODEMPASSWORD'
password = 'uxWxrj5g@'
ip = '192.168.0.1'
username = 'admin'
reboot = 'no'
monitor = "no"
clear = 'no'

parser = argparse.ArgumentParser()
parser.add_argument('-u', default=username, help="username")
parser.add_argument('-i', default=ip, help="ip")
parser.add_argument('-p', default=password, help="password")
parser.add_argument('-r', default=reboot, help="reboot")
parser.add_argument('-m', default=monitor, help="monitor")
parser.add_argument('-c', default=clear, help="clear stats")

args = parser.parse_args()

username = args.u
ip = args.i
password = args.p
reboot = args.r
monitor = args.m
clear = args.c

result = os.system("pkill chromedriver")
result = os.system("pkill chromium")
result = os.system("pkill Xvfb")

ts0 = int(round(time.time() * 1000))

maybe_goheadless(monitor)

driver = get_modem(ip)

enter_pw(password)
enter_user(username)
doLoginButton()

gotoMain()
time.sleep(1)
domodemStatusMain()

gotoDsl1()
samples.update(get_dsl_power())
samples.update(get_dsl_transport())
samples.update(get_dsl_status())
samples.update(get_dsl_link())
samples.update(get_dsl_channel())
maybeClearDsl1(clear)

gotoInternet()
samples.update(get_internet_settings())
maybeClearInternet(clear)

gotoResourcetable()
eptcount = get_resourcetable(ts0)

gotoUtilities()
maybeReboot(reboot)

ts1 = int(round(time.time() * 1000))
delta_ts = ts1 - ts0

doLogoutButton(reboot)
time.sleep(1)

driver.close()
driver.quit()

data[ts0] = samples      # all the samples in that dict, are the value to the ts0 index
data_json = json.dumps(data) + '\n'
fo = open(json_fname, "a+")
fo.write(data_json)
fo.close()

result = os.system("pkill Xvfb")
