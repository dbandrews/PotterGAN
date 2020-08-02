import pandas as pd
import time

from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import requests
from bs4 import BeautifulSoup

import re
import os
import csv
import json
import datetime as dt
from itertools import repeat
from multiprocessing import Pool, cpu_count

import shutil



def recent_post_links(chrome_path, username, post_count=10):
    """
        With the input of an account page, scrape the 10 most recent posts urls
        Args:
        username: Instagram username
        post_count: default of 10, set as many or as few as you want
        Returns:
        A list with the unique url links for the most recent posts for the provided user
        """
    print('User ' + username + ' started:')
    start_time = time.time()
    url = "https://www.instagram.com/" + username + "/"
    options = Options()
    options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    browser = Chrome(options=options, executable_path=chrome_path)
    browser.get(url)
    post = 'https://www.instagram.com/p/'
    post_links = []
    while len(post_links) < post_count:
        links = [a.get_attribute('href')
                 for a in browser.find_elements_by_tag_name('a')]
        for link in links:
            if post in link and link not in post_links:
                post_links.append(link)

        print('\tPost ' + str(len(post_links)) + ' Processed')
        time_elaps = time.time() - start_time
        if time_elaps > (post_count/12*20):
            print('Time out on reading in post details, some posts skipped')
            browser.close()
            return post_links[:post_count]
        scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
        browser.execute_script(scroll_down)
        time.sleep(3)
    else:
        #browser.stop_client()
        browser.close()
        #os.system("taskkill /f /im chromedriver.exe /T")
        return post_links[:post_count]


def recent_hashtag_links(chrome_path, hashtag_term,post_count, output_dir):
    """
        With the input of an account page, scrape the 10 most recent posts urls
        Args:
        chrome_path: Path to chrome driver exe on local computer
        hashtag_term: Instagram hashtag. 
        post_count: default of 10, set as many or as few as you want
        Returns:
        A list with the unique url links for the most recent posts for the provided hashtag
        """
    print('Hashtag ' + hashtag_term + ' started:')
    start_time = time.time()
    url = "https://www.instagram.com/explore/tags/" + hashtag_term + "/"
    options = Options()
    options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    browser = Chrome(options=options, executable_path=chrome_path)
    browser.get(url)
    post = 'https://www.instagram.com/p/'
    post_links = []
    repeat_count = 0 #If it hangs and doesn't find new links for consecutive loops, break 

    while len(post_links) < post_count:

        prior_link_count = len(post_links)

        links = [a.get_attribute('href')
                 for a in browser.find_elements_by_tag_name('a')]

        for link in links:
            if post in link and link not in post_links:
                post_links.append(link)
        
        #Check if any new links actually got added
        if prior_link_count == len(post_links):
            repeat_count += 1

        #If too many repeats, break
        if repeat_count > 5:
            print('\n............Scraping issue, no new links being added.............')
            browser.close()
            return post_links[:post_count]


        #Dump log of links found every 100 or so. 12 links at a time are added after initial 33
        if len(post_links)  % 100 <= 10:
            write_file = os.path.join(output_dir,'link_log.csv')
            print("\n............Link log file written to.........")
            print(str(write_file))
            log_file = pd.Series(post_links)
            log_file.to_csv(write_file, index=False, header=False)

        print('\r Post ' + str(len(post_links)) + ' Processed', flush=True, end='')

        time_elaps = time.time() - start_time
        if time_elaps > (post_count/12*20):
            print('Time out on reading in post details, some posts skipped')
            browser.close()
            return post_links[:post_count]

        scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
        browser.execute_script(scroll_down)
        time.sleep(3)
    else:
        #browser.stop_client()
        browser.close()
        #os.system("taskkill /f /im chromedriver.exe /T")
        return post_links[:post_count]



def find_hashtags(comment):
    """
    Find hastags used in comment and return them
    Args:
    comment: Instagram comment text
    Returns:
    a list or individual hashtags if found in comment
    """
    hashtags = re.findall('#[A-Za-z]+', comment)
    if (len(hashtags) > 1) & (len(hashtags) != 1):
        return hashtags
    elif len(hashtags) == 1:
        return hashtags[0]
    else:
        return ""

