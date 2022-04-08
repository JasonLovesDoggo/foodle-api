"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
exports.__esModule = true;
exports.seededRandomInt = exports.modeData = exports.newSeed = exports.words = void 0;
// @ts-ignore
var seedrandom_1 = require("seedrandom");
var words_5_1 = require("./data/words_5");
exports.words = __assign(__assign({}, words_5_1["default"]), { contains: function (word) {
        return words_5_1["default"].words.includes(word) || words_5_1["default"].valid.includes(word);
    } });
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
    "default": 'daily', modes: [
        {
            name: "Daily", unit: 86400000, start: 1642370400000,
            seed: newSeed('daily'), historical: false, streak: true
        }, {
            name: "Hourly",
            unit: 3600000,
            start: 1642528800000,
            seed: newSeed('hourly'),
            historical: false,
            icon: "m50,7h100v33c0,40 -35,40 -35,60c0,20 35,20 35,60v33h-100v-33c0,-40 35,-40 35,-60c0,-20 -35,-20 -35,-60z",
            streak: true
        }
    ]
};
function seededRandomInt(min, max, seed) {
    var rng = (0, seedrandom_1["default"])("".concat(seed));
    return Math.floor(min + (max - min) * rng());
}
exports.seededRandomInt = seededRandomInt;
var daily;
daily = exports.words.words[seededRandomInt(0, exports.words.words.length, exports.modeData.modes[1].seed)];
console.log(daily);
process.env.daily_word = daily;
