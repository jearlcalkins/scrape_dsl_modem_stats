from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display
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

data = {}
samples = {}
units = {}


def refp(astr):
    pfp = re.compile('([-+]?[0-9]*\.?[0-9]+).+')
    result = pfp.search(astr)
    return result.group(1)

def goheadless():
    display = Display(visible=0, size=(800, 600))
    display.start()

def get_modem(ip):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.binary_location = "/usr/bin/chromium-browser"
    driver = webdriver.Chrome(options=options)
    driver.get('http://192.168.0.1')
    return driver

def enter_pw(pw):
    ctr = 1
    while ctr < 6:
        try:
            passwordElement = driver.find_element_by_xpath("//input[@id='admin_password']")
            passwordElement.send_keys("uxWxrj5g")
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

    results = list()
    ctr = 1
    while ctr < 4:
        try:
            dslUpstreamElement = driver.find_element_by_xpath("//td[@id='UpStream']")
            results.append(float(refp(dslUpstreamElement.text)))
            samples['dslUpstreamElement'] = float(refp(dslUpstreamElement.text)) 
            ctr = 0
            break
        except NoSuchElementException as Exception:
            #print("transport is NOT yet there")
            ctr += 1
            time.sleep(1)

    if ctr == 0:
        dslDownstreamElement = driver.find_element_by_xpath("//td[@id='DownStream']")
        results.append(float(refp(dslDownstreamElement.text)))
        samples['dslDownstreamElement'] = float(refp(dslDownstreamElement.text))

        dslLineStatusElement = driver.find_element_by_xpath("//td[@id='LineStatus']")
        results.append(dslLineStatusElement.text)
        samples['dslLineStatusElement'] = dslLineStatusElement.text

        return results
    else:
        samples['dslUpstreamElement'] = -1.0 
        samples['dslDownstreamElement'] = -1.0 
        samples['dslLineStatusElement'] = 'NULL' 
        return [-1.0, -1.0, 'NULL']


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
    results = list()
    ctr = 1
    while ctr < 4:
        try:
            Packets_Downstream = driver.find_element_by_xpath("//td[@id='msDslTransportTble_@Packets_1']")
            results.append(int(Packets_Downstream.text))
            samples['Packets_Downstream'] = int(Packets_Downstream.text)
            ctr = 0
            break
        except NoSuchElementException as Exception:
            #print("transport is NOT yet there")
            ctr += 1
            time.sleep(1)

    if ctr == 0:
        Packets_Upstream = driver.find_element_by_xpath("//td[@id='msDslTransportTble_@Packets_2']")
        results.append(int(Packets_Upstream.text))
        samples['Packets_Upstream'] = int(Packets_Upstream.text)

        Total_Usage_Downstream = driver.find_element_by_xpath("//td[@id='msDslTransportTble_@Total_Usage_1']")
        results.append(float(refp(Total_Usage_Downstream.text)))
        samples['Total_Usage_Downstream'] =  float(refp(Total_Usage_Downstream.text))

        Total_Usage_Upstream = driver.find_element_by_xpath("//td[@id='msDslTransportTble_@Total_Usage_2']")
        results.append(float(refp(Total_Usage_Upstream.text)))
        samples['Total_Usage_Upstream'] = float(refp(Total_Usage_Upstream.text))

        return results
    else:
        return [-1.0, -1.0, -1.0, -1.0]


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

    results = list()

    RS_FEC = driver.find_element_by_xpath("//td[@id='msDslChannelTble_@RS_FEC_Correction_1']")
    results.append(int(RS_FEC.text))
    samples['RS_FEC'] = int(RS_FEC.text)

    CRC_Errors = driver.find_element_by_xpath("//td[@id='msDslChannelTble_@CRC_Errors_1']")
    results.append(int(CRC_Errors.text))
    samples['CRC_Errors'] =  int(CRC_Errors.text)

    return results

