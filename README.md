# scrape_dsl_modem_stats
scrape C1100T DSL modem stats with the python selenium module

#### the following installation is for a Raspberry Pi (RPI)
This can run on an older RPI 2  

#### Environmental Assumptions:  
1. RPI OS installed was: "Raspbian GNU/Linux 10 (buster)"
1. The desktop was installed, with the default chromium web browser
2. You should be able to browse to and login to the C1100T DSL CenturyLink modem from the RPI  
3. the RPI basic install includes:  
+ python3 Python 3.7.3 (default, Dec 20 2019, 18:57:59  
+ pip3  

This install will allow you to run your RPI in a headless manner.  The RPI has an HDMI and analog video, but this application doesn't require video out hardware, or video monitors. The headless environment is applicable when implementing this application on a server, without video hardware e.g. a cloud server.  

<https://en.wikipedia.org/wiki/Xvfb> (a dummy X11 display server)  
<http://elementalselenium.com/tips/38-headless> an xvfb reference  

This application controls the RPI chromium web browser, as if a user were surfing, using the keyboard and mouse.  The chromedriver is a google chrome API, that allows programmatic control over their browser.  

ssh into the pi account, or use the desktop terminal to:

`sudo apt-get update`  
`sudo apt-get upgrade`  
`sudo apt-get install xvfb`
`sudo pip3 install pyvirtualdisplay` 
`sudo apt-get install chromium-chromedriver`  
`pip3 install -U selenium`  
 

