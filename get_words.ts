let seedrandom = require('seedrandom');
var fs = require('fs'); // export the datax
let rawdata = fs.readFileSync('./data/wordlist.json');
let wordList = JSON.parse(rawdata);
let data = {}
let daily;
const enum ms {
	SECOND = 1000,
	MINUTE = 1000 * 60,
	HOUR = 1000 * 60 * 60,
	DAY = 1000 * 60 * 60 * 24,
}

export function newSeed(mode: string) {
    const now = Date.now();
    switch (mode) {
        case 'daily':
            return Date.UTC(1970, 0, 1 + Math.floor((now - (new Date().getTimezoneOffset() * ms.MINUTE)) / ms.DAY));
        case 'hourly':
            return now - (now % ms.HOUR);
        // case GameMode.minutely:
        // 	return now - (now % ms.MINUTE);
    }
}

export const modeData = {
    modes: [
        {
            name: "Daily",
            unit: ms.DAY,
            start: 1642370400000,	// 17/01/2022     UTC+2
            seed: newSeed('daily'),
            historical: false,
            streak: true,
        },
        {
            name: "Hourly",
            unit: ms.HOUR,
            start: 1642528800000,	// 18/01/2022 8:00pm    UTC+2
            seed: newSeed('hourly'),
            historical: false,
            icon: "m50,7h100v33c0,40 -35,40 -35,60c0,20 35,20 35,60v33h-100v-33c0,-40 35,-40 35,-60c0,-20 -35,-20 -35,-60z",
            streak: true,
        }
        // {
        // 	name: "Minutely",
        // 	unit: ms.MINUTE,
        // 	start: 1642528800000,	// 18/01/2022 8:00pm
        // 	seed: newSeed(GameMode.minutely),
        // 	historical: false,
    ]
};
let dailyword = wordList[seededRandomInt(0, wordList.length, modeData.modes[0].seed)];
console.log(dailyword)
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
    hourlys[time.toString()] = wordList[(seededRandomInt(0, wordList.length, tempdate))]
}

let lastupdated = `${today.getDate()}/${today.getMonth() + 1}/${today.getFullYear()}`
data['lastupdated'] = lastupdated
fs.writeFile("./data/generated_words.json", JSON.stringify(data), function(err) {
    if (err) throw err;
    console.log('complete');
    }
);