def write_to_file(output_list, filename, fieldnames):
    '''
    Takes in a list of dictionary objects. Writes out a csv with specified field names.
    Can be used asynchronously as it appends
    '''
    with open(filename, 'a', encoding='utf8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # writer.writeheader()
        for row in output_list:
            writer.writerow(row)


def find_mentions(comment):
    """
    Find mentions used in comment and return them
    Args:
    comment: Instagram comment text
    Returns:
    a list or individual mentions if found in comment
    """
    mentions = re.findall('@[A-Za-z]+', comment)
    if (len(mentions) > 1) & (len(mentions) != 1):
        return mentions
    elif len(mentions) == 1:
        return mentions[0]
    else:
        return ""

def download_pic(browser, dir_name, user, suffix):
    try:
        soup = BeautifulSoup(browser.page_source, features="html.parser")
        photo_url = soup.find("meta", property="og:image")['content']
    except:
        print('No Image found, likely video only')
        return None

    image = requests.get(photo_url, stream=True)
    post_url = browser.current_url
    #Get last text between forward slashes...
    post_hash = post_url.split('/')[-2]

    with open(
            '{dirname}/{post_hash}.jpg'.format(dirname=dir_name, post_hash=post_hash),
            'wb') as out_file:
        shutil.copyfileobj(image.raw, out_file)

def download_details(browser, comment, url, hashtags):
    try:
        # This captures the standard like count.
        likes = browser.find_element_by_xpath(
            """//*[@id="react-root"]/section/main/div/div/
                article/div[2]/section[2]/div/div/button""").text.split()[0]
        post_type = 'photo'
    except:
        # This captures the like count for videos which is stored
        likes = browser.find_element_by_xpath(
            """//*[@id="react-root"]/section/main/div/div/
                article/div[2]/section[2]/div/span""").text.split()[0]
        post_type = 'video'

    #Get account name - for getting follower counts later:
    account_name = browser.find_element_by_xpath("""//*[@id="react-root"]/section/main/div/
    div[1]/article/header/div[2]/div[1]/div[1]/a""").text.split()[0]

    age = browser.find_element_by_css_selector('a time').text

    # mentions = find_mentions(comment)

    post_details = {'link': url, 'type': post_type, 'likes': likes,
                    'age': age, 'comment': comment, 'hashtags': hashtags,
                    'account_name': account_name}

    return post_details

def login_browser(browser,creds):
    '''
    Uses a chromedriver object and credentials to login and return the same object for downstream use
    creds should be a dict with keys: user,pass credentials for logging into Instagram
    '''

    browser.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    #Wait till username box loads for pasting
    #  delay = 10
    # user_box = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, '''//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[2]/div/label/input''')))
    user_box = browser.find_element_by_xpath('''//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[2]/div/label/input''')
    user_box.send_keys(creds['user'])  
    
    pass_box = browser.find_element_by_xpath('''//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input''')
    pass_box.send_keys(creds['pass'])
                                                
    submit_button = browser.find_element_by_xpath('''//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button''')
                                                    #//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[4]/button
    submit_button.submit()

    time.sleep(5)
                                                                
    return browser




def insta_user_details(chrome_path, user_urls, dir_name, creds, executor_url=None, session_id=None):
    """
    Take user urls and get follower information
    *** NOTE THAT INSTAGRAM WILL BAN AFTER ~ 500 SCRAPED WITHIN AN HOUR. NOT USABLE FOR LARGER SCRAPES
    Args:
    urls: List of urls for Instagram posts
    dir_name: directory to save user_log.csv into
    creds: dict with keys user,pass to log into Instagram
    executor,session_id: Parameters generated by an existing chromedriver instance. Use if re startng scraping to avoid logging in again.
    Returns:

    Side Effect:
    Saves user_log.csv to dir_name folder with followers per username
    """
    if executor_url is None and session_id is None:
        options = Options()
        # options.add_argument('--headless')
        #options.add_argument('--no-sandbox') #removed to see if it would help chrome windows not closing
        options.add_argument('--disable-gpu')
        # options.add_argument('user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)')
        # options.add_argument('--remote-debugging-port=9222')
        
        #Setup chromedriver. Loop through urls before checking for each item.
        browser = Chrome(options=options, executable_path=chrome_path)
        print("Executor Url", str(browser.command_executor._url))
        print("Session ID:", str(browser.session_id))

        browser = login_browser(browser,creds)
    else:
        #Connect to existing
        browser = webdriver.Remote(command_executor=executor_url,desired_capabilities={})
        # browser.close()   # this prevents the dummy browser
        # browser.session_id = session_id

    total_user_details = []

    url_count = 0
    for url in user_urls:

        print('\r Processing User: ' + str(url_count+1) + '/' + str(len(user_urls)), flush=True, end='')

        try:
            browser.get(url)

            followers = browser.find_element_by_xpath("""//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span""").text

            following = browser.find_element_by_xpath("""//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span""").text
            
            try:
                profile =  browser.find_element_by_xpath("""//*[@id="react-root"]/section/main/div/header/section/div[2]/span""").text
            except:
                print("Issue getting profile statement for account ", url)
                profile = ''

            user_details = {'account_name': url.split('/')[-2],
                'followers':followers,
            'following':following,
            'profile':profile}

            total_user_details.append(user_details)

            url_count += 1
            time.sleep(5)

            if url_count % 100 == 0:
                    write_to_file(total_user_details,
                                os.path.join(dir_name,'user_details.csv'),
                                fieldnames=['account_name','followers','following','profile'] )
        except:
            print("Issues with Profile", url)


    browser.close()

    write_to_file(total_user_details,
    os.path.join(dir_name,'user_details.csv'),
    fieldnames=['account_name','followers','following','profile'] )



def insta_link_list_details(chrome_path,urls, user, dir_name, term_list):
    """
    Take a list of post urls and writes out post details and download images.
    Args:
    urls: List of urls for Instagram posts
    dir_name: directory to save images into
    term_list: list of hashtags to restrict what images are saved.
    Returns:
    A list of dictionaries with details for each Instagram post, including link,
    post type, like/view count, age (when posted), and initial comment
    Side Effect:
    Downloads images to folders in a specified directory. 
    """

    options = Options()
    options.add_argument('--headless')
    #options.add_argument('--no-sandbox') #removed to see if it would help chrome windows not closing
    options.add_argument('--disable-gpu')
    # options.add_argument('--remote-debugging-port=9222')
    
    #Setup chromedriver. Loop through urls before checking for each item.
    browser = Chrome(options=options, executable_path=chrome_path)
    total_post_details = []


    img_counter = 0

    for url in urls:

        print('\r Processing Link: ' + str(img_counter+1) + '/' + str(len(urls)), flush=True, end='')
        browser.get(url)

        try:
            comment = browser.find_element_by_xpath(
                """//*[@id="react-root"]/section/main/div/div/
                    article/div[2]/div[1]/ul/div/li/div/div/div[2]/span""").text

        except:
            comment = "   "
            print('No Comment Found or error with comment xpath')

        hashtags = find_hashtags(comment)

        # Only downloads pictures of certain items

        download_pic(browser, dir_name, user, img_counter)
        post_details = download_details(browser, comment, url, hashtags)
        # print(post_details)
        total_post_details.append(post_details)



        time.sleep(1)
        img_counter += 1

    browser.close()

    write_to_file(total_post_details,os.path.join(dir_name,'post_details.csv'),
    fieldnames = ['link', 'type', 'likes',
                'age', 'comment', 'hashtags',
                'account_name'] )

    # return total_post_details


def insta_link_details(chrome_path,url, user, dir_name, term_list):
    """
    Take a post url and return post details and download image.
    Used for multiprocessing one url at a time
    Args:
    urls: A url for Instagram post. 
    dir_name: directory to save images into
    term_list: list of hashtags to restrict what images are saved.
    Returns:
    A list of dictionaries with details for each Instagram post, including link,
    post type, like/view count, age (when posted), and initial comment
    Side Effect:
    Downloads images to folders in a specified directory. 
    """

    options = Options()
    options.add_argument('--headless')
    #options.add_argument('--no-sandbox') #removed to see if it would help chrome windows not closing
    options.add_argument('--disable-gpu')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])#Prevents startup port message
    # options.add_argument('--remote-debugging-port=9222')
    
    #Setup chromedriver. Loop through urls before checking for each item.
    browser = Chrome(options=options, executable_path=chrome_path)
    total_post_details = []

    browser.get(url)

    try:
        comment = browser.find_element_by_xpath(
            """//*[@id="react-root"]/section/main/div/div/
                article/div[2]/div[1]/ul/div/li/div/div/div[2]/span""").text

    except:
        comment = "   "
        print('No Comment Found or error with comment xpath')

    hashtags = find_hashtags(comment)

    # Only downloads pictures of certain items

    download_pic(browser, dir_name, user, 1)
    post_details = download_details(browser, comment, url, hashtags)
    # print(post_details)
    total_post_details.append(post_details)

    time.sleep(1)

    browser.close()

    write_to_file(total_post_details,os.path.join(dir_name,'post_details.csv'),
    fieldnames=['link', 'type', 'likes',
                'age', 'comment', 'hashtags',
                'account_name'] )

    # return total_post_details


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


