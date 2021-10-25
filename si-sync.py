#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from selenium import webdriver
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
    print('Fetching video urls...')
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
        driver.find_element_by_tag_name('ion-button').click()
    except:
        print('Could not find login button')
    
    # enter account details
    try:
        uname_box = driver.find_element_by_id('username')
        uname_box.click()    
        uname_box.send_keys(username)
        pass_box = driver.find_element_by_id('password')
        pass_box.click()    
        pass_box.send_keys(password)     
        anmelde_button = driver.find_elements_by_xpath('//button[1]')
        anmelde_button[0].click()
    except:
        print('Cannot log in')

    # --- synch videos       
    # get video titles     
    try:
        driver.get(video_url)
        time.sleep(1)
        headers = driver.find_elements_by_tag_name('ion-card-title')
        video_titles = list(map(lambda x: x.text, headers))
    except:
        print('Could not get video names')
    
    # get video links
    def expand_shadow_element(element):
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root
    try:
        roots = driver.find_elements_by_tag_name('ion-button')
        shadow_roots = [expand_shadow_element(r) for r in roots]
        links = list()
        for i in range(len(shadow_roots)):
            try:
                links.append(shadow_roots[i].find_element_by_tag_name('a').get_attribute('href'))
            except:
                continue
        vid_links_hq = links[2::3]
    except:
        print('Could not get video urls')        
    assert len(video_titles) == len(vid_links_hq), \
        'title vs. video link number mismatch'
    try:
        vid_links_fin = list()
        for link in vid_links_hq:
            driver.get(link)
            vid_links_fin.append(driver.current_url)
    except:
        print('Could not get downloadable video urls')    
    driver.close()
    
    # download videos
    try:
        for i in range(len(vid_links_fin)):
            if not os.path.isfile(video_titles[i]):
                print("Downloading " + video_titles[i])
                urllib.request.urlretrieve(vid_links_fin[i], video_titles[i],
                                                           MyProgressBar())
    except:
        print('Could not download videos')    
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
   
