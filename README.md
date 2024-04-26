# Fasteffekt
CLI Tool to benchmark the Effekt language during developement.

Requirements:
- Effekt install that is at least newer than commit hash in ./latest_supported_effekt
- Installs for the effekt-backends you want to use (supported are JS, Chez-lift, chez-monadic and chez-callcc)
- Linux platform
- NodeJS >= 18

if you are unsure how to start:
1. clone the effekt-lang repo
2. manually checkout the commit hash from ./latest_supported_effekt 
3. run "git submodule init && git submodule update"
4. run sbt install
This will install the correct effekt version required for this tool.

How to use:
- clone repo locally
- navigate into repo root folder
- run "npm link" => this installs "fasteffekt" bin into your path using npm using symlink to repo
- verify installation: npm list -g | grep "fasteffekt"
- run "fasteffekt --help"
- done

Additional information:
The benchmarks are very susceptible to breaking changes in effekt.
We can only guarantee that the tool works for the specific commit hash supplied by us.

