# Add  challenges


## Create directory structure  :

Go to the git cloned repo :

    cd ~/ctf_pedagogique/challs
you can use environment variable to ease directory creation  that must end up with .dir:

    export NEW_CHALL_NAME=php_exec
    mkdir $NEW_CHALL_NAME.dir
Now you must create the json file that will describe your challenge,
"parameters" is used to pass arguments to you script in a ordered way :

```json
{
  "name": "name of your challenge",
  "points": 100,
  "description": " your challenge description ",
  "parameters": [
    {
      "name": "name of the input displayed to the user. As this is the first parameter, this will be passed as first argv to your challenge script",
      "placeholder": "simple example display to the user"
    }
  ],
  "languages": [
    {
      "name": "name the language (example: PYTHON)",
      "extension": "extension of the language (example: .py)"
    }
  ],
  "resolved_conclusion":"your challenge conclusion note."
}
```

Create a init.py script that will init challenges dependencies (db, secrets ...).
Create a check.py script that will return 2 if you challenge is still usable.
Create a exploit.py script that will return 3 if you challenge is still hackable.

Then re-run init.sh.

## Tests :

You can tests challenges with (selenium docker need to be started):

`./test.sh`

and (Go Api need to be started):

`python3 test.py`
