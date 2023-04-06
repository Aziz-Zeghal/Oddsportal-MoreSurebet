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
url = "https://www.oddsportal.com/football/argentina/liga-profesional/san-lorenzo-independiente-6aKyx0xI/#1X2;2"
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

def one_x_two() :
    """
    def : This function will check if a match has a 1x2 opportunity
    if there is no 1x2 opportunity, it will return an empty string
    else, it will return a string with the info
    returns : nothing (temporary)
    """
    #We try to see if highest in green is here
    try :
        highest = driver.find_element(By.XPATH, "//div[@class='flex text-xs h-9 border-b border-[#E0E0E0] bg-gray-light bg-gray-med_light !h-[60px] !h-[60px]']")
    except NoSuchElementException:
        print("No opportunity\n")
    else :
        if highest != [] :
            
            #We try to find the bookmakers
            #Later on, this will be changed to include user's input
            try :
                book1 = driver.find_element(By.XPATH, "//img[@title='1xBet']")
            except NoSuchElementException:
                print("Bookmaker1 Missing\n")
            else :
                try :
                    book2 = driver.find_element(By.XPATH, "//img[@title='Pinnacle']")
                except NoSuchElementException:
                    print("Bookmaker2 Missing\n")
                else :
                    if book1 != [] and book2 != []:
                        print("Both bookmakers found! Starting calculations\n")
                        #One way to do it, is to check if the containers are yellow, but we will calculate everything
                        #Get the parents (to get values) 
                        odds1 = (book1.find_element(By.XPATH, "../../..")).text
                        odds2 = (book2.find_element(By.XPATH, "../../..")).text
                        
                        #We get the odds, from index 1 to 3 (we don't want the bookmaker name)
                        #This part is unique to 1X2, the rest can have its own function.
                        all_odds = transform(odds1, 3) + transform(odds2, 3)
                        (max_odds, books) = sel(all_odds)
                        profit = calculate(max_odds)
                        
                        if profit > 0 :
                            print("FOUND ON 1X2 :\n")
                            for i in range(0, 2) :
                                print(str(max_odds[i]) + " " + books[i])
                        print("Profit : " + str(profit) + "%\n")

def all_one_x_two() :
    """
    def : This function will cycles through FT, 1st H etc.
    returns : nothing (temporary)
    """
    print("Full Time")
    one_x_two()
    #Find buttons container, for optimization purposes
    try :
        buttons = driver.find_element(By.XPATH, "//div[@class='flex w-auto gap-2 pb-2 mt-2 ml-3 overflow-auto text-xs max-mt:hidden']")
    except NoSuchElementException:
        print("Buttons Missing\n")
        driver.quit()
    else :
        #Select non-clicked buttons
        toclick = buttons.find_elements(By.XPATH, "//div[@class='p-2 pl-3 pr-3 cursor-pointer bg-gray-medium']")
        for button in toclick :
            print(button.text)
            button.click()
            one_x_two()

        

#--| Main
start = time.time()
all_one_x_two()
end = time.time()
driver.quit()

print("it took " + str(end - start) + " time")
