import json
import time

import aiohttp
import asyncio

start = time.perf_counter()

with open('data/wordlist.json', 'r') as wl:
    words = json.load(wl)

with open('data/missing-info.json', 'r') as mi:
    missing_words_data = json.load(mi)
    missing_words_with_info = missing_words_data['wordlist']

# def generate_hint(word):
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


async def cleanup_data(data, word, recleandata=True):
    if recleandata:
        data = data[0]
    if 'phonetic' in data.keys():
        data.pop('phonetic')
    if 'word' in data.keys():
        data.pop('word')
    if 'phonetics' in data.keys():
        if data['phonetics']:
            audio = data['phonetics'][0]
            if 'text' in audio.keys():
                audio.pop('text')
            data.pop('phonetics')
            data['audio'] = audio
    meanings = data['meanings']
    for meaning in meanings:
        for definition in meaning['definitions']:
            if 'synonyms' in definition.keys():
                if not definition['synonyms']:
                    definition.pop('synonyms')
            if 'antonyms' in definition.keys():
                if not definition['antonyms']:
                    definition.pop('antonyms')
        if 'synonyms' in meaning.keys():
            if not meaning['synonyms']:
                meaning.pop('synonyms')
        if 'antonyms' in meaning.keys():
            if not meaning['antonyms']:
                meaning.pop('antonyms')

    await asyncio.sleep(.5)
    print(f' & cleaned it up')
    return data


async def retrieve_word_data(word: str):
    uri = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
    async with aiohttp.ClientSession() as session:
        async with session.get(uri) as response:
            if response.status != 200:
                if word in missing_words_with_info:
                    print(
                        f'definition of {word} failed to fetch {"But we have the info in word-data.json" if word in missing_words_with_info else ""}',
                        end='')
                    return await cleanup_data(missing_words_data[word], word, recleandata=False)
                failed_words.append(word)
                return print(
                    f'Word {word} failed with uri {uri} {"But we have the info in word-data.json" if word in missing_words_with_info else ""}')

            print(f'definition of {word} retrieved', end=' ')

            return await cleanup_data(await response.json(), word)


async def main():
    for word in words:
        await asyncio.sleep(.5)
        word_data[str(word)] = (await retrieve_word_data(word))

    dump_data(word_data)
    if failed_words:
        print('failed words', failed_words)
    else:
        print('No Failed Words!!!!')


def dump_data(data, filepath: str = './data/word_data.json'):
    with open(filepath, 'w+') as data_file:
        json.dump(data, data_file)
        end = time.perf_counter()
        print(f'execution time was {round(end - start, 6)}s')


# dump_data(words_dict, 'data/hints.json')  Don't uncomment this

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
