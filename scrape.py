from pathlib import Path
from urllib.parse import urlparse
import requests
import json
import shutil
import os
import re

class RedditImageScraper():
    _BASE_URL = 'https://www.reddit.com/r/'
    _IMAGE_WHITELIST = ['i.imgur.com', 'i.redd.it']

    def __init__(self, subreddit, limit):
        self.subreddit = subreddit
        self.limit = limit
        self.file_path = './' + subreddit

        self._get_posts()

    # Gets each individual post and returns them in a list 
    def _get_posts(self):
        try:
            r = requests.get(self._build_url(), headers={'User-Agent': 'Python Reaction Scraper'})
            r.raise_for_status()
        except requests.ConnectionError:
            print('Could not connect to website!')

        data = r.json()

        self._save_images(data['data']['children'])


    # Save all posts
    def _save_images(self, images):
        # Create directory for images
        Path(self.file_path).mkdir(exist_ok=True)

        # If the image contains a whitelisted url, store in new list 
        images = [image for image in images if 
                    any(whitelisted in image['data']['url'] for whitelisted in self._IMAGE_WHITELIST)]

        for image in images:
            image_details = image['data']
            image_url = str(image_details['url'])
            image_title = str(image_details['title'])
            image_ext = os.path.splitext(urlparse(image_url).path)[1]

            # Image has to have more than 25 upvotes and is not NSFW
            if(image_details['ups'] >= 25 and image_details['over_18'] is False):
                # If .gifv, then replace with .mp4
                if(image_ext == '.gifv'):
                    image_ext = '.mp4'
                    image_url = image_url.replace('.gifv', '.mp4')
                
                # Sanitize title for use as filename
                image_title = re.sub(r'[^0-9a-zA-Z_\[\] ]', '', image_title)

                print(image_url, ' ', image_title)

                try:
                    r = requests.get(image_url, stream=True)
                    r.raise_for_status()
                except requests.ConnectionError:
                    print('Could not grab an image', ' ', image_url)
                    continue

                # Write image to directory
                with open(self.file_path + '/' + image_title + image_ext, 'wb') as out_file:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, out_file)

        print('Finished downloading images from {0}'.format(self.subreddit))

    def _build_url(self):
        return self._BASE_URL + self.subreddit + '/.json?limit=' + str(self.limit)


x = RedditImageScraper(input('What subreddit would you like to scrape?: '), input('How many images?: '));