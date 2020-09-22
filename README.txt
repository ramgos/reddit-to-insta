This project is a template for making a bot that grabs posts from a subreddit
and posts them to instagram.

To set this up you'll need:
* a MongoDB account and cluster (If you're fairly new to mongoDB I suggest you watch TechWithTim's video)
* a CloudAMQP account (I'm planning on making a version in the future only dependent on MongoDB
* a reddit application
* an instagram account
* a heroku account and app

I hope to make in the future a solution that doesn't require CloudAMQP

First, install all the requirements listed in requirements.txt
and clone this repository.

Then you'll need to change in reddit_bot.py:
* the MongoClient link
* the CloudAMQP link
* the queue name
* the reddit client information

and in insta_bot:
* your instagram bot account details
* the CloudAMQP link
* the queue name

Now for deploying everythin to heroku, I'll not attempt to explain how to do it
because heroku themseleves made a great tutorial: https://devcenter.heroku.com/articles/git

my bot: https://www.instagram.com/195monke/