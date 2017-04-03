import json
import requests

challenges_ids = [c['challenge_id'] for c in requests.get('http://127.0.0.1:8080/v1.0/challenge').json()]

for chall_id in challenges_ids:
    languages = requests.get('http://127.0.0.1:8080/v1.0/challenge/{}'.format(chall_id)).json()['languages']
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
            print('Failed for {} on {}'.format(chall_id, lang['name']))
