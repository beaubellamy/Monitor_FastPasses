from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as seleniumException

chromdriver = "C:\\Users\\bbel1\\AppData\\Local\\Continuum\\anaconda3\\Lib\\site-packages\\chromedriver_2.41.exe"
driver = webdriver.Chrome(chromdriver)

user = "YOUR-USERNAME"
pwd = "YOUR-PASSWORD"
guests = ["guest-CAFEF00D-6502-0000-0000-000303002409-unselected",
          "guest-CAFEF00D-6502-0000-0000-000303002525-unselected",
          "guest-CAFEF00D-6502-0000-0000-000303002476-unselected"]

dates = ["18"]
parks = {"17": "Epcot", "18": "Hollywood Studios", "20": "Magic Kingdom", "22": "Animal Kingdom"}

driver.get("https://disneyworld.disney.go.com/login/")
# Enter the login details
elem = driver.find_element_by_id("loginPageUsername")

elem.send_keys(user)
elem = driver.find_element_by_id("loginPagePassword")
elem.send_keys(pwd)
elem.send_keys(Keys.RETURN)

fastPass = "https://disneyworld.disney.go.com/fastpass-plus/"
driver.get(fastPass)
sleep(2)
elem = driver.find_element_by_css_selector(".ng-scope.button.next")
sleep(2)
elem.send_keys(Keys.RETURN)
for guest in guests:
     sleep(5)
     driver.find_element_by_xpath("""//*[@id="""+'"'+guest+'"'+"""]/div""").click()
   
    
driver.find_element_by_xpath("""//*[@id="selectPartyPage"]/div[3]/div/div[2]/div""").click()
sleep(2)
elem = driver.find_element_by_css_selector(".current-month.ng-binding")

while (elem.text != "February"):
    elem = driver.find_element_by_class_name("next-month").click()
    elem = driver.find_element_by_css_selector(".current-month.ng-binding")


elem = driver.find_elements_by_css_selector(".day.ng-binding.ng-scope")

dayIdx = []
for i in range(len(elem)):
   if (elem[i].text in dates):
       dayIdx.append(i)

# loop through each dayIdx
# for day in dayIdx:
day = 29

elem[day].click()

key = elem[day].text

sleep(2)
# Find each park link
elements = driver.find_elements_by_css_selector(".park.ng-scope")

parkIdx = 0
for i in range(len(elements)):
    if (parks[key] in elements[i].text):
        parkIdx = i
        break

# click on the park
elements[parkIdx].click()



# Confirm "Continue with guest" is available
try:
    element = driver.find_element_by_css_selector(".button.ng-binding.primary")
    element.click()
except seleniumException.ElementNotVisibleException as exception:
    print ("Members already have the maximum number of fast passes for this day")

print ("got past the exception")