def get_dsl_power():
    # the <p> DSL Power paragraph and its <tr> table holds SNR, Power, which
    # are captured, whereas three attenuation stats are available.
    # this dataset appears to refresh every 6 seconds
    #print("SNR_downstream:", refp(SNR_downstream.text),"dB")
    #print("SNR_upstream:", refp(SNR_upstream.text),"dB")
    #print("Power_downstream:", refp(Power_downstream.text),"dbm")
    #print("Power_upstream:", refp(Power_upstream.text),"dbm")

    results = list()
    ctr = 1
    while ctr < 6:
        try:
            SNR_downstream = driver.find_element_by_xpath("//td[@id='msDslPowerTble_@SNR_1']")
            results.append(float(refp(SNR_downstream.text)))
            samples['SNR_downstream'] = float(refp(SNR_downstream.text))
            ctr = 0
            break
        except NoSuchElementException as Exception:
            #print("dsl_power is NOT yet there")
            ctr += 1
            time.sleep(1)

    if ctr == 0:
        SNR_upstream = driver.find_element_by_xpath("//td[@id='msDslPowerTble_@SNR_2']")
        results.append(float(refp(SNR_upstream.text)))
        samples['SNR_upstream'] =  float(refp(SNR_upstream.text))

        Power_downstream = driver.find_element_by_xpath("//td[@id='msDslPowerTble_@Power_1']")
        results.append(float(refp(Power_downstream.text)))
        samples['Power_downstream'] = float(refp(Power_downstream.text))

        Power_upstream = driver.find_element_by_xpath("//td[@id='msDslPowerTble_@Power_2']")
        results.append(float(refp(Power_upstream.text)))
        samples['Power_upstream'] =  float(refp(Power_upstream.text))

        return results
    else:
        samples['SNR_downstream'] = -1.0 
        samples['SNR_upstream'] =-1.0
        samples['Power_downstream'] = -1.0 
        samples['Power_upstream'] = -1.0

        return [-1.0, -1.0, -1.0, -1.0] 

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
    
    results = list()
    ctr = 1
    while ctr < 4:
        try:
            LinkUptime = driver.find_element_by_xpath("//td[@id='LinkUptime']")
            results.append(LinkUptime.text)
            samples['LinkUptime'] =  LinkUptime.text
            ctr = 0
            break
        except NoSuchElementException as Exception:
            #print("LinkUptime is NOT yet there")
            ctr += 1
            time.sleep(1)

    if ctr == 0:
        LinkTrainErrors = driver.find_element_by_xpath("//td[@id='LinkTrainErrors']")
        results.append(int(LinkTrainErrors.text))
        samples['LinkTrainErrors'] = int(LinkTrainErrors.text)
        return results
    else:
        samples['LinkUptime'] = 'NULL' 
        samples['LinkTrainErrors'] = -1 
        return ['Null', -1]


def doMain():

    ctr = 1
    while ctr < 6:
        try:
            gomain_button = driver.find_element_by_xpath("//a[@id='ms_mainmenu']").click()
            return 1
        except NoSuchElementException as Exception:
            #print("gomain_button is NOT yet there")
            ctr += 1
            time.sleep(1)
    return -1

def doDsl1():

    ctr = 1
    while ctr < 4:
        try:
            goDsl1Status_button = driver.find_element_by_xpath("//a[@id='dslstatus-1']").click()
            return 1
        except NoSuchElementException as Exception:
            #print("goDsl1Status_button is NOT there")
            ctr += 1
            time.sleep(1)

    return -1

parser = argparse.ArgumentParser()
parser.add_argument('-u', default='admin', help="username")
parser.add_argument('-p', required=True, help="password")
args = parser.parse_args()
username = args.u
password = args.p

goheadless()

driver = get_modem('192.168.0.1')
enter_pw(password)
enter_user(username)
login_button = driver.find_element_by_xpath("//a[@id='login_apply_btn']").click()
doMain()
doDsl1()

ts0 = int(round(time.time() * 1000))
dsl_power_results = get_dsl_power()
dsl_transport_results = get_dsl_transport()
dsl_status_results = get_dsl_status()
dsl_link_results = get_dsl_link()
dsl_channel_results = get_dsl_channel()
ts1 = int(round(time.time() * 1000))
delta_ts = ts1 - ts0

final = dsl_power_results + dsl_transport_results + dsl_status_results + dsl_link_results + dsl_channel_results
final.insert(0, ts0)

time.sleep(1)
logout_button = driver.find_element_by_xpath("//a[@id='logout_btn']").click()
driver.close()
driver.quit()

data[ts0] = samples      # all the samples in that dict, are the value to the ts0 index
data_json = json.dumps(data) + '\n'
fo = open("json_c1100t.txt", "a+")
fo.write(data_json)
fo.close()
