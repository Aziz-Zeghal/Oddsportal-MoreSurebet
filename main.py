from test import *
from tools import *

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)


#--| Main
url = input("Enter the url : ")
driver.get(url)
sleep(1)

start = time.time()

#Functions implemented : extract_all & extract
print(extract_all(driver))

end = time.time()
print("Time elapsed : " + str(end - start) + "s")

driver.quit()