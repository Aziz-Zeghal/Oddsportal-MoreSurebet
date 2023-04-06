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
url = "https://www.oddsportal.com/basketball/brazil/nbb/minas-paulistano-htxX8KaS/#over-under;1;155.50;0"
#Home/Away : https://www.oddsportal.com/basketball/bulgaria/nbl/beroe-rilski-sportist-UZ823qD3/#home-away;1
#1x2 : https://www.oddsportal.com/basketball/bulgaria/nbl/beroe-rilski-sportist-UZ823qD3/#1X2;2
#Under/Over OPEN : https://www.oddsportal.com/basketball/brazil/nbb/minas-paulistano-htxX8KaS/#over-under;1;155.50;0
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

def container_find(type):
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
        return ""
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
        return ""
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

        

#--| Main
start = time.time()
#print(extract("Home/Away"))
print(container_find("Other"))
end = time.time()
driver.quit()

print("it took " + str(end - start) + " time")
