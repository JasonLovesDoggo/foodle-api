from os import getenv, linesep
from urllib.parse import quote_plus
from dotenv import load_dotenv
import requests
from datetime import datetime

hourmap = {0: '12 AM',
           1: '1 AM',
           2: '2 AM',
           3: '3 AM',
           4: '4 AM',
           5: '5 AM',
           6: '6 AM',
           7: '7 AM',
           8: '8 AM',
           9: '9 AM',
           10: '10 AM',
           11: '11 AM',
           12: '12 PM',
           13: '1 PM',
           14: '2 PM',
           15: '3 PM',
           16: '4 PM',
           17: '5 PM',
           18: '6 PM',
           19: '7 PM',
           20: '8 PM',
           21: '9 PM',
           22: '10 PM',
           23: '11 PM'}


class StatsWrapper:
    def __init__(self):
        load_dotenv()
        self.PHONENUM = getenv('phonenum')
        self.API_KEY = getenv('apikey')
        self.message = 'pee pee poo poo'
        self.date = datetime.today()  # .strftime('%A')

    def HourReplacment(self, hour: int):  # im sure there is a builtin for this, but I don't know it
        return hourmap[hour]

    def send(self):
        API_URL = f"https://api.callmebot.com/signal/send.php?phone=+{self.PHONENUM}&apikey={self.API_KEY}&text={quote_plus(self.message)}"
        requests.get(API_URL)

    def generate_stats(self):
        daily = self.get_daily()
        hourlys = self.get_hourlys()
        hourly_words = ''
        for word in hourlys:
            hourly_words += f'\n{word}'

        self.message = f"""
        Hey Jason! it's {self.date.strftime('%A')}, {self.date.strftime('%Y %B %d')} And here are today's foodle Information
        Daily word : {daily}
        Hourly words : {hourly_words}
        """
        print(self.message)  # self.send()

    def get_daily(self):
        return 'hello'

    def get_hourlys(self) -> list[tuple]:
        # word/ hour
        raw_words = [('grate', 0), ('pizza', 1), ('thyme', 2), ('scone', 3), ('pizza', 4), ('syrup', 5), ('quite', 6),
                     ('pasta', 7), ('salsa', 8), ('patty', 9), ('morry', 10), ('grill', 11), ('pecan', 12),
                     ('fresh', 13),
                     ('vodka', 14), ('kebab', 15), ('tangy', 16), ('sugar', 17), ('aroma', 18), ('shake', 19),
                     ('brine', 20), ('spill', 21), ('sweet', 22), ('mince', 23)]
        words = []
        for word, hour in raw_words:
            words.append(f'{word} at {self.HourReplacment(hour)}')
        return words

    def compute(self):
        self.generate_stats()


if __name__ == '__main__':
    Signal = StatsWrapper()
    Signal.compute()
