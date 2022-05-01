from os import environ
from os.path import exists
from urllib.parse import quote_plus
from dotenv import load_dotenv
import requests

from utils.utils import *


class StatsWrapper:
    def __init__(self):
        if exists('.env'):
            load_dotenv()
        self.PHONENUM = environ['PHONENUM']
        self.API_KEY = environ['APIKEY']
        self.message = ''
        self.date = datetime.today()  # .strftime('%A')

    def send(self):
        API_URL = f"https://api.callmebot.com/signal/send.php?phone=+{self.PHONENUM}&apikey={self.API_KEY}&text={quote_plus(self.message)}"
        headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'}
        requests.get(API_URL, headers=headers, timeout=8)
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
        words = []
        for hour, word in raw_words.items():
            words.append(f'{word} at {HourReplacment(hour)}')
        return words

    def compute(self):
        self.generate_stats()


if __name__ == '__main__':
    Signal = StatsWrapper()
    Signal.compute()
