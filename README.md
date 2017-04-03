# Pedagogic CTF

This project is meant to ease the learning of software security.

You will be able to exploit simple programs with the source code in front of you. Then you will be ask to fix the code and submit it, the server will test your code (both looking for security vulnerabilities and testing functionalities). Then you will have your result, explaining where you failed.

## Contributions

Please feel free to contribute ! See in the */challs* directory for instructions of how to add challenges. Feel free to contact me on github or at: **hugodelval [at] gmail [dot] com**

## Getting Started

### Installation

Tested on Debian 8.7, golang 1.7.4 and docker 17.03.0-ce

Build containers, Go Api and AngularJS App:

`./build.sh`

Init challenges:

`./init.sh`

### Running !

`./run.sh`

## How does it work?

The user can do 3 things :

- exploit programs (and learn the vulnerability)
- correct challenges (learn how to fix the vulnerability)
- test and debug in playground

### Exploit

The server launch the program with the user input as *stdin*. The user goal is to find the **secret** of the program (something that should not be visible if there are no vulnerabilities).

If the user finds the secret, he can submit it to the server, which will check the secret validity and add points to the user.

### Correct

The user can then correct the program:

1. the user send the corrected code
2. the server copies the code in a new temporary directory and start a docker instance mapping it
4. the docker's entrypoint executes the init script of the program (init.py). This initialise the program, create secrets, databases and so on...
5. the docker's entrypoint executes submitted code using several tests that check if the program still works (challs/*/check.py)
6. the docker's entrypoint executes submitted code using several tests that check if the program is no more exploitable (challs/*/exploit.py)
7. the server stops the container and deletes the temporary folder
8. the server gives points to the users if the program still works and is no more exploitable
