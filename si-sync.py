#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from pyshadow.main import Shadow
import urllib.request
import progressbar

'''
This script fetches the video names and urls from an LMU-Cast website for the course
"Statistical Inference", generates corresponding filenames and downloads the videos
to the directory which contains this script (unless these filenames already exist in there).

For this you require the listed python packages. Also, you need to fill in your 
own uni email and password below before running the script.

@author: adkipnis
'''

class MyProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


# --------------- Main    
def main(login_url, video_url, username, password):    
    # start driver and keep browser open if python closes
    options = webdriver.ChromeOptions()   
    options.add_argument('--headless')     
    options.add_experimental_option('prefs',
                                    {"download.default_directory" : video_dir})           
    driver = webdriver.Chrome(options=options)
    driver.get(login_url)
   
    # --- Login
    # locate "here"-button and login to LMU account
    try:
        driver.find_element(By.TAG_NAME, 'ion-button').click()
    except:
        print('Could not find login button.')
    
    # enter account details
    print('Logging in...')
    try:
        uname_box = driver.find_element(By.ID, 'username')
        uname_box.click()    
        uname_box.send_keys(username)
        pass_box = driver.find_element(By.ID, 'password')
        pass_box.click()    
        pass_box.send_keys(password)     
        anmelde_button = driver.find_elements(By.XPATH, '//button[1]')
        anmelde_button[0].click()
    except:
        print('Cannot log in')

    # --- synch videos       
    # get video titles 
    print('Retrieving video titles...')    
    try:
        driver.get(video_url)
        time.sleep(1)
        headers = driver.find_elements(By.TAG_NAME, 'ion-card-title')
        video_titles = list(map(lambda x: x.text, headers))
    except:
        print('Could not get video titles.')
    
    # get video links
    print('Retrieving video URLs...') 
    
    try:
        shadow = Shadow(driver)
        elements = shadow.find_elements("a")
        links = [s.get_attribute('href') for s in elements]
        vid_links_hq = [l for l in links if l != None and 'high_quality.mp4' in l]
    except:
        print('Could not get video URLs')   
    assert 0 < len(vid_links_hq), \
        'Could not get video URLs'
    assert len(video_titles) == len(vid_links_hq), \
        'Title vs. video link number mismatch'
    try:
        vid_links_fin = list()
        for link in vid_links_hq:
            driver.get(link)
            vid_links_fin.append(driver.current_url)
    except:
        print('Could not get downloadable video urls')    
    driver.close()
    
    # download videos
    print('Downloading new videos...')
    try:
        for i in range(len(vid_links_fin)):
            if not os.path.isfile(video_titles[i]):
                print("Downloading " + video_titles[i])
                urllib.request.urlretrieve(vid_links_fin[i], video_titles[i],
                                                           MyProgressBar())
    except:
        print('Failed to download videos.')    
    # up to date message                          
    print('Videos up to date.')
    
# ===========================================================================

# initialization
video_dir = os.path.dirname(os.path.abspath(__file__))
login_url = 'https://cast.itunes.uni-muenchen.de/#/home'
video_url = 'https://cast.itunes.uni-muenchen.de/#/clip-list/0xMpNDNpYf'
username = 'your.name@campus.lmu.de'
password = 'yourpassword'

# run main
if __name__ == "__main__":
    main(login_url, video_url, username, password)
   
