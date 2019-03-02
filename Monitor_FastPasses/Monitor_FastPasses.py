from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as seleniumException
import credentials

chromdriver = credentials.chromedriver# = "C:\\Users\Beau\Anaconda3\Lib\site-packages\chromedriver.exe"
driver = webdriver.Chrome(chromdriver)

user = credentials.username
pwd = credentials.password
guests = credentials.guests

month = "March"
dates = ["5"]
parks = {"4": "Epcot", "5": "Hollywood Studios", "2": "Magic Kingdom", "3": "Animal Kingdom"}
EpcotFastPasses = []
HollywoodFastPasses = ["Fantasmic","Star Tours","Toy Story"]
MagicFastPasses = []
AnimalFastPasses = []
selectedFastPasses = {"4": {}, "5": {}, "2": {}, "3": {}}



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
 

for date in dates:

    driver.find_element_by_xpath("""//*[@id="selectPartyPage"]/div[3]/div/div[2]/div""").click()
    sleep(2)
    elem = driver.find_element_by_css_selector(".current-month.ng-binding")

    while (elem.text != month):
        elem = driver.find_element_by_class_name("next-month").click()
        elem = driver.find_element_by_css_selector(".current-month.ng-binding")


    elem = driver.find_elements_by_css_selector(".day.ng-binding.ng-scope")

    
    for i in range(len(elem)):
        if (elem[i].text == date):
            day = i

    day = 16

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
    except seleniumException.NoSuchElementException as exception:
        pass
        # On the fast pass page


    # Fast Pass page
    while len(selectedFastPasses[date]) < 4:
    
        
        # Select the filter by time
        timeFilter = driver.find_element_by_css_selector(".timeFilterOptionBox.ng-scope")
        elements = timeFilter.find_elements_by_class_name("ng-scope")

        # click on the desired filter ??????
        for elem in elements:
            if elem.text == "Afternoon":
                elem.click()
                break

        sleep(5)
        # Check if the desired ride has an available fast pass.
        experiences = driver.find_elements_by_class_name("experienceNameLand")
        experienceTimes = driver.find_elements_by_class_name("available-times-container")

        #Figure out which park we need to use the fast pass list from
        # HollywoodFastPasses

        for idx, experience in enumerate(experiences):
            ride = experience.text.split("\n")[0]

            # Check if the ride is in the fast pass list.
            if any(substring in ride for substring in HollywoodFastPasses):
                availableTimes = experienceTimes[idx].find_elements_by_css_selector(".availableTime.ng-scope")
                
                # Remove the ride from the fast pass list, so we dont find it the next time round.
                idx = [i for i, s in enumerate(HollywoodFastPasses) if s in ride]
                del HollywoodFastPasses[idx[0]]

                if availableTimes:
                    if not selectedFastPasses[date]:
                        selectedFastPasses[date] = {ride: availableTimes[0].text} # Add the first time value
                        # select the time to add to the fast pass list
                        availableTimes[0].click()

                    else:
                        # check each time has a minimum gap between existing fast pass times
                        print ("Add additional fast passes")
                        continue

                    # Confirm selection
                    driver.find_element_by_css_selector(".ng-scope.button.confirm.tertiary").click()
                    # Contnue with another Fast pass on the same day
                    driver.find_element_by_css_selector(".icon.calendarDay.ng-scope").click()
                    # Continue with current guest list
                    driver.find_element_by_xpath("""//*[@id="selectPartyPage"]/div[3]/div/div[2]/div""").click()
    
                    break

        
        # if yes, get earliest time with atleast 1 hour inbetween fast passes.

        # What happens when the desired fast pass isn't available at all?

        # fast pass not available -----  <span ng-if="experience.offersets.length === 0" class="icon fpCancel noAvailableTimes ng-scope"></span>




