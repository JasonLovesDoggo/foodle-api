let seedrandom = require('seedrandom');
var fs = require('fs'); // export the datax
import wordList from './data/wordlist.json';
let data = {}
let daily;


export function newSeed(mode: string) {
    const today = new Date();
    switch (mode) {
        case 'daily':
            return new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())).valueOf();
        case 'hourly':
            return new Date(today.getFullYear(), today.getMonth(), today.getDate(), today.getHours()).valueOf();
    }
}


export const modeData = {
    modes: [
        {
        name: "Daily", unit: 86400000, start: 1642370400000,	// 17/01/2022
        seed: newSeed('daily')
    }, {
        name: "Hourly",
        unit: 3600000,
        start: 1642528800000,	// 18/01/2022 8:00pm
        seed: newSeed('hourly')
    }]
};

export function seededRandomInt(min: number, max: number, seed: number) {
    const rng = seedrandom(`${seed}`);
    return Math.floor(min + (max - min) * rng());

}

daily = wordList[(seededRandomInt(0, wordList.length, modeData.modes[0].seed))];        // change to 1 for hourly
data['daily'] = daily;
let hourlys = data['hourly'] = {}
// @ts-ignore
let x = Array.from({length: 24}, (x, i) => i);
const today = new Date();
for (let time in x) {
    // @ts-ignore
    let tempdate = new Date(today.getFullYear(), today.getMonth(), today.getDate(), time).valueOf();
    hourlys.push(wordList[(seededRandomInt(0, wordList.length, tempdate))])
}



fs.writeFile("./data/generated_words.json", JSON.stringify(data), function(err) {
    if (err) throw err;
    console.log('complete');
    }
);
