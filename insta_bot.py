from instabot import Bot
import pika
from PIL import Image
from time import sleep
import json
import requests
import schedule
import io
import os
import shutil

bot = Bot()
bot.login(username="your instagram username", password="your password")


# this function doesn't really matter unless your hosting
# the bot on a private VPS where you need to care about storage
def clean_dir():
    for filename in os.listdir("images"):
        file_path = os.path.join("images", filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def make_square(im, min_size=256, fill_color=(0, 0, 0, 0)):
    x, y = im.size
    size = max(min_size, x, y)
    new_im = Image.new('RGB', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
    return new_im


def upload_to_instagram(imagepath, imagecaption, imageid):
    bot.upload_photo(photo=imagepath, caption=imagecaption)
    print("sucess: added image with id:" + imageid)


params = pika.URLParameters\
    ('your cloudAMQP link')

connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='your queue name', durable=True)


def post():
    method_frame, header_frame, body = channel.basic_get('your queue name')
    if method_frame:
        # acknowledge
        channel.basic_ack(method_frame.delivery_tag)

        data = json.loads(body)

        tags = data['tags']
        source = requests.get(data['url'])
        postid = data['id']
        title = data['title']
        permlink = data['reddit_url']
        ocposter = data['ocposter']

        image_bytes = io.BytesIO(source.content)
        img = Image.open(image_bytes)
        detect_deleted = Image.open("if_you_are_looking_for_an_image.jpg")

        if list(img.getdata()) == list(detect_deleted.getdata()):
            print("image was deleted. URL: " + str(source))
        else:
            path = "images/" + postid + ".jpg"
            img = make_square(img)
            img.save(path)

            # instagram caption formating. you may change this to your liking
            caption = '"' + title + '"' + '\n' + "posted by: " + ocposter + " (on reddit)\n" + "https://reddit.com" + \
                      permlink + "\n" + "*\n" + "*\n" + "*\n" \
                      + tags

            sleep(5)

            bot.upload_photo(path, caption)
            print("sucess: added image with id:" + postid)
    else:
        print('No message in queue')


# in hours.txt all hours the bot will be posting are listed.
# to change the hours simply add new lines or delete lines from the txt file

hoursf = open("hours.txt", "r")
lines = hoursf.readlines()
hoursf.close()

for line in lines:
    schedule.every().day.at(line.replace("\n", "")).do(post)
schedule.every().day.at("00:30").do(clean_dir)

while True:
    schedule.run_pending()
    sleep(5)
