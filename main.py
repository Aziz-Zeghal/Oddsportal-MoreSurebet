from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from time import sleep
import time
 
#--| Setup
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)


#--| Parse or automation
url = "https://www.oddsportal.com/tennis/spain/itf-m25-reus-men/damas-miguel-melero-kretzer-alejandro-OzabS6GT/#over-under;2"
#Home/Away : https://www.oddsportal.com/basketball/bulgaria/nbl/beroe-rilski-sportist-UZ823qD3/#home-away;1
#1x2 : https://www.oddsportal.com/basketball/bulgaria/nbl/beroe-rilski-sportist-UZ823qD3/#1X2;2
#Under/Over OPEN : https://www.oddsportal.com/basketball/brazil/nbb/minas-paulistano-htxX8KaS/#over-under;1;155.50;0
#Under/Over ToOpen : https://www.oddsportal.com/volleyball/bulgaria/superliga/neftohimic-burgas-pirin-razlog-Aa1R2YPA/#over-under;2
#Under/Over ToOpen2 : https://www.oddsportal.com/tennis/spain/itf-m25-reus-men/damas-miguel-melero-kretzer-alejandro-OzabS6GT/#over-under;2
driver.get(url)

#--| Functions
def calculate(odds) :
    """
    def : This function will calculate the profit
    params : list of floats
    returns : float
    """
    profit = 0
    for odd in odds :
        profit += 1/odd
    return round((1 - profit) * 100, 3)

#This function will be changed to include the bookmakers
def sel(odds) :
    """
    def : this function will select the highest odds
    Len(odds) / 2 is used to distinguish between the two bookmakers
    params : list of floats
    returns : (list of floats, list of strings)
    """
    max_odds = []
    books = []
    space = len(odds) // 2
    for i in range(0, space) :
        if odds[i] > odds[i + space] :
            max_odds.append(odds[i])
            books.append("1xBet")
        else :
            max_odds.append(odds[i + space])
            books.append("Pinnacle")

    return (max_odds, books)

def transform(text, n) :
    """
    def : this function takes the text of a bookmaker container and outputs n odds
    params : string, int
    returns : list of floats
    """
    odds = text.split("\n")
    give = []
    if odds[1] == "BONUS" :
        for i in range(0, n) :
            give.append(float(odds[i + 2]))
    else :
        for i in range(0, n) :
            give.append(float(odds[i + 1]))
    return give

def container_open() :
    """
    def : This function will ONLY retrieve the bet types containers worth opening
    "Other" bet types have many containers
    Each container has a different argument for the bet
    Example : Under/Over has 155.5, 156, etc.
    params : None
    returns : list of WebElements
    """
    try :
        toclick = driver.find_elements(By.XPATH, "//div[@class='relative flex flex-col']")
    except NoSuchElementException:
        return "You are not in a match page !"
    else :
        #looks like this :
        #Over/Under +132.5 Points
        #7
        #1.84
        #1.88
        #93.0%
        #Or looks like this :
        #Over/Under =136.5 Points
        #7
        #-
        #Now we check if the container is worth opening (at least 2 bookmakers for bet)
        for container in toclick :
            text = container.text.split("\n")
            if int(text[1]) < 3 :
                toclick.remove(container)

        for cont in toclick :
            print(cont.text)
            
        return toclick

def container_find(type) :
    """
    def : This function will select the bookmaker containers and extract values
    In the future, this function will be changed to include the user's input

    1x2 has 3 extracted values
    Home/Away has 2
    Other bet types have 3 but first one is special (bet argument) 
    
    params : string
    returns : list of floats and strings
    """
    #We try to see if highest in green is here
    try :
        highest = driver.find_element(By.XPATH, "//div[@class='flex text-xs h-9 border-b border-[#E0E0E0] bg-gray-light bg-gray-med_light !h-[60px] !h-[60px]']")
    except NoSuchElementException:
        return "You are not in a match page !"
    else :
        if highest != [] :
            
            #We try to find the bookmakers
            #Later on, this will be changed to include user's input
            try :
                book1 = driver.find_element(By.XPATH, "//img[@title='1xBet']")
            except NoSuchElementException:
                return ""
            else :
                try :
                    book2 = driver.find_element(By.XPATH, "//img[@title='Pinnacle']")
                except NoSuchElementException:
                    return ""
                else :
                    if book1 != [] and book2 != []:
                        #One way to do it, is to check if the containers are yellow, but we will calculate everything
                        #Get the parents (to get values) 
                        odds1 = (book1.find_element(By.XPATH, "../../..")).text
                        odds2 = (book2.find_element(By.XPATH, "../../..")).text
                        
        togive = ""
        match type :
            
            #We get the odds, from index 1 to 3 (we don't want the bookmaker name)
            case "1x2" :
                all_odds = transform(odds1, 3) + transform(odds2, 3)
                i = 3
            
            case "Home/Away" :
                all_odds = transform(odds1, 2) + transform(odds2, 2)
                i = 2
            
            #All other bet types have 3 odds, but the first one is special
            case "Other" :
                #The first value is the bet argument
                #Example : Under/Over will have
                #odds1 = [155.5, 1.64, 2.07]
                #155.5 is the total for Under/Over
                #TODO : change the output with the bet type
                #TODO : change transform (repeated operations)
                all_odds = transform(odds1, 3) + transform(odds2, 3)
                togive += "For " + str(all_odds.pop(0)) + "\n"
                all_odds.pop(2)
                i = 2
                
        (max_odds, books) = sel(all_odds)
        profit = calculate(max_odds)
        
        if profit < 0 :
            return ""
        
        for i in range(0, i) :
            togive += str(max_odds[i]) + " " + books[i] + "\n"
        togive += "Profit : " + str(profit) + "%\n"
        
        return togive

def extract(type) :
    """
    def : This function will cycles through FT, 1st H etc.
    params : string
    returns : string
    """
    temp = container_find(type)
    togive = "\n" + driver.title + "\n"
    if temp != "" :
        togive += "\nFirst time\n" + temp
    #Find buttons container, for optimization purposes
    try :
        buttons = driver.find_element(By.XPATH, "//div[@class='flex w-auto gap-2 pb-2 mt-2 ml-3 overflow-auto text-xs max-mt:hidden']")
    except NoSuchElementException:
        driver.quit()
        return "You are not in a match page !"
    else :
        #Select non-clicked buttons
        toclick = buttons.find_elements(By.XPATH, "//div[@class='p-2 pl-3 pr-3 cursor-pointer bg-gray-medium']")
        for button in toclick :
            time = "\n" + button.text + "\n"
            button.click()
            temp = container_find(type)
            if temp != "" :
                togive += time + temp
        
        return togive

        
def extract_all() :
    """
    def : This function will cycle through all bet types
    Function can start at any bet type of a match
    For optimization purposes we will only consider the following :
    1x2, Home/Away, Over/Under, Asian handicap
    Other bet types will be ignored (I will make an argument for bet consideration)
    params : None
    returns : string
    """
    #We read the bet type where we start
    current_type = driver.find_element(By.XPATH, "//li[@class='flex items-center justify-center pl-[13px] pr-[13px] pt-[11px] pb-[11px] opacity-80 text-xs cursor-pointer text-white-main h-max whitespace-nowrap odds-item active-odds']")
    
#--| Main
start = time.time()
#print(extract("Home/Away"))
#print(container_find("Other"))
#container_open()
print(extract_all())
end = time.time()
driver.quit()

print("it took " + str(end - start) + " time")
