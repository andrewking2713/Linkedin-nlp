import requests
import re
from bs4 import BeautifulSoup
import math
import time
import random


def job_id_scrape(target_url: str, num_of_jobs: int) -> list:
    """
    Accepts a 'target_url' to scape (see below for target URL generation) and 'num_of_jobs' on the page to scrape.
    Follow the steps to produce a target URL:
    1. Goto Linkedin and search for a job with any filters you want.
    2. Open up the Developer inspector (Use Google Chrome) and scroll down until the next set of jobs load.
    3. In the network tab there should be a "search" request when it loads the new jobs.
    4. Grab that URL in the search request.
    5. replace the last NUMBER in the URL with a {} in order to utilize a .format() for looping later. ie 'start=0' -> 'start={}'

    The num_of_jobs can be gathered by clicking on any of the dropdown filter menus on LinkedIn after filtering for the criteria
    you wish to filter
    """
    l=[] #Empty list to store job IDs. These IDs are used to create the URLs for specific job searches later
    a = 0 #Used for the URL page number
    pattern = 'jobPosting:(?P<job_id>\d+)' #Regex patter to get the job ID
    for i in range(0, math.ceil(num_of_jobs/25)): #Use math.ceil() to round off the loop, the numerator can be found by looking at the filters when building the target URL.
        res = requests.get(target_url.format(a)) #Get request against the target URL and a .format() in order to provide specific page number.
        a += 25
        soup = BeautifulSoup(res.text, 'html.parser')
        all_jobs = soup.find_all('li') #The 'li' tag contains the job ID
        for j in range(0, len(all_jobs)): #Loop through all b4 'li' list
            job_id = re.search(pattern, str(all_jobs[j])) #Using Regex to search for the ID
            l.append(int(job_id.groups()[0])) #Appened the ID and casting it as int for later use.
    return l


