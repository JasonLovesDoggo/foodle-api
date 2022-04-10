"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
exports.__esModule = true;
exports.seededRandomInt = exports.modeData = exports.newSeed = void 0;
var seedrandom = require('seedrandom');
var fs = require('fs'); // export the datax
var wordlist_json_1 = __importDefault(require("./data/wordlist.json"));
var data = {};
var daily;
function newSeed(mode) {
    var today = new Date();
    switch (mode) {
        case 'daily':
            return new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())).valueOf();
        case 'hourly':
            return new Date(today.getFullYear(), today.getMonth(), today.getDate(), today.getHours()).valueOf();
    }
}
exports.newSeed = newSeed;
exports.modeData = {
    modes: [
        {
            name: "Daily", unit: 86400000, start: 1642370400000,
            seed: newSeed('daily')
        }, {
            name: "Hourly",
            unit: 3600000,
            start: 1642528800000,
            seed: newSeed('hourly')
        }
    ]
};
function seededRandomInt(min, max, seed) {
    var rng = seedrandom("".concat(seed));
    return Math.floor(min + (max - min) * rng());
}
exports.seededRandomInt = seededRandomInt;
daily = wordlist_json_1["default"][(seededRandomInt(0, wordlist_json_1["default"].length, exports.modeData.modes[0].seed))]; // change to 1 for hourly
data['daily'] = daily;
var hourlys = data['hourly'] = {};
// @ts-ignore
var x = Array.from({ length: 24 }, function (x, i) { return i; });
var today = new Date();
for (var time in x) {
    // @ts-ignore
    var tempdate = new Date(today.getFullYear(), today.getMonth(), today.getDate(), time).valueOf();
    hourlys[time.toString()] = wordlist_json_1["default"][(seededRandomInt(0, wordlist_json_1["default"].length, tempdate))];
}
fs.writeFile("./data/generated_words.json", JSON.stringify(data), function (err) {
    if (err)
        throw err;
    console.log('complete');
});
