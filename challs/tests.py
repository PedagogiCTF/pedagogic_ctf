#!/usr/bin/env python

import json
import requests


def check_exploitation(chall_id, languages):

    for lang in languages:
        data = {
            'language': lang['name']
        }

        response = requests.post(
            'http://127.0.0.1:8080/v1.0/challenge/{}/execute'.format(chall_id),
            data=json.dumps(data)
        )
        if response.status_code not in [200, 403]:
            print('Exploitation failed for {} on {}'.format(
                chall_id,
                lang['name']
            ))


def check_validate(chall_id):

    data = {
        'secret': "fail"
    }
    response = requests.post(
        'http://127.0.0.1:8080/v1.0/challenge/{}/validate'.format(chall_id),
        data=json.dumps(data)
    )
    if response.status_code != 406:
        print('Validate failed for {}'.format(chall_id))


def check_correction(chall_id, languages):

    for lang in languages:
        data = {
            'language': lang['name'],
            'content_script': lang['file_content']
        }
        response = requests.post(
            'http://127.0.0.1:8080/v1.0/challenge/{}/correct'.format(chall_id),
            data=json.dumps(data)
        )
        if response.status_code != 406:
            print('Correction failed for {} on {}'.format(chall_id, lang['name']))


def main():

    response = requests.get('http://127.0.0.1:8080/v1.0/challenge').json()
    challenges_ids = [c['challenge_id'] for c in response]

    for chall_id in challenges_ids:

        languages = requests.get(
            'http://127.0.0.1:8080/v1.0/challenge/{}'.format(chall_id)
        ).json()['languages']

        check_exploitation(chall_id, languages)
        check_validate(chall_id)
        check_correction(chall_id, languages)


if __name__ == "__main__":

    main()
