from sys import exit
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as seleniumException
import credentials

chromdriver = credentials.chromedriver
driver = webdriver.Chrome(chromdriver)

user = credentials.username
pwd = credentials.password
guests = credentials.guests


def displayFastPassTimes(fastPassDictionary):

    for key in fastPassDictionary.keys():
        # Convert the time back to clock time
        timeMinutes = fastPassDictionary[key]
        hour = int(timeMinutes/60)
        minute = int(((timeMinutes/60.0)-hour)*60.0)

        time = str(hour % 12)+":"+str(minute)

        if hour < 12:
            time += " AM"
        else:
            time += " PM"

        print (key,": ",time)
                            

def getTimeElements(driver):
    timeFilter = driver.find_element_by_css_selector(".timeFilterOptionBox.ng-scope")
    return timeFilter.find_elements_by_class_name("ng-scope")


def removeRideFromList(ride='', fastPassList=[]):
    """
    Removes the ride from the fast pass list when we have selected a time.
    """

    idx = [i for i, s in enumerate(fastPassList) if s in ride]
    del fastPassList[idx[0]]
    return fastPassList

def convertTime(timeString=''):
    if timeString == '':
        return 0
    else:
        timeItems = timeString.split(' ')
        time = timeItems[0].split(':')
        hour = int(time[0])
        minute = int(time[1])

        if (timeItems[1] == 'PM'):
            hour += 12

        return (hour * 60) + minute

def checktimes(availableTimes = [], fastPassTimes = []):
    
    if not availableTimes or not fastPassTimes:
        return 0, 0
    
    for idx, time in enumerate(availableTimes):
        keepThis = True
        t = int(convertTime(time.text))

        # find a time (t) that is atleast 1 hour difference between all time in the fast pass list
        for fptime in fastPassTimes.values():
            if not abs(fptime - t) > 60:
                keepThis = False
                
                break # to the next time (t)

        # time (t) has an hour between times in fast pass list
        if keepThis:
            break

        if not keepThis and idx == len(availableTimes)-1:
            print ('The selected fast pass time may conflict with an existing fast pass')
            return -1, 0


    return idx, t





if __name__ == '__main__':

    month = "March"
    dates = ["5"]
    parks = {"4": "Epcot", "5": "Hollywood Studios", "2": "Magic Kingdom", "3": "Animal Kingdom"}
    EpcotFastPasses = []
    HollywoodFastPasses = ["Disney Junior Dance","Fantasmic","Tower of Terror"]
    #HollywoodFastPasses = ["Tower of Terror"]

    MagicFastPasses = []
    AnimalFastPasses = []
    selectedFastPasses = {"4": {}, "5": {}, "2": {}, "3": {}}
    continuallyWatch = []


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

        fastPasses_Later = []

        # Fast Pass page
        while len(selectedFastPasses[date]) < 4 and len(HollywoodFastPasses) > 0:
    
        
            # Select the filter by time
            elements = getTimeElements(driver)

            # select each time filter
            for filterIdx in range(len(elements)):
                if elements[filterIdx].text in ["Morning", "Afternoon", "Evening"]:
                    elements[filterIdx].click()
            
                    nextTimeFilter = False
            
                    sleep(5)
                    # Check if the desired ride has an available fast pass.
                    experiences = driver.find_elements_by_class_name("experienceNameLand")
                    experienceTimes = driver.find_elements_by_class_name("available-times-container")

                    # Figure out which park we need to use the fast pass list from
                    # TODO: generalise the checking of the fast pass list 
                    # HollywoodFastPasses

                    for idx in range(len(experiences)):
                        ride = experiences[idx].text.split("\n")[0]

                        # Check if the ride is in the fast pass list.
                        if any(substring in ride for substring in HollywoodFastPasses):
                            availableTimes = experienceTimes[idx].find_elements_by_css_selector(".availableTime.ng-scope")
                
                    
                            if availableTimes:
                                if not selectedFastPasses[date]:
                                    time = convertTime(availableTimes[0].text)
                                    selectedFastPasses[date][ride] = time # Add the first time value
                                    # select the time to add to the fast pass list
                                    availableTimes[0].click()
                                    HollywoodFastPasses = removeRideFromList(ride,HollywoodFastPasses)

                                else:
                                    # check each time has a minimum gap between existing fast pass times
                                    print ("Add additional fast passes")
                                    idxT, time = checktimes(availableTimes, selectedFastPasses[date])
                                    if idxT >= 0:
                                        selectedFastPasses[date][ride] = time
                                        availableTimes[idxT].click()
                                        HollywoodFastPasses = removeRideFromList(ride,HollywoodFastPasses)
                                    else:
                                        # Need to try to find alternative time for these ride
                                        HollywoodFastPasses += [HollywoodFastPasses.pop(0)]
                                        #fastPasses_Later.append(ride)

                                        # A little convoluted, but if the first element in the list is the 
                                        # current ride, we have been here before and now we need to move 
                                        # to the next time filter.
                                        if (HollywoodFastPasses[0] in ride):
                                            nextTimeFilter = True
                                            break


                                # Confirm selection
                                sleep(5)
                                try:
                                    driver.find_element_by_css_selector(".ng-scope.button.confirm.tertiary").click()
                                except seleniumException.NoSuchElementException as exception:
                                    print ("There is a conflict that, currently, can not be resolved by the program.")
                                    print ("Manual intervention is required to complete the fast pass process.")
                                    exit("There was a Fast Pass conflict")
                                    # Need to wait for the user to continue the program
                                    # press: Back
                                    # Add ride to the next time filter.


                                # Contnue with another Fast pass on the same day
                                sleep(5)
                                if len(selectedFastPasses[date]) < 3:
                                    driver.find_element_by_css_selector(".icon.calendarDay.ng-scope").click()
                                    # Continue with current guest list
                                    sleep(5)
                                    driver.find_element_by_xpath("""//*[@id="selectPartyPage"]/div[3]/div/div[2]/div""").click()
                        
                                else:
                                    # click "No Thanks, Im done"
                                    driver.find_element_by_css_selector(".ng-scope.button.next.primary").click()
                            
                                    displayFastPassTimes(selectedFastPasses[date])
                                    # All fast passes have been selected.
                                    exit(0)
                    

                                sleep(5)
                    

                                #break

                            else:
                                print ('Fast passes are not available for ',ride)
                                HollywoodFastPasses = removeRideFromList(ride,HollywoodFastPasses)
                                continuallyWatch.append(ride)

                        experiences = driver.find_elements_by_class_name("experienceNameLand")
                        experienceTimes = driver.find_elements_by_class_name("available-times-container")

                    # re-state the time filters
                    elements = getTimeElements(driver)
                    if nextTimeFilter:
                        continue
                else:
                    print ("Couldn't find a fast pass time for",HollywoodFastPasses,"that didn't conflict with existing fast passes")
                    HollywoodFastPasses = []
                    # We assume that we only reach this point after cycling through the time 
                    # filters Morning, Afternoon, and Evening
                    break


                # if yes, get earliest time with atleast 1 hour inbetween fast passes.

                # What happens when the desired fast pass isn't available at all?

              



