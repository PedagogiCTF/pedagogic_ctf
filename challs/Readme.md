# Add  challenges

You can (*and should*) take inspiration from other existing challenges, see for example `challs/injection_conf.dir`

## Create directory structure

Go to the git cloned repo, and create your new challenge:

```bash
    cd ~/pedagogic_ctf/challs
    mkdir ${chall_name}.dir
```

Now let's create the json file that will describe your challenge,
"parameters" is used to pass arguments to you script in a ordered way:

```json
{
  "name": "name of your challenge",
  "points": 100,
  "description": " your challenge description: what the program does",
  "parameters": [
    {
      "name": "name of the input displayed to the user. As this is the first parameter, this will be passed as first argv to your challenge script",
      "placeholder": "simple example display to the user"
    },
    {
      "name": "Email",
      "placeholder": "ex: me@me.com"
    }
  ],
  "languages": [
    {
      "name": "For now only 'GOLANG', 'PERL' or 'PYTHON'",
      "extension": "For now only '.go', '.pl', or '.py'"
    }
  ],
  "resolved_conclusion":"your challenge conclusion note, explaining the vulnerability and how to avoid it"
}
```

Then 3 more files are required for the challenge to be fully operational:

- `init.py` that will init challenges dependencies (db, secrets ...).
It will be launched **once** when you start the project with `argv[1] = the_secret_the_user_need_to_find`.
It will also be launched each time a user submits a correction proposal.
- `check.py` which should return 2 if you challenge is still usable.
It will be launched along with `exploit.py` each time a user submits a correction proposal of the challenge.
The arguments are: 
    * `argv[1] = the_secret`
    * `argv[2] = /path/to/the/user/script`
- `exploit.py` which should return 3 if you challenge is still hackable.
It will be launched along with `check.py` each time a user submits a correction proposal of the challenge.
The arguments are: 
    * `argv[1] = the_secret`
    * `argv[2] = /path/to/the/user/script`

## Tests :

You can tests challenges with (selenium docker need to be started):

`./tests.sh`

and (Go Api need to be started):

`python3 tests.py`
