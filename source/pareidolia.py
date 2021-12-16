import os
import urllib
import urllib.request
from time import sleep

import praw
import tweepy

from credentials import *

# connect to reddit
reddit = praw.Reddit(client_id=ID,
                     client_secret=SECRET,
                     password=PASSWORD,
                     user_agent=AGENT,
                     username=USERNAME)

# connect to twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# create images folder if one does not exits
if not os.path.exists('./images'):
    os.mkdir('./images')

caption = ''  # caption for image
source = ''
extension = ''


def get_images():
    global caption, source
    statuses = []

    tweets = api.user_timeline(screen_name='pareidolia_bot')
    for status in tweets:
        status = status.text.split('https', 1)
        status = status[0].strip()

        if len(status) < 100:
            statuses.append(status)

    for submission in reddit.subreddit('Pareidolia').top(time_filter='day'):

        if 'https://i.imgur.com/' not in submission.url and 'https://i.redd.it' not in submission.url:
            continue

        if len(submission.title) > 100:
            continue


        if submission.title.lower() in statuses or "nsfw" in submission.title.lower():
            print('Tweet already exists in timeline or not suitable')
            continue

        img_url = submission.url
        source = 'https://www.reddit.com/r/Pareidolia/comments/' + str(
            submission)
        _, extension = os.path.splitext(img_url)

        urllib.request.urlretrieve(
            img_url, 'images/image' + extension)

        file_size = os.stat('images/image' + extension)

        if file_size.st_size > 3145728:
            print('file too big')
        else:
            caption = submission.title
            break

    send_tweet(extension)




def send_tweet(extension):
    global caption
    
    media = api.media_upload("images/image" + extension)
    api.update_status(status=caption.lower(), media_ids=[media.media_id])

    print('sending tweet', caption)


if __name__ == '__main__':
    get_images()
    print('sleeping 5 hours')
    while True:
        sleep(18000)  # tweet every 5 hours
        get_images()
