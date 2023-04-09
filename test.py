from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from time import sleep
import time

#--| Function test
#1 : Green profit not found OR containers not found for container_open
#2 : Works as intended, but did not find what we wanted
#“” : Just no profit found


#test container_open
def test_container_open(driver):
    # On random page
    driver.get("https://www.google.com/search?client=opera-gx&q=google+traduction&sourceid=opera&ie=UTF-8&oe=UTF-8")
    sleep(4)
    print(container_open() == [])
    # On 1x2 page
    driver.get("https://www.oddsportal.com/basketball/bulgaria/nbl/beroe-rilski-sportist-UZ823qD3/#1X2;2")
    sleep(4)
    print(container_open() == [])

    # On Under/Over page OPEN
    driver.get("https://www.oddsportal.com/basketball/brazil/nbb/minas-paulistano-htxX8KaS/#over-under;1;155.50;0")
    sleep(4)
    print(container_open() != [])

    # On Under/Over page CLOSED
    #FIXME : work is good, but filter faulty
    driver.get("https://www.oddsportal.com/volleyball/bulgaria/superliga/neftohimic-burgas-pirin-razlog-Aa1R2YPA/#over-under;2")
    sleep(4)
    print(container_open() != [])

#test container_find
def test_container_find(driver):
    # On random page
    driver.get("https://www.google.com/search?client=opera-gx&q=google+traduction&sourceid=opera&ie=UTF-8&oe=UTF-8")
    print(container_find("1x2") == "1")
    print(container_find("Home/Away") == "1")
    print("\n")
    #print(container_find("Over/Under") == "1")

    # On 1x2 page with no green
    driver.get("https://www.oddsportal.com/basketball/bulgaria/nbl/beroe-rilski-sportist-UZ823qD3/#1X2;2")
    print(container_find("1x2") == "1")
    print(container_find("Home/Away") == "1")
    #print(container_find("Over/Under") == "1")
    print("\n")
    
    # On 1x2 page with green
    driver.get("https://www.oddsportal.com/football/argentina/liga-profesional/san-lorenzo-independiente-6aKyx0xI/#1X2;2")
    print(container_find("1x2") == "")
    #This test is cursed, as it will calculate
    #FIX
    #print(container_find("Home/Away") == "1")
    print("\n")
    
    # On Home/Away page with no green
    driver.get("https://www.oddsportal.com/basketball/puerto-rico/bsn/grises-de-humacao-leones-de-ponce-pQDKRBCG/#home-away;1")
    #FIX
    #print(container_find("1x2") == "1")
    print(container_find("Home/Away") == "1")
    print("\n")

    # On Home/Away page with green
    driver.get("https://www.oddsportal.com/hockey/usa/nhl/columbus-blue-jackets-new-york-rangers-Am1R42bg/#home-away;1")
    #FIX
    #print(container_find("1x2") == "1")
    print(container_find("Home/Away") == "")
    print("\n")
