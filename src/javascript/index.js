#!/usr/bin/env node

const {verify} = require('crypto');
const path = require('path');
const runAll = require("./compare/comparator")

const knownBackends = ["js", "chez-lift", "llvm", "ml"];
const passedArguments = {
    help: false,
    backend: "js",
    isVerify: false,
    version: false,
    verbose: false
};

process.argv.slice(2).map(p => p.toLowerCase()).forEach(arg => {
    if (arg == "--help" || arg == "-h") {
        passedArguments.help = true;
    } else if (arg.startsWith("--backend=")) {
        const arr = arg.split("=");
        if (arr.length == 2 && knownBackends.findIndex(p => p == arr[1]) != -1) {
            passedArguments.backend = arr[1];
            return;
        }
        throw new Error(`backend parameter is incorrect. must be --backend=js or one of \n${knownBackends.join("\t")}`)
    } else if (arg == "--small" || arg == "-s") {
        passedArguments.isVerify = true;
    } else if (arg == "--version" || arg == "-v") {
        passedArguments.version = true;
    } else if (arg == "--verbose") {
        passedArguments.verbose = true;
    } else {
        throw new Error(`can not parse argument: ${arg}`)
    }
})


if (passedArguments.help) {
    console.log(`
  fasteffekt - by Maximilian Marschall
  benchmarking the current install of the effekt language.
  will execute benchmarks in effekt and JS.
  outputs results to console and JSON file
  execute all benchmarks: fasteffekt [--small] [backend]
  run with: 
  options:
    --help, -h:      documentation
    --small, -s:     run minimal benchmark to verify they all work
    --version, -v:   show version of fasteffekt
    --verbose        verbose logging
    backend:         which effekt backend to use. defaults to JS. passed directly to effekt.sh
  `)
} else if (passedArguments.version) {
    const packageJson = require('../../package.json');
    // Access the version field and log it
    console.log('Package version:', packageJson.version);
} else {
    if (passedArguments.isVerify)
        console.log("verify-mode:", passedArguments.isVerify)
    if (passedArguments.verbose) {
        console.log("verbose");
    }
    console.log(`run for backend ${passedArguments.backend}`);

    runAll(passedArguments.isVerify ? "--verify" : "", passedArguments.backend, passedArguments.verbose);
}

