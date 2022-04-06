import json
import time

import aiohttp
import asyncio

start = time.perf_counter()

with open('json-data/wordlist.json', 'r') as wl:
    words = json.load(wl)


#def generate_hint(word):
#    lengh = len(set(word))
#    if lengh == 4:
#        return 'Hint: Double Letters!'
#    elif lengh == 3:
#        return 'Hint: Two Sets Of Double Letters!'
#    else:                                                  If hints.json is ever deleted use this
#        return ''
# words_dict = {word: ['', generate_hint(word)] for word in words}

word_data = {}
failed_words = []

def cleanup_data(data, word):
    data = data[0]
    if 'phonetic' in data.keys():
        data.pop('phonetic')
    data.pop('word')
    if data['phonetics']:
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

    print(f'cleaned up {word}')
    return data


async def retrieve_word_data(word: str):
    uri = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
    async with aiohttp.ClientSession() as session:
        async with session.get(uri) as response:
            if response.status != 200:
                failed_words.append(word)
                return print(f'Word {word} failed with uri {uri}')
            print(f'definition of {word} retrieved', end=' ')
            return cleanup_data(await response.json(), word)


async def main():
    for word in words:
        await asyncio.sleep(1)
        word_data[str(word)] = (await retrieve_word_data(word))
    dump_data(word_data)
    print('failed words', failed_words)


def dump_data(data, filepath: str = './json-data/word_data.json'):
    with open(filepath, 'w+') as data_file:
        json.dump(data, data_file)
        end = time.perf_counter()
        print(f'execution time was {end - start}s')


#dump_data(words_dict, 'json-data/hints.json')

#if __name__ == '__main__':              DONT RUN... NOT A GOOD IDEA unless you want to manually go through word_data.json and fix it
#    loop = asyncio.get_event_loop()
#    loop.run_until_complete(main())
