import pandas as pd
import time
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import re
import os
import datetime as dt
import requests
from bs4 import BeautifulSoup
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


def recent_hashtag_links(chrome_path, hashtag_term, post_count=10):
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

    image = requests.get(photo_url, stream=True)

    with open(
            '{dirname}/img_{user}_{suffix}.jpg'.format(dirname=dir_name, user=user, suffix=suffix),
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
    age = browser.find_element_by_css_selector('a time').text

    mentions = find_mentions(comment)
    post_details = {'link': url, 'type': post_type, 'likes/views': likes,
                    'age': age, 'comment': comment, 'hashtags': hashtags,
                    'mentions': mentions}
    return post_details


def insta_link_details(chrome_path,urls, user, dir_name, term_list):
    """
    Take a post url and return post details and download image.
    Args:
    urls: a list of urls for Instagram posts
    dir_name: directory to save images into
    term_list: list of hashtags to restrict what images are saved. Will be used to make subfolders
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
    
    #Setup chromedriver. Loop through urls before checking for each item.
    browser = Chrome(options=options, executable_path=chrome_path)
    total_post_details = pd.DataFrame()


    img_counter = 0
    for url in urls:
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
        for term in term_list:

            if any(term in ht for ht in hashtags):
                output_dir_name = os.path.join(dir_name,term)

                #Create the directory....
                if not os.path.exists(output_dir_name):
                    os.makedirs(output_dir_name)


                download_pic(browser, output_dir_name, user, img_counter)
                post_details = download_details(browser, comment, url, hashtags)
                total_post_details = total_post_details.append(post_details, ignore_index=True)

            else:
                post_details = {}

        time.sleep(1)
        img_counter += 1

    browser.close()

    return total_post_details



if __name__ == "__main__":

    #How many posts to TRY and download, will max out, sometimes randomly doesn't get all accessible.
    #May be getting blocked by non authenticated attempts.....
    num_posts = 50000

    #Specify users to scrape from.
    user_list = ['kinuceramics']

    #or specify a hashtag list
    hashtag_list = ['ceramicmug']

    #Directory to save folders of images into
    output_dir = r"C:\Users\Dustin\Python_Scripts\Generative_Deep_Learning\PotterGAN\PotterGAN\data"

    #Term list to restrict what items are saved. Checks hashtag on image before saving
    term_list = ['ceramicmug']

    #Set path to chromedriver executable
    path_chrome = 'C:/Program Files (x86)/chromedriver_win32/chromedriver.exe'

    start_time = time.time()

    #--------------------------FOR USERS SCRAPING-----------------------------------
    # for user in user_list:

    #     #gets just post links
    #     recent_posts = recent_post_links(path_chrome,user, num_posts)

    #     #does the actual downloading from the post links
    #     details_time = time.time()
    #     #Loop through post links, build details and download each
    #     details = insta_link_details(path_chrome,recent_posts, user, output_dir, term_list )

    #     print("Details Processed in: " + str(round(time.time() - details_time)) + "s")

    #     time_stamp = dt.datetime.strftime( dt.datetime.now(), format ="%Y_%M_%d")
    #     file_name = user + '_' + str(num_posts) +'_' + time_stamp + '.csv'
    #     details.to_csv(os.path.join(output_dir,file_name))

    #     print("All Posts Processed in: " + str(round(time.time() - start_time)) + 'seconds')

    #--------------------------FOR HASHTAG SCRAPING-----------------------------------
    for ht in hashtag_list:

        #gets just post links
        recent_posts = recent_hashtag_links(path_chrome,ht, num_posts)

        #does the actual downloading from the post links
        details_time = time.time()
        #Loop through post links, build details and download each
        details = insta_link_details(path_chrome,recent_posts, ht, output_dir, term_list )

        print("Details Processed in: " + str(round(time.time() - details_time)) + "s")

        time_stamp = dt.datetime.strftime( dt.datetime.now(), format ="%Y_%M_%d")
        file_name = ht + '_' + str(num_posts) +'_' + time_stamp + '.csv'
        details.to_csv(os.path.join(output_dir,file_name))

        print("All Posts Processed in: " + str(round(time.time() - start_time)) + 'seconds')