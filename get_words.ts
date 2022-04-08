// @ts-ignore
import seedrandom from "seedrandom";
import wordList from "./data/words_5";

export const words = {
    ...wordList, contains: (word: string) => {
        return wordList.words.includes(word) || wordList.valid.includes(word);
    },
};

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
    default: 'daily', modes: [
        {
        name: "Daily", unit: 86400000, start: 1642370400000,	// 17/01/2022
        seed: newSeed('daily'), historical: false, streak: true,
    }, {
        name: "Hourly",
        unit: 3600000,
        start: 1642528800000,	// 18/01/2022 8:00pm
        seed: newSeed('hourly'),
        historical: false,
        icon: "m50,7h100v33c0,40 -35,40 -35,60c0,20 35,20 35,60v33h-100v-33c0,-40 35,-40 35,-60c0,-20 -35,-20 -35,-60z",
        streak: true,
    }]
};

export function seededRandomInt(min: number, max: number, seed: number) {
    const rng = seedrandom(`${seed}`);
    return Math.floor(min + (max - min) * rng());
}

let daily;
daily = words.words[seededRandomInt(0, words.words.length, modeData.modes[1].seed)];
console.log(daily)
process.env.daily_word = daily;