if __name__ == "__main__":

    from credentials import creds #Manually enter Instagram login info in a "creds" dict with keys: "user","pass". save to credentials.py

    #How many posts to TRY and download, will max out, sometimes randomly doesn't get all accessible.
    #May be getting blocked by non authenticated attempts.....
    num_posts = 15000

    #Specify users to scrape from.
    # user_list = ['kinuceramics'] 

    #or specify a hashtag list
    hashtag_list = ['ceramicvase']

    #Directory to save folders of images into per hashtag. 
    # Also saves link_log.csv of all links collected, and post_details.csv for each hashtag
    output_dir = r"C:\Users\Dustin\Python_Scripts\Generative_Deep_Learning\PotterGAN\PotterGAN\data"

    #Term list to restrict what items are saved. Checks hashtag on image before saving
    term_list = ['ceramicvase']

    #Set path to chromedriver executable
    chrome_path = 'C:/Program Files (x86)/chromedriver_win32/chromedriver.exe'

    start_time = time.time()

    #--------------------------FOR HASHTAG SCRAPING-----------------------------------
    for ht in hashtag_list:
        
        #Create the directory for the hashtag....
        output_dir_name = os.path.join(output_dir, ht)
        if not os.path.exists(output_dir_name):
            os.makedirs(output_dir_name)

        l = os.listdir(output_dir_name)

        if ('post_details.csv' in l )or ('link_log.csv' in l):
            print('post_details.csv or link_log.csv already exist in output directory. Skipping...Delete if fresh start required')
            print('Images can be left in output folder to avoid re downloading')
        else:
            #gets just post links
            recent_posts = recent_hashtag_links(chrome_path,ht, num_posts, output_dir_name)

            #Save links out for reference
            pd.Series(recent_posts).to_csv(os.path.join(output_dir_name,"link_log.csv"),index=False, header=False)

            details_time = time.time()

            #Get all images already in output dir to avoid re downloading
            l = os.listdir(output_dir_name)
            existing_images = ["https://www.instagram.com/p/" + x.split('.')[0] + '/' for x in l]
            
            print('\n Total posts to process: ' + str(len(recent_posts)))

            #Only get images not already in output directory
            recent_posts = list(set(recent_posts) - set(existing_images))

            print('Posts already existing in folder: ' + str(len(existing_images)))
            print('New posts to add to folder: ' + str(len(recent_posts)))

            # #Loop through post links, build details and download each.
            # Use function on each individual URL for multprocessing for now
            # #Use multiprocessing!
            with Pool(cpu_count()-1) as p:
                p.starmap(insta_link_list_details, 
                zip(repeat(chrome_path), chunker(recent_posts,30), repeat(ht), repeat(output_dir_name), repeat(term_list)),
                chunksize=1)
            
            p.close()
            p.join()

            # insta_link_list_details(path_chrome,recent_posts, ht, output_dir_name, term_list )

            print("All Posts Processed in: " + str(round(time.time() - start_time)) + ' seconds')


        # if 'user_details.csv' in l:
        #     print('User_details.csv already exists in output folder. Skipping....Delete if fresh start required')
        # else:
        #     print("Getting User Info on all Posts ")

        #     user_details = pd.read_csv(
        #         os.path.join(output_dir_name,'post_details.csv'),
        #     names=['post_link','media_type','likes','post_age','caption','hashtags','account_name'])

        #     user_details['user_urls'] = "https://www.instagram.com/" + user_details['account_name'] + "/"

        #     #Loop through, multiprocessing to get all user info. Followers,following, profile statement saved to a csv
        #     # with Pool(cpu_count()-3) as p:
        #     #     p.starmap(insta_user_details, 
        #     #     zip(repeat(chrome_path), chunker(user_details['user_urls'].values,500), repeat(output_dir_name), repeat(creds)),
        #     #     chunksize=1)
        #     # p.close()
        #     # p.join()

        #     #Single process Attempt:
        #     insta_user_details(chrome_path,user_details['user_urls'].values, 
        #     output_dir_name, 
        #     creds) 
        #     # executor_url='http://127.0.0.1:54475/devtools/browser/',
        #     # session_id='a584ad5e-63e8-4d28-94b2-b1c006aed224')
