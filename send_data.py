import json
from os import getenv, environ
from os.path import exists
from urllib.parse import quote_plus
from dotenv import load_dotenv
import requests
from datetime import datetime

from utils import get_daily

hourmap = {'0': '12 AM',
           '1': '1 AM',
           '2': '2 AM',
           '3': '3 AM',
           '4': '4 AM',
           '5': '5 AM',
           '6': '6 AM',
           '7': '7 AM',
           '8': '8 AM',
           '9': '9 AM',
           '10': '10 AM',
           '11': '11 AM',
           '12': '12 PM',
           '13': '1 PM',
           '14': '2 PM',
           '15': '3 PM',
           '16': '4 PM',
           '17': '5 PM',
           '18': '6 PM',
           '19': '7 PM',
           '20': '8 PM',
           '21': '9 PM',
           '22': '10 PM',
           '23': '11 PM'}

with open('data/generated_words.json', 'r') as gw:
    gen_words = json.load(gw)


class StatsWrapper:
    def __init__(self):
        if exists('.env'):
            load_dotenv()
        self.PHONENUM = environ['PHONENUM']
        self.API_KEY = environ['APIKEY']
        self.message = ''
        self.date = datetime.today()  # .strftime('%A')

    def HourReplacment(self, hour: str):  # im sure there is a builtin for this, but I don't know it
        return hourmap[str(hour)]

    def send(self):
        API_URL = f"https://api.callmebot.com/signal/send.php?phone=+{self.PHONENUM}&apikey={self.API_KEY}&text={quote_plus(self.message)}"
        requests.get(API_URL)
        print('sent successfully')

    def generate_stats(self):
        daily = get_daily()
        hourlys = self.get_hourlys()
        hourly_words = ''
        for word in hourlys:
            hourly_words += f'\n{word}'

        self.message = f"""
        Hey Jason! it's {self.date.strftime('%A')}, {self.date.strftime('%Y %B %d')} And here are today's foodle Information
Daily word : {daily}
Hourly words ↓	↓	↓	
     
    {hourly_words}
        """
        print(self.message)
        self.send()

    def get_hourlys(self):  # returns list[tuple] github actions is being annoying
        # word/ hour
        raw_words = gen_words['hourly']
        raw_words_2 = [('grate', 0), ('pizza', 1), ('thyme', 2), ('scone', 3), ('pizza', 4), ('syrup', 5), ('quite', 6),
                       ('pasta', 7), ('salsa', 8), ('patty', 9), ('morry', 10), ('grill', 11), ('pecan', 12),
                       ('fresh', 13),
                       ('vodka', 14), ('kebab', 15), ('tangy', 16), ('sugar', 17), ('aroma', 18), ('shake', 19),
                       ('brine', 20), ('spill', 21), ('sweet', 22), ('mince', 23)]
        words = []
        for hour, word in raw_words.items():
            words.append(f'{word} at {self.HourReplacment(hour)}')
        return words

    def compute(self):
        self.generate_stats()


if __name__ == '__main__':
    Signal = StatsWrapper()
    Signal.compute()
