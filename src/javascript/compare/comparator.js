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
const execute = (command, onOutput, onError) => {
    try {
        const output = execSync(command, {encoding: 'utf8'});
        onOutput(output.trim())
    } catch (error) {
        onError(error)
    }
}

function effektBuildCommand(backend, effektFile, executableName) {
    return `rm -f ./out/${executableName} && effekt.sh -b ${effektFile} --backend ${backend}`;
}

function effektCommand(amount, verifyArgs, executableName) {
    return `./out/${executableName} ${amount} ${verifyArgs}`
}

function executeCommands(commands, isVerify, backend, verbose) {
    const outputs = [];
    commands.forEach((command, index) => {
        const performance = {name: command[0], effekt: {}, error: false , js: {}}
        outputs.push(performance)

        console.log("running benchmark:", performance.name)
        const dirtyCd = `cd ${__dirname} && cd ../../..`;
        const amount = "10"
        const verifyArgs = isVerify ? "--verify" : ""

        const [executableName, effektPath, jsCmd] = command
        const effektCmd = [dirtyCd, effektCommand(amount, verifyArgs, executableName)].join(" && ")
        if (verbose)
            console.log(effektCmd);

        performance.command = effektCmd;
        const onRuntimeError = (error) => {
            console.error(`benchmark ${executableName} execution crashed in effekt. log in output file`)
            performance.error = true;
            performance.effekt = { error: "runtime error", status: error.status, output: error.output.join("\n")};
        }
        const runEffekt = () =>  execute(effektCmd, (time) => performance.effekt = time, onRuntimeError)
        const onCompileError = (error) => {
            console.error(`benchmark ${executableName} compilation failed. log in output file`)
            performance.error = true;
            performance.effekt = { error: "compile error", status: error.status, output: error.output.join("\n")};
        }
        execute([dirtyCd, effektBuildCommand(backend, effektPath, executableName)].join(" && "), runEffekt, onCompileError );

        // run pure JS benchmark
        const jsExecCmd = [dirtyCd, jsCmd + ` ${amount} ${verifyArgs}`].join(" && ");
        if (verbose)
            console.log(jsExecCmd);
        execute(jsExecCmd, (time) => performance.js = time)
    });

    const errors = outputs.filter( log => log.error)
    
    logErrors(errors);
    
    const successfullBenchmarks = outputs.filter( log => !log.error)
    logSuccesses(successfullBenchmarks);
}

function logSuccesses(benchmarkRuns ) {
    let analysis = benchmarkRuns.map(mark => ({
        name: mark.name,
        effekt: analyzeDurations(mark.effekt),
        js: analyzeDurations(mark.js)
    })).map(perf => ({...perf, ratio: perf.effekt.sum / perf.js.sum}))

    console.log("Mini analysis:", analysis.map(mark => ({
        name: mark.name,
        effekt: mark.effekt.sum,
        js: mark.js.sum,
        ratio: mark.effekt.sum / mark.js.sum
    })))
    const outputFile = "fasteffekt_results.json"
    console.log(`Verbose analysis saved to ${outputFile}`);
    fs.writeFileSync(outputFile, JSON.stringify(analysis, null, 3));
}

function logErrors(errors) {
    let analysis = errors
    .map(mark => {
        const loggedErrorForBenchmark = [mark.command,
            "error:",mark.effekt.error,
            "status:", mark.effekt.status,
            "output:", mark.effekt.output];
        return (loggedErrorForBenchmark.join("\n"))
    });
    const errorlog = analysis.join("\n\n");
    const outputFile = "fasteffekt_error.txt"
    fs.writeFileSync(outputFile, errorlog);
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
