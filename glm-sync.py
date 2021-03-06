#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib.request
import time
import progressbar
import numpy as np

'''
This script fetches the video names and urls from an LMU-Cast website for the course
"Generalized Regression", generates corresponding filenames and downloads the videos
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
# --------------- Main    
def main(video_dir, url, username, password):    
    # start driver and keep browser open if python closes
    options = webdriver.ChromeOptions()     
    options.add_argument('--headless')     
    options.add_experimental_option('prefs',
                                    {"download.default_directory" : video_dir})           
    driver = webdriver.Chrome(options=options)
    driver.get(url)
   
    # --- Login
    # locate "here"-button and login to LMU account
    print('Logging in...')
    try:
        here_button = driver.find_elements(By.XPATH, '//a[1]')
        here_button[0].click()
    except:
        print('No login info')
    
    # enter account details
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
    time.sleep(1)   
    print('Retrieving video titles...')  
    try:
        headers = driver.find_elements(By.TAG_NAME, 'h2')
        header_names = list(map(lambda x: x.text, headers))[1:]
        text_field_list = driver.find_elements(By.CLASS_NAME, 'text')
        text_fields = list(map(lambda x: x.text, text_field_list))
        text_label_list = driver.find_elements(By.CLASS_NAME, 'label')
        text_labels = list(map(lambda x: x.text, text_label_list))
        label_idx = [label == 'Untertitel:' for label in text_labels]
        subtitle_names = np.array(text_fields)[np.array(label_idx)]
    except:
        print('Could not get video names')
        
    assert len(header_names) == len(subtitle_names), \
            'header subtitle number mismatch'
    video_titles = [a + ' - ' + b + '.mp4'
                    for a,b in zip(header_names, subtitle_names)]
        
    # get video links
    time.sleep(1)
    print('Retrieving video URLs...') 
    try:
        vid_links = driver.find_elements(By.TAG_NAME, 'a')
        vid_links_hq = list(map(lambda x: x.get_attribute('href'),
                                vid_links))[2::3]
        assert len(video_titles) == len(vid_links_hq), \
            'title video link number mismatch'
        vid_links_fin = list()
        for link in vid_links_hq:
            driver.get(link)
            vid_links_fin.append(driver.current_url)
    except:
        print('Could not download videos')    
    driver.close()
    
    # download videos
    print('Downloading new videos...')
    for i in range(len(vid_links_fin)):
        if not os.path.isfile(video_titles[i]):
            print("Downloading " + video_titles[i])
            urllib.request.urlretrieve(vid_links_fin[i], video_titles[i],
                                                       MyProgressBar())
           
    # up to date message                          
    print('Videos up to date.')
    
# ===========================================================================


# initialization
video_dir = os.path.dirname(os.path.abspath(__file__))
url = 'https://cast.itunes.uni-muenchen.de/vod/playlists/5mqVUOLd5m.html'
username = 'your.name@campus.lmu.de'
password = 'yourpassword'

# run main
if __name__ == "__main__":
    main(video_dir, url, username, password)
   
