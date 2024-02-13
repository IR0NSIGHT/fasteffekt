/**
 * this file is the main benchmark-tool logic.
 * it has predefined shell commands that it executes, measures and logs
 * called by index.js
 */
const {execSync} = require('child_process');
const fs = require('fs');


// List of shell commands
const commands = [
  ['permute', 'src/effekt/benchmark/permute.effekt', 'node src/javascript/Permute.js'],
  ["nbody", "src/effekt/benchmark/nbody.effekt", "node src/javascript/Nbody.js"],
  ['list', 'src/effekt/benchmark/list.effekt', 'node src/javascript/List.js'],
  ["mandelbrot", "src/effekt/benchmark/mandelbrot.effekt", "node src/javascript/Mandelbrot.js"],
  ["bounce","src/effekt/benchmark/bounce.effekt","node src/javascript/bounce.js"],
  ['towers','src/effekt/benchmark/towers.effekt',"node src/javascript/towers.js"],
  ["sieve","src/effekt/benchmark/sieve.effekt", "node src/javascript/Sieve.js"],
  ["storage","src/effekt/benchmark/storage.effekt","node src/javascript/Storage.js"],
  ["queens","src/effekt/benchmark/queens.effekt","node src/javascript/queens.js"]
  // Add more commands as needed
];

/**
 * synced execution, only returns once command is done.
 * @param {*} command shell command as string to execute
 * @param {*} onOutput (commandOutput) => Void callback function
 */
const execute = (command, onOutput) => {
    const output = execSync(command, {encoding: 'utf8'});
    onOutput(output.trim())
}

function effektCommand(backend, effektFile, amount, verifyArgs, name) {
    return `effekt.sh -b ${effektFile} --backend ${backend} && ./out/${name} ${amount} ${verifyArgs}`
}

function executeCommands(commands, isVerify, backend, verbose) {
    const outputs = [];
    commands.forEach((command, index) => {
        const performance = {name: command[0], effekt: {}, js: {}}
        outputs.push(performance)

        console.log("running benchmark:", performance.name)
        const dirtyCd = `cd ${__dirname} && cd ../../..`;
        const amount = "10"
        const verifyArgs = isVerify ? "--verify" : ""

        const [executableName, effektPath, jsCmd] = command
        const effektCmd = [dirtyCd, effektCommand(backend, effektPath, amount, verifyArgs, executableName)].join(" && ")
        if (verbose)
            console.log(effektCmd);
        try {
            performance.command = effektCmd;
            execute(effektCmd, (time) => performance.effekt = time)
        } catch (error) {
            console.error(`benchmark ${executableName} execution crashed in effekt. log in output file`)
            performance.effekt = error;
        }
        // run pure JS benchmark
        const jsExecCmd = [dirtyCd, jsCmd + ` ${amount} ${verifyArgs}`].join(" && ");
        if (verbose)
            console.log(jsExecCmd);
        execute(jsExecCmd, (time) => performance.js = time)
    });


    try {
        let analysis = outputs.map(mark => ({
            name: mark.name,
            effekt: analyzeDurations(mark.effekt),
            js: analyzeDurations(mark.js)
        }))
        analysis = analysis.map(perf => ({...perf, ratio: perf.effekt.sum / perf.js.sum}))
        console.log("Mini analysis:", analysis.map(mark => ({
            name: mark.name,
            effekt: mark.effekt.sum,
            js: mark.js.sum,
            ratio: mark.effekt.sum / mark.js.sum
        })))
        const outputFile = "fasteffekt_results.json"
        console.log(`Verbose analysis saved to ${outputFile}`);
        fs.writeFileSync(outputFile, JSON.stringify(analysis, null, 3));
    } catch {
        let analysis = outputs
            .map(mark => ([mark.command, mark.effekt].join("\n")))
        const errorlog = analysis.join("\n\n");
        const outputFile = "fasteffekt_error.txt"
        fs.writeFileSync(outputFile, errorlog);
        console.error("error occured: not all benchmarks returned readable values. See " + outputFile + " for detailed errors.")
        process.exit(1);
    }
}

/**
 * analyze duration array
 * @param {string} durations : list of duration times for every benchmark run
 */
const analyzeDurations = (durations) => {
    durations = JSON.parse(durations);
    const sum = durations.reduce((accumulator, currentValue) => accumulator + currentValue, 0);
    const avg = sum / durations.length

    return {sum: sum, avg: avg, durations: durations}
}


const runAll = (isVerify, backend, verbose) => {
    if (verbose)
        console.log(`run all benchmarks with backend=${backend}, small=${isVerify}`)
    executeCommands(commands, isVerify, backend, verbose)
}
module.exports = runAll
// 
