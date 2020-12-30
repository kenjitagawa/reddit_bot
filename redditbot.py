import os
import random
import string
import time

import dotenv
import praw
import requests
import telebot
from informationsdb.main_db import InformationDataBase


class Bots:
    def __init__(self):
        print('Starting bots...')


# Telegram Bot
class TelegramBotCommands(Bots):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    # Welcome the user once Telegram bot starts.
    def welcome(self, message_user):
        _message = f"""Welcome to the the Reddit Bot. Here you will receive images from the Sub-Reddits "r\\pics" and "r\\itookapicture". 
        To use this bot;\
        /start\ 
        /images\
        /random-image\
        
        Have a great day! - The Developer
        """

        self.bot.send_message(message_user.chat.id, _message)


    def send_item(self, message_user, title, image_address):
        # Send the image and the title to the user.
        _message = f"""
        Title:
        {title}
        """
        self.bot.send_photo(message_user.chat.id, caption=_message, photo=image_address)



# Reddit Bot
class RedditBot(Bots):
    def __init__(self):
        super().__init__()
        CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
        CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
        REDIRECT_URI = os.getenv('REDIRECT_URI')
        self.db = InformationDataBase()

        self.reddit = praw.Reddit(client_id=CLIENT_ID,
                                  client_secret=CLIENT_SECRET,
                                  redirect_uri=REDIRECT_URI,
                                  user_agent="Redbot by u/k3nn7h")


    def get_images(self, limit=10, range_name=10, sub_reddit=['itookapicture','dogpictures']):
        # Get images from each subreddit and save with their respective names (directories)
        for sub in sub_reddit:
            subreddit = self.reddit.subreddit(sub)
            self.image_ext(sub)
            for submission in subreddit.new(limit=limit):

                print(f"{submission.url} being written...")
                img = requests.get(submission.url)
                # generating random name

                random_name = self.random_name(range_name)
                print('Generating name. Assigned name for {} is {}'.format(submission.url, random_name))
                #Saving images

                with open(f"{sub}\\{random_name}.png", 'wb') as file:
                    print(f'{random_name} generated in ".png" format. Find it in the "pictures" directory.')
                    file.write(img.content)
                    file.close()

                # image_information
                title = submission.title
                post_id = submission.id
                addr = f'{sub}\\{random_name}.png'
                print(f"""
                Title: {title} \n
                Post ID: {post_id} \n
                File Name: {random_name}
                Adding to DataBase...
                """)
                # Add files to MySQL databse
                try:
                    self.db.add_bd(post_id=post_id, title=title, name_photo=random_name, address=addr)


                except Exception as e:
                    print(e)
                    continue

            # Checking the files for proper extension.
            self.image_ext(sub)


    # Delete all of the images from the folders and clear the database
    def delete_all(self, sub_reddit=['itookapicture','dogpictures']):
        r = ''
        for s in sub_reddit:
            while r != 'y' or r != 'n':
                r = input('You are about to delete all images, are you sure(y/n)? ').lower()
                cwd = os.getcwd() + "\\" + s
                #Checking user input for a "yes"
                if r == 'y':
                    for file in os.listdir(cwd):
                        print(f'Removing {file}', end='\n')
                        os.remove(cwd + "\\" + file)
                        print(f'{file} removed!', end='\n')
                    break
        # Clear DB
        return self.db.clear_db()



    # Function to prepare for sending to Telegram
    def prepare(self):
        # Getting the directories
        dir = random.choice([dir for dir in os.listdir('.') if os.path.isdir(dir) and dir not in ['.idea', 'env', 'informationsdb']])
        def get_info():
            # Getting the images names
            try:
                img = random.choice(os.listdir(dir))
                name = img.split('.')[0]

                info = self.db.get_image_title(name)

                title = info[0]
                address = info[1]

                values = [title, img, address]
                print(values)

                return values

            except:
                return "ErroR!"


        #------------------------------------------------------------------------------------#

        while True:
            try:
                vals = get_info()
                return vals

            except IndexError as e:
                print(e, '\n Populating folders...')
                self.get_images(limit=10, range_name=10, sub_reddit=['pics','itookapicture'])
                vals = get_info()
                return vals


    @staticmethod
    def image_ext(sub_reddit):
        extensions = ('.jpg', '.png')
        cwd = os.getcwd()
        list_dirs = os.listdir(cwd)
        if sub_reddit not in list_dirs:
            os.mkdir(sub_reddit)

        img_dir = os.listdir(cwd + "\\" + sub_reddit)

        not_img = [file for file in img_dir if (file.endswith(extensions) ==False)]
        for file in not_img:
            print(f'Removing {file}...', end='\n')
            directory_file = os.path.join((cwd + "\\" + sub_reddit), file)
            print(directory_file, end='\n')
            os.remove(directory_file)
            print('Done! {} removed!'.format(file), end='\n')

        imgs_true = [True for file in (cwd + '\\' + sub_reddit) if file.endswith((extensions))]
        if all(imgs_true) == True:
            return True

    @staticmethod
    def random_name(_range=5):
        name = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(_range))
        return name

def main():

    @bot.message_handler(commands=['start', 'help'])
    def welcome(message_user):
        tel.welcome(message_user)

    @bot.message_handler(['images'])
    def send_item(message_user):
        while True:
            try:
                info = red.prepare()
                title = info[0]
                photo = open(info[2], "rb")

                print(info)

                print(f'Sending image to {message_user.chat.first_name}!')
                tel.send_item(message_user=message_user, title=title, image_address=photo) # Should work now...
                time.sleep(5)
            except:
                pass

    @bot.message_handler(commands=['random_image'])
    def rand_img(message_user):
        info = red.prepare()
        title = info[0]
        photo = open(info[2], "rb")


        return tel.send_item(message_user=message_user, title=title, image_address=photo)

    bot.polling()


if __name__ == "__main__":
    dotenv.load_dotenv('.env')
    TOKEN = os.getenv("TELEGRAM_TOKEN")

    # Initialising bot
    bot = telebot.TeleBot(TOKEN)

    tel = TelegramBotCommands(bot)
    red = RedditBot()

    print('Ready...')
    main()