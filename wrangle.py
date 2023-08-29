import requests
import re
from bs4 import BeautifulSoup
import math
import pandas as pd
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


def job_scrape(job_dict: dict, job_ids_list: list) -> tuple[dict, list]:
    """
    Accepts a dictionary, empty or already semi-filled, and a list of job IDs obtained from job_id_scrape. Returns a dictionary with the information from the webpage using the job ID.
    This function is intended to by used in a loop where i is == len(job_id_list). Once a webpage has succesfully been scraped the job_id_list will .pop() the leading entry.
    """
    if job_dict == {}:
        job_dict = {'job_title' : [], 'company' : [], 'job_info' : [], 'when_posted' : [], 'num_applicants' : [],
      'seniority' : [], 'employment_type' : [], 'job_function' : [], 'industry' : [], 'job_url' : []}
    else:
        pass
    target_job_url = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}/' #format of the URL. The {} is where the jobID gets formated to.
    res_job = requests.get(target_job_url.format(job_ids_list[0]))
    if res_job.status_code != 200:
        print('Status code not 200. Sleeping for 1 minute')
        time.sleep(15) #Long sleep in case of IP block
    else:
        soup = BeautifulSoup(res_job.text, 'html.parser')
        try:
            job_dict['job_title'].append(soup.find('div',{'class':'top-card-layout__entity-info'}).find('a').text.strip()) #Title
        except:
            job_dict['job_title'].append(None)
        try:
            job_dict['company'].append(soup.find('div',{'class':'top-card-layout__card'}).find('a').find('img').get('alt')) #Company
        except:
            job_dict['company'].append(None)
        try:
            job_dict['job_info'].append(soup.find('div',{'class':'show-more-less-html__markup'}).text.strip()) #Bulk, might need to find a way to clean this up.
        except:
            job_dict['job_info'].append(None)
        try:
            job_dict['when_posted'].append(soup.find('span',{'class':'posted-time-ago__text'}).text.replace('\n', '').strip()) #When was it posted
        except:
            job_dict['when_posted'].append(None)
        num_of_apps1 = soup.find('figcaption',{'class':'num-applicants__caption'})  #number of applicants scape attempt1
        if num_of_apps1 == None: #Check first soup, if it fails check second soup
            num_of_apps2 = soup.find('span', class_='num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet') #number of applicants scrape attempt2
            if num_of_apps2 == None: #Check second soup, if it fails, append None
                job_dict['num_applicants'].append(None) #if nosoup works just append None
            else:
                job_dict['num_applicants'].append(num_of_apps2.text.replace('\n', '').strip()) #If first soup failed and second soup passed, append second soup
        else:
            job_dict['num_applicants'].append(num_of_apps1.text.replace('\n', '').strip()) #If first soup works, append first soup
        job_attributes = soup.find('ul',{'class':'description__job-criteria-list'}) #Job attributes
        if job_attributes == None: #Check to see if there is soup. If not, append none.
            job_dict['seniority'].append(None)
            job_dict['employment_type'].append(None)
            job_dict['job_function'].append(None)
            job_dict['industry'].append(None)
        else:
            job_attributes = job_attributes.text.replace('\n', '').strip()
            if 'Seniority level' in job_attributes:
                pattern = 'Seniority level\s+(?P<seniority>(.*?)(?:\s{2,}|$))'
                job_dict['seniority'].append(re.search(pattern, job_attributes).groups()[0])
            else:
                job_dict['seniority'].append(None)
            if 'Employment type' in job_attributes:
                pattern = 'Employment type\s+(?P<employment_type>(.*?)(?:\s{2,}|$))'
                job_dict['employment_type'].append(re.search(pattern, job_attributes).groups()[0])
            else:
                job_dict['employment_type'].append(None)
            if 'Job function' in job_attributes:
                pattern = 'Job function\s+(?P<job_function>(.*?)(?:\s{2,}|$))'
                job_dict['job_function'].append(re.search(pattern, job_attributes).groups()[0])
            else:
                job_dict['job_function'].append(None)
            if 'Industries' in job_attributes:
                pattern = 'Industries\s+(?P<industries>(.*?)(?:\s{2,}|$))'
                job_dict['industry'].append(re.search(pattern, job_attributes).groups()[0])
            else:
                job_dict['industry'].append(None)
        job_dict['job_url'].append(f'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_ids_list[0]}/')
        job_ids_list.pop(0)
        time.sleep(random.choice(range(2,4,1))) # Sleep to avoid IP block
    return job_dict, job_ids_list


