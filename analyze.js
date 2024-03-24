const fs = require('fs');

function findMedian(arr) {
    arr.sort((a, b) => a - b);
    const middleIndex = Math.floor(arr.length / 2);

    if (arr.length % 2 === 0) {
        return (arr[middleIndex - 1] + arr[middleIndex]) / 2;
    } else {
        return arr[middleIndex];
    }
}

function calculateGeometricMean(array) {
    if (!Array.isArray(array) || array.length === 0) {
        throw new Error('Input must be a non-empty array.');
    }
    let sum = 0;
    array.filter(x => x > 0).forEach(val =>
        sum += Math.log(val)
    );
    sum = sum / array.length;
    return sum;
}

function calculateStandardDeviation(array) {
    if (!Array.isArray(array) || array.length === 0) {
        throw new Error('Input must be a non-empty array.');
    }

    const standardDeviation = (array, usePopulation = false) => {
        const mean = array.reduce((acc, val) => acc + val, 0) / array.length;
        return Math.sqrt(
            array.reduce((acc, val) => acc.concat((val - mean) ** 2), []).reduce((acc, val) => acc + val, 0) /
            (array.length - (usePopulation ? 0 : 1))
        );
    };

    return standardDeviation(array)
}

function getKeyValuesFromFile(filename, backend) {
    const data = fs.readFileSync(filename, 'utf8');

    try {
        const jsonData = JSON.parse(data);

        // Iterate over each object in the array
        const keyValues = jsonData.map(item => {
            if (item.effekt && item.effekt.durations && Array.isArray(item.effekt.durations)) {
                return {
                    name: item.name,
                    geomean: calculateGeometricMean(item.effekt.durations),
                    standardDeviation: calculateStandardDeviation(item.effekt.durations),
                    min: Math.min(...item.effekt.durations),
                    max: Math.max(...item.effekt.durations),
                    median: findMedian(item.effekt.durations)
                }
            }
        });

        result.push({
            backend: backend,
            filename: filename,
            benchmarks: keyValues
        })


    } catch (error) {
        console.error('Error parsing JSON:', error);
    }
}
// Check if filename is provided as command-line argument
if (process.argv.length < 5) {
    console.error('Please provide the filename as a command-line argument.');
    process.exit(1);
}

const js = process.argv[2];
const monadic = process.argv[3];
const callcc = process.argv[4];
const lift = process.argv[5];

const result = [];

getKeyValuesFromFile(js, "effekt-javascript");
getKeyValuesFromFile(monadic, "effekt-chez-monadic");
getKeyValuesFromFile(callcc, "effekt-chez-callcc");
getKeyValuesFromFile(lift, "effekt-chez-lift");

process.stdout.write(JSON.stringify(result,null,3))
process.stdout.end();
