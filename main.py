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
url = "https://www.oddsportal.com/volleyball/romania/divizia-a1-women/alba-blaj-rapid-bucuresti-EXZIV2LU/#home-away;2"
driver.get(url)
sleep(2)
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
    toclick = driver.find_elements(By.XPATH, "//div[@class='relative flex flex-col']")
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
        #Now we check if the container is worth openning (at least 2 bookmakers for bet)
    for container in toclick :
        text = container.text.split("\n")
        if int(text[1]) < 3 :
            toclick.remove(container)

    i = 1
    print("The containers")
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
        highest = driver.find_element(By.XPATH, "//p[@class='text-[10px] font-bold text-green-dark']")
    except NoSuchElementException:
        return "1"
    else :
        if highest != [] :
            
            #We try to find the bookmakers
            #Later on, this will be changed to include user's input
            try :
                book1 = driver.find_element(By.XPATH, "//img[@title='1xBet']")
            except NoSuchElementException:
                return "2"
            else :
                try :
                    book2 = driver.find_element(By.XPATH, "//img[@title='Pinnacle']")
                except NoSuchElementException:
                    return "2"
                else :
                    if book1 != [] and book2 != []:
                        #One way to do it, is to check if the containers are yellow, but we will calculate everything
                        #Get the parents (to get values) 
                        odds1 = (book1.find_element(By.XPATH, "../../..")).text
                        odds2 = (book2.find_element(By.XPATH, "../../..")).text
                        
        togive = ""
        match type :
            
            #We get the odds, from index 1 to 3 (we don't want the bookmaker name)
            case "1X2" :
                all_odds = transform(odds1, 3) + transform(odds2, 3)
                i = 3
            
            case "Home/Away" :
                all_odds = transform(odds1, 2) + transform(odds2, 2)
                i = 2
            
            #All other bet types have 3 odds, but the first one is special
            case _:
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
    togive = container_find(type)
    #Find buttons container, for optimization purposes
    try :
        buttons = driver.find_element(By.XPATH, "//div[@class='flex w-auto gap-2 pb-2 mt-2 ml-3 overflow-auto text-xs max-mt:hidden']")
    except NoSuchElementException:
        driver.quit()
        return "1"
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
    #Refuse cookies
    try :
        refuse = driver.find_element(By.ID, "onetrust-reject-all-handler")
        refuse.click()
    except NoSuchElementException:
        pass
    #We read the bet type where we start
    current_type = driver.find_element(By.XPATH, "//li[@class='flex items-center justify-center pl-[13px] pr-[13px] pt-[11px] pb-[11px] opacity-80 text-xs cursor-pointer text-white-main h-max whitespace-nowrap odds-item active-odds']")
    bet_name = current_type.text
    togive = extract(bet_name)
    if togive != "" :
        togive = driver.title + "\n" + bet_name  + "\n" + togive
        
    return togive + "\n"

#--| Main

#--| Function test
#1 : Green profit not found OR containers not found for container_open
#2 : Works as intended, but did not find what we wanted
#“” : Just no profit found
start = time.time()

#test container_open
def test_container_open():
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
def test_container_find():
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

print(extract_all())
end = time.time()
driver.quit()
print("it took " + str(end - start) + " time")
