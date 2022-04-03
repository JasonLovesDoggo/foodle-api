import json
import time

import aiohttp
import asyncio

start = time.perf_counter()

words = ['fresh', 'crust', 'serve', 'flesh', 'seedy', 'corny', 'salad', 'spicy', 'kebab', 'pulpy', 'vodka', 'peach',
         'drink', 'tangy', 'sugar', 'aroma', 'shake', 'spill', 'brine', 'sweet', 'mince', 'olive', 'zesty', 'scrap',
         'apron', 'cacao', 'bland', 'quart', 'smear', 'patty', 'hunky', 'treat', 'fungi', 'booze', 'thyme', 'grate',
         'soggy', 'enjoy', 'mocha', 'smoke', 'lunch', 'paste', 'carve', 'apple', 'honey', 'cream', 'diner', 'onion',
         'juicy', 'icing', 'whisk', 'sushi', 'candy', 'grape', 'burnt', 'dough', 'trout', 'filet', 'donut', 'bread',
         'dairy', 'tasty', 'puree', 'diary', 'penne', 'ramen', 'fishy', 'steak', 'caper', 'pizza', 'plate', 'broil',
         'cumin', 'gravy', 'yeast', 'cider', 'creme', 'grill', 'flour', 'beefy', 'scone', 'toast', 'saucy', 'spice',
         'feast', 'syrup', 'maize', 'cocoa', 'mango', 'chili', 'salty', 'pesto', 'salsa', 'spoon', 'crepe', 'water',
         'briny', 'bagel', 'melon', 'pasta', 'taffy', 'basil', 'wafer', 'snack', 'bacon', 'juice', 'wheat', 'berry',
         'fruit', 'sauce', 'fried', 'baste', 'pecan', 'curry', 'lemon', 'latte', 'broth', 'guava', 'fudge', 'femur',
         'gourd', 'farro', 'saute', 'flans', 'oreos', 'heinz', 'bhaji', 'torte', 'crisp', 'chips', 'anise', 'punch',
         'tuber', 'ugali', 'ladle', 'beans', 'spuds', 'stove', 'spork', 'herbs', 'lager', 'seeds', 'liver', 'namul',
         'lassi', 'ranch', 'cater', 'manti', 'straw', 'grain', 'crabs', 'jelly', 'adobo', 'taste', 'pilaf', 'mochi',
         'vegan', 'latke', 'munch', 'queso', 'curds', 'roast', 'fries', 'chard', 'mints', 'minty', 'dates', 'clams',
         'prune', 'aspic', 'rujak', 'gummy', 'cakes', 'baozi', 'melty']

words_dict = {i: ['', ''] for i in words}
# print(words_dict)

word_data = []
failed_words = []
example_data = [{"word": "apron", "phonetic": "/ˈeɪ.pɹən/", "phonetics": [{"text": "/ˈeɪ.pɹən/", "audio": ""},
                                                                          {"text": "/ˈeɪ.pɹən/",
                                                                           "audio": "https://api.dictionaryapi.dev/media/pronunciations/en/apron-us.mp3",
                                                                           "sourceUrl": "https://commons.wikimedia.org/w/index.php?curid=1317627",
                                                                           "license": {"name": "BY-SA 3.0",
                                                                                       "url": "https://creativecommons.org/licenses/by-sa/3.0"}}],
                 "meanings": [{"partOfSpeech": "noun", "definitions": [{
                     "definition": "An article of clothing worn over the front of the torso and/or legs for protection from spills; also historically worn by Freemasons and as part of women's fashion.",
                     "synonyms": [], "antonyms": []},
                     {"definition": "The short cassock ordinarily worn by English bishops.", "synonyms": [],
                         "antonyms": []},
                     {"definition": "A hard surface bordering a structure or area.", "synonyms": [], "antonyms": []},
                     {"definition": "The sides of a tree's canopy.", "synonyms": [], "antonyms": []},
                     {"definition": "The cap of a cannon; a piece of lead laid over the vent to keep the priming dry.",
                         "synonyms": [], "antonyms": []},
                     {"definition": "A removable cover for the passengers' feet and legs in an open horse carriage.",
                         "synonyms": [], "antonyms": []}], "synonyms": [], "antonyms": []}, {"partOfSpeech": "verb",
                                                                                             "definitions": [{
                                                                                                 "definition": "To cover with, or as if with, an apron.",
                                                                                                 "synonyms": [],
                                                                                                 "antonyms": []}],
                                                                                             "synonyms": [],
                                                                                             "antonyms": []}],
                 "license": {"name": "CC BY-SA 3.0", "url": "https://creativecommons.org/licenses/by-sa/3.0"},
                 "sourceUrls": ["https://en.wiktionary.org/wiki/apron"]}]


def cleanup_data(data, word):
    data = data[0]
    print(data)
    if 'phonetic' in data.keys():
        data.pop('phonetic')
    data.pop('word')
    audio = data['phonetics'][0]
    if 'text' in audio.keys():
        audio.pop('text')
    data.pop('phonetics')
    data['audio'] = audio
    meanings = data['meanings']
    for meaning in meanings:
        for definition in meaning['definitions']:
            if not definition['synonyms']:
                definition.pop('synonyms')
            if not definition['antonyms']:
                definition.pop('antonyms')
        if not meaning['synonyms']:
            meaning.pop('synonyms')
        if not meaning['antonyms']:
            meaning.pop('antonyms')

    return_data = ({str(word): data})
    return return_data


async def retrieve_word_data(word: str):
    uri = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
    async with aiohttp.ClientSession() as session:
        async with session.get(uri) as response:
            if response.status != 200:
                failed_words.append(word)
                return print(f'Word {word} failed with uri {uri}')
            print(f'definition of {word} retrived')
            return cleanup_data(await response.json(), word)


async def main():
    for word in words:
        await asyncio.sleep(1)
        word_data.append(await retrieve_word_data(word))
    dump_data(word_data)
    print('failed words', failed_words)


def dump_data(data):
    with open('./json-data/temp.json', 'w+') as data_file:
        json.dump(data, data_file)
        end = time.perf_counter()
        print(f'execution time was {end - start}s')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
