from Tools import tools_v000 as tools
from MyHours import myhours as m
from AzureDevOps import azuredevops as a
import os
from os.path import dirname
import time
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# False : If you have already start the clock => just update after. => Default value is True
isStartMyHoursNeeded = True

# -10 for the name of this project logWorkpbi
# save_path = dirname(__file__)[ : -10]
save_path = os.path.dirname(os.path.abspath("__file__"))
propertiesFolder_path = save_path + "/"+ "Properties"

a.save_path = tools.readProperty(propertiesFolder_path, 'logWorkPBI', 'save_path=')
a.boards = tools.readProperty(propertiesFolder_path, 'logWorkPBI', 'boards=')
a.pbi = tools.readProperty(propertiesFolder_path, 'logWorkPBI', 'pbi=')

delay_properties = 10



# Open Browser
tools.openBrowserChrome()

# MyHours part
m.connectToMyTimeTrack()

# afficher une popup expliquant qu'il faut se connecter une première fois
# Et installer l'extension chrome pour retenir les users et password
def show_popup():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showinfo("Information", "Please connect for the first time and install the Chrome extension to remember the users and passwords.")
    root.destroy()


print ("Test if we need to wait the page of the user / password")
if tools.waitLoadingPageByID2(5, 'email-label') :
    # show_popup()
    # print ("Need to wait the page of the password")
    # tools.waitLoadingPageByID2(10, 'email-label')
    # time.sleep(30)
    m.enterCredentials2()

time.sleep(1)

# Force refresh the page
tools.driver.refresh()

m.startTrack2()

time.sleep(1)

# Need to update the task with information from Admin
# Click on the edit button
tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="group-no-project-no-task-bulk-edit"]')
add_task_button = tools.driver.find_element(By.XPATH, '//*[@id="group-no-project-no-task-bulk-edit"]')
add_task_button.click()

# Fill in the Projet
tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="bulk-project-autocomplete"]')
switchToWeekTrackBtn = tools.driver.find_element(By.XPATH, '//*[@id="bulk-project-autocomplete"]')
switchToWeekTrackBtn.send_keys("Business operations (non project / service related tasks)")
switchToWeekTrackBtn.send_keys(Keys.DOWN)
switchToWeekTrackBtn.send_keys(Keys.ENTER)

tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="bulk-task-name"]')
switchToWeekTrackBtn = tools.driver.find_element(By.XPATH, '//*[@id="bulk-task-name"]')
switchToWeekTrackBtn.click()
switchToWeekTrackBtn.send_keys("Mail + administration")
switchToWeekTrackBtn.send_keys(Keys.ENTER)

tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="bulk-notes"]')
switchToWeekTrackBtn = tools.driver.find_element(By.XPATH, '//*[@id="bulk-notes"]')
switchToWeekTrackBtn.click()
switchToWeekTrackBtn.send_keys("Mail + administration")
switchToWeekTrackBtn.send_keys(Keys.ENTER)

tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="bulk-tags"]')
switchToWeekTrackBtn = tools.driver.find_element(By.XPATH, '//*[@id="bulk-tags"]')
switchToWeekTrackBtn.click()
switchToWeekTrackBtn.send_keys("Mail + administration")
switchToWeekTrackBtn.send_keys(Keys.ENTER)

tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="bulk-edit-dialog"]/div[3]/div/div[2]/button[2]')
switchToWeekTrackBtn = tools.driver.find_element(By.XPATH, '//*[@id="bulk-edit-dialog"]/div[3]/div/div[2]/button[2]')
switchToWeekTrackBtn.click()

time.sleep(5)

# go to the research page
# https://timetrackingwindsurf.web.app/task-search
tools.driver.get('https://timetrackingwindsurf.web.app/task-search')

# Search the input task where we can enter the jira ticket (j.jira)
# //*[@id="task-search-input"]
tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="task-search-input"]')
task_search_input = tools.driver.find_element(By.XPATH, '//*[@id="task-search-input"]')
# Need to select all the current text in the input
task_search_input.send_keys(Keys.CONTROL + "a")
task_search_input.send_keys(a.pbi)
task_search_input.send_keys(Keys.RETURN)

