# dif-JSONMutator
A command-line tool that takes a JSON schema and a JSON sample as input, and generates a stream of mutated JSON payloads based on the schema. Uses a combination of random value generation within type constraints and guided mutations based on common JSON vulnerabilities (e.g., integer overflows, string injections). - Focused on Dynamically generates and injects fuzzed input into running applications (e.g., web applications, APIs). Focuses on identifying vulnerabilities by observing application behavior under unexpected input conditions. Supports various fuzzing strategies, such as mutation-based and generation-based fuzzing.

## Install
`git clone https://github.com/ShadowStrikeHQ/dif-jsonmutator`

## Usage
`./dif-jsonmutator [params]`

## Parameters
- `-h`: Show help message and exit
- `--schema`: Path to the JSON schema file.
- `--sample`: Path to the JSON sample file.
- `--iterations`: No description provided
- `--output`: Path to the output file to write the mutated payloads. If not specified, outputs to stdout.

## License
Copyright (c) ShadowStrikeHQ
