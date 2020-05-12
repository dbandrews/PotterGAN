import pandas as pd
import time
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import re
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
        time.sleep(15)
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


def insta_link_details(url, user, suffix):
    """
    Take a post url and return post details
    Args:
    urls: a list of urls for Instagram posts
    Returns:
    A list of dictionaries with details for each Instagram post, including link,
    post type, like/view count, age (when posted), and initial comment
    """

    options = Options()
    options.add_argument('--headless')
    #options.add_argument('--no-sandbox') #removed to see if it would help chrome windows not closing
    options.add_argument('--disable-gpu')
    browser = Chrome(options=options, executable_path="C:\\Users\\andrewt02\\Desktop\\chromedriver.exe")
    browser.get(url)

    try:
        comment = browser.find_element_by_xpath(
            """//*[@id="react-root"]/section/main/div/div/
                article/div[2]/div[1]/ul/div/li/div/div/div[2]/span""").text

    except:
        comment = "   "
        print('No Comment Found or error with comment xpath')

    hashtags = find_hashtags(comment)

    # Only downloads pictures of mugs
    if any('mug' in ht for ht in hashtags) or any('cup' in ht for ht in hashtags):
        dir_name = 'data/raw/MugImages'
        download_pic(browser, dir_name, user, suffix)
        post_details = download_details(browser, comment, url, hashtags)

    if any('plate' in ht for ht in hashtags):
        dir_name = 'data/raw/PlateImages'
        download_pic(browser, dir_name, user, suffix)
        post_details = download_details(browser, comment, url, hashtags)

    if any('vase' in ht for ht in hashtags):
        dir_name = 'data/raw/VaseImages'
        download_pic(browser, dir_name, user, suffix)
        post_details = download_details(browser, comment, url, hashtags)

    if any('teapot' in ht for ht in hashtags):
        dir_name = 'data/raw/TeapotImages'
        download_pic(browser, dir_name, user, suffix)
        post_details = download_details(browser, comment, url, hashtags)

    if any('bowl' in ht for ht in hashtags):
        dir_name = 'data/raw/BowlImages'
        download_pic(browser, dir_name, user, suffix)
        post_details = download_details(browser, comment, url, hashtags)

    else:
        post_details = {}

    time.sleep(1)
    browser.close()

    return post_details



if __name__ == "__main__":

    #How many posts to TRY and download, will max out, sometimes randomly doesn't get all accessible
    num_posts = 500

    user_list = ['tythetyger', 'dvstynthewynd']

    path_chrome = "YOUR_PATH_HERE\\chromedriver.exe"

    start_time = time.time()
    for user in user_list:

        #gets just post linke
        recent_posts = recent_post_links(user, num_posts)

        user_data = pd.DataFrame()

        post_number=0

        #does the actual downloading from the post links
        for post in recent_posts:
            details_time = time.time()
            details = insta_link_details(post, user, post_number)
            post_number = post_number+1

            #saves out the post details
            user_data = user_data.append(details, ignore_index=True)
            print("Details Processed in: " + str(time.time() - details_time) + "s")

        user_data.to_csv(user + '_' + str(num_posts) + 'posts_19-04-2020.csv')
        print("All Posts Processed in: " + str(time.time() - start_time) + 'seconds')