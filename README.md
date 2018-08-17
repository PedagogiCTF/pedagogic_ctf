# Pedagogic CTF

This project is meant to ease the learning of software security.

You will be able to exploit simple programs with the source code in front of you. Then you will be ask to fix the code and submit it, the server will test your code (both looking for security vulnerabilities and testing functionalities). Then you will have your result, explaining where you failed.

## Contributions

Please feel free to contribute ! See in the */challs* directory for instructions of how to add challenges.

## Getting Started

### Installation

You will need to install these software:
- docker
- sudo
- git
- make

If you want to build the project yourself, you will also need:
- python3
- nodejs + bower
- golang

Launch this command:
```bash
git clone https://github.com/PedagogiCTF/pedagogic_ctf
cd pedagogic_ctf
```

This project was tested on debian stretch but should work on any Linux distribution.

### Running !

Please make sure that the ports **80** and **443** are available on your local machine 
(shutdown *apache*, *nginx* and so on..).

Then create the ssl volume using these commands:

```bash
docker volume create frontend-ssl
bash ssl.sh # Please follow the instructions
```

Once you've added the ssl certificates, you can build and launch the app:

```bash
# This will fetch the docker images from https://hub.docker.com/r/pedagogictf/
# Then it will launch them
make run-prod
```

The pulling of docker images can be a bit long depending on your network, go drink a coffee :)

As soon as the previous command ends you can access the service at `http://localhost`. 
Note that if you used the method in `ssl.sh` to generate the certificate, the certificate will 
be auto-signed, which means that you will have a warning in your browser. 
Use something like https://letsencrypt.org to have a real certificate signed by a valid CA.


## How does it work?

The user can do 3 things:

- exploit programs (and learn the vulnerability)
- correct challenges (learn how to fix the vulnerability)
- test and debug in playground

### Exploit

The server launch the program with the user input as *argv*. The user goal is to find the **secret** of the program (something that should not be visible if there are no vulnerabilities).

If the user finds the secret, he can submit it to the server, which will check the secret validity and add points to the user.

### Correct

The user can then correct the program:

1. the user send the corrected code
2. the server copies the code in a new temporary directory and starts a docker instance mapping it
3. the docker's entrypoint executes submitted code using several tests that check if the program still works (challs/*/check.py)
4. the docker's entrypoint executes submitted code using several tests that check if the program is no more exploitable (challs/*/exploit.py)
5. the server stops the container and deletes the temporary files
6. the server gives points to the users if the program still works and is no more exploitable
