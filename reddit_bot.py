from pymongo import MongoClient
from PIL import Image
import praw
import random
import pika
from time import sleep
import json

cluster = \
    MongoClient("your mongo client link")

db = cluster["your data base"]

# you'll need to add 2 collections to your database in MongoDB
postids_c = db["postids"]
tags_c = db["tags"]

params = pika.URLParameters\
    ('your cloudAMPQ link')

connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='your queue name', durable=True)


def ultimate_dump(dictodump):
    return json.dumps(dictodump, indent=4, sort_keys=True, default=str)


def make_square(im, min_size=256, fill_color=(0, 0, 0, 0)):
    x, y = im.size
    size = max(min_size, x, y)
    new_im = Image.new('RGB', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
    return new_im


def generate_path(dirc):
    new_img_path = dirc
    for i in range(12):
        new_img_path += str(random.randint(0, 9))

    new_img_path += ".jpg"
    return new_img_path


# connect to reddit
reddit = praw.Reddit(client_id='your client id', client_secret='your client secret', username='your bots username',
                     password='your password', user_agent='can be any string here')

subreddit_to_clone = reddit.subreddit('the subreddit you want')

while True:
    hot_feed = subreddit_to_clone.hot(limit=10)
    for submission in hot_feed:
        try:
            if submission.is_video:
                continue

            submission_image = vars(submission)['preview']['images'][0]['source']['url']
            redditpost_id = str(vars(submission)['id'])
            document = {"_id": redditpost_id}

            is_id_valid = postids_c.find_one(document)

            if is_id_valid is None:

                postids_c.insert_one(document)
                tags = tags_c.distinct("text")

                message = {
                    "tags": random.choice(tags),
                    "url": submission_image,
                    "id": redditpost_id,
                    "title": str(vars(submission)['title']),
                    "reddit_url": str(vars(submission)['permalink']),
                    "ocposter": str(vars(submission)['author'].name)
                }

                channel.basic_publish(exchange='', routing_key='your queue name', body=ultimate_dump(message))
            else:
                pass
        except KeyError as e:
            print(e.args[0] + " key missing")

    sleep(60)
