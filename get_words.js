"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.seededRandomInt = exports.modeData = exports.newSeed = void 0;
var seedrandom = require('seedrandom');
var fs = require('fs'); // export the datax
var rawdata = fs.readFileSync('./data/wordlist.json');
var wordList = JSON.parse(rawdata);
var data = {};
var daily;
function newSeed(mode) {
    var now = Date.now();
    switch (mode) {
        case 'daily':
            return Date.UTC(1970, 0, 1 + Math.floor((now - (new Date().getTimezoneOffset() * 60000 /* MINUTE */)) / 86400000 /* DAY */));
        case 'hourly':
            return now - (now % 3600000 /* HOUR */);
        // case GameMode.minutely:
        // 	return now - (now % ms.MINUTE);
    }
}
exports.newSeed = newSeed;
exports.modeData = {
    modes: [
        {
            name: "Daily",
            unit: 86400000 /* DAY */,
            start: 1642370400000,
            seed: newSeed('daily'),
            historical: false,
            streak: true,
        },
        {
            name: "Hourly",
            unit: 3600000 /* HOUR */,
            start: 1642528800000,
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
var dailyword = wordList[seededRandomInt(0, wordList.length, exports.modeData.modes[0].seed)];
console.log(dailyword);
function seededRandomInt(min, max, seed) {
    var rng = seedrandom("".concat(seed));
    return Math.floor(min + (max - min) * rng());
}
exports.seededRandomInt = seededRandomInt;
daily = wordList[(seededRandomInt(0, wordList.length, exports.modeData.modes[0].seed))]; // change to 1 for hourly
data['daily'] = daily;
var hourlys = data['hourly'] = {};
// @ts-ignore
var x = Array.from({ length: 24 }, function (x, i) { return i; });
var today = new Date();
for (var time in x) {
    // @ts-ignore
    var tempdate = new Date(today.getFullYear(), today.getMonth(), today.getDate(), time).valueOf();
    hourlys[time.toString()] = wordList[(seededRandomInt(0, wordList.length, tempdate))];
}
var lastupdated = "".concat(today.getDate(), "/").concat(today.getMonth() + 1, "/").concat(today.getFullYear());
data['lastupdated'] = lastupdated;
fs.writeFile("./data/generated_words.json", JSON.stringify(data), function (err) {
    if (err)
        throw err;
    console.log('complete');
});