time.sleep(1)

# Localiser le tableau
if tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="search-results-table"]') :
    table = tools.driver.find_element(By.XPATH, '//*[@id="search-results-table"]')

    # Parcourir les lignes du tableau
    rows = table.find_elements(By.XPATH, './/tbody/tr')


    # Need to store data 
    array = [ ]

    # Extraire les informations de chaque ligne
    for row in rows:
        date = row.find_element(By.XPATH, './/td[contains(@id, "date-cell")]').text
        duration = row.find_element(By.XPATH, './/td[contains(@id, "duration-cell")]').text
        print(f"Date: {date}, Duration: {duration}")

        # I would like to save all those information in arrays
        array.append([date, duration])

    print(array)
    
    # Need to go to the PBI
    a.connectToAzureDevOpsInsim(a.boards, a.pbi, a.userInsim, a.userInsimPassword)

    time.sleep(1)


    # Need to add all the time for this JIRA
    time_all = timedelta(hours=0, minutes=0, seconds=0)

    # Print the array with all the info for this JIRA
    print("----------------- Infos -----------------  ")

    for r in array:
        print( ' '.join([str(x) for x in r] ) )

        # Convertir la chaîne de temps en objet timedelta
        duration_str = r[1]
        time_parts = duration_str.split()
        time_kwargs = {}
        for part in time_parts:
            if 'h' in part:
                time_kwargs['hours'] = int(part.replace('h', ''))
            elif 'm' in part:
                time_kwargs['minutes'] = int(part.replace('m', ''))
            elif 's' in part:
                time_kwargs['seconds'] = int(part.replace('s', ''))

        time_object = timedelta(**time_kwargs)

        # Extraire les heures, minutes et secondes de l'objet timedelta
        total_seconds = int(time_object.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f"{hours}h {minutes}m {seconds}s")

        # Need to add the time past to this JIRA
        time_all += time_object

    print(f"Total time: {time_all}")

    print(str(time_all))
    timedelta_8 = timedelta(hours=8, minutes=0, seconds=0)

    time_all_sec = time_all.total_seconds()
    timedelta_8_sec = timedelta_8.total_seconds()
    total_sec = time_all_sec / timedelta_8_sec
    print(str(round(total_sec, 3)))

    # Need to update the JIRA for the Story Points field
    # /html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div/div/input
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div/div/input')
    story_points_field = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div/div/input')
    story_points_field.click()
    time.sleep(1)
    # Clear the field
    story_points_field.send_keys(Keys.CONTROL + "a")
    story_points_field.send_keys(Keys.DELETE)
    story_points_field.send_keys(str(round(total_sec, 3)))
    time.sleep(1)

else :
    print ("No data for this PBI")
    
    # Need to go to the PBI
    a.connectToAzureDevOpsInsim(a.boards, a.pbi, a.userInsim, a.userInsimPassword)
    total_sec = 0

    # Need to update the PBI for the Story Points field
    # /html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div/div/input
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div/div/input')
    story_points_field = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div/div/input')
    story_points_field.click()
    time.sleep(1)
    # Clear the field
    story_points_field.send_keys(Keys.CONTROL + "a")
    story_points_field.send_keys(Keys.DELETE)
    story_points_field.send_keys(str(round(total_sec, 3)))
    time.sleep(1)

# Need to place the PBI in DONE
# /html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[1]/div/div[1]/div[1]/div/div[3]/div/div/input
tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[1]/div/div[1]/div[1]/div/div[3]/div/div/input')
state_field = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[1]/div/div[1]/div[1]/div/div[3]/div/div/input')
state_field.click()

# Clear the field
state_field.send_keys(Keys.CONTROL + "a")
state_field.send_keys(Keys.DELETE)
state_field.send_keys("Done")
state_field.send_keys(Keys.ENTER)
time.sleep(1)

# Need to save the change
# /html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div[2]/div[3]/div[1]/div/button[1]
tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div[2]/div[3]/div[1]/div/button[1]')
save_button = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div[2]/div[3]/div[1]/div/button[1]')
save_button.click()
time.sleep(1)
