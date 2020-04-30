import requests
import sys
import base64
import json

from .auth import spotipyAuth


class WebApi:
    apiUrl = 'https://api.spotify.com/v1/me/{}'

    def __init__(self, config):
        self.config = config
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if hasattr(config, 'accessToken'):
            self.headers['Authorization'] = 'Bearer {}'.format(config.accessToken)
        else:
            self.__refresh_token()

        if not hasattr(config, 'deviceId'):
            deviceId = self.__get_device()
            config.store_device_id(deviceId)

        if hasattr(config, 'deviceId'):
            self.params = {
                'device_id': config.deviceId,
                'volume_percent': config.volume
            }
            self.initialised = True
        else:
            self.initialised = False

    def play(self):
        data = {'device_ids': [self.params['device_id']]}
        self.__request('PUT', self.apiUrl.format('player'), data=json.dumps(data))
        res = self.__request('GET', self.apiUrl.format('player'))
        isPlaying = res['is_playing']
        action = 'player/pause' if isPlaying else 'player/play'
        self.__request('PUT', self.apiUrl.format('player/volume'), self.params)
        self.__request('PUT', self.apiUrl.format(action), self.params)

    def next(self):
        self.__request('POST', self.apiUrl.format('player/next'), self.params)

    def prev(self):
        self.__request('POST', self.apiUrl.format('player/previous'), self.params)

    def next_list(self):
        self.__switch_playlist(1)

    def prev_list(self):
        self.__switch_playlist(-1)

    def shuffle(self):
        res = self.__request('GET', self.apiUrl.format('player'))
        params = dict(self.params)
        params['state'] = not res['shuffle_state']
        self.__request('PUT', self.apiUrl.format('player/shuffle'), params)

    def __switch_playlist(self, offset):
        res = self.__request('GET', self.apiUrl.format('player'))
        if res is None or not res['is_playing']:
            return
        playlistUir = res['context']['uri']
        if 'playlist' not in playlistUir:
            return
        playlistId = playlistUir.split(':')[-1]
        res = self.__request('GET', self.apiUrl.format('playlists?limit=50'))
        items = res['items']
        index = 0
        while not items[index]['id'] == playlistId:
            index += 1

        index += offset
        if index == len(items):
            index = 0
        elif index < 0:
            index = len(items) - 1

        newList = items[index]['uri']
        data = {"context_uri": newList}
        self.__request('PUT', self.apiUrl.format('player/play'), data=json.dumps(data))

    def __get_device(self):
        res = self.__request('GET', self.apiUrl.format('player/devices'))
        if res:
            devices = res['devices']
            for device in devices:
                if device['name'] == self.config.deviceName:
                    return device['id']
        sys.stderr.write('Device {} not found\n'.format(self.config.deviceName))
        return None

    def __refresh_token(self):
        sys.stdout.write('refreshing access token...\n')
        base64token = base64.b64encode(bytes('{}:{}'.format(self.config.clientId, self.config.clientSecret), 'utf-8'))
        headers = {
            'Authorization': 'Basic {}'.format(str(base64token, 'utf-8')),
        }
        if hasattr(self.config, 'refreshToken'):
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.config.refreshToken
            }
            res = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
            if res.ok:
                self.config.store_token('accessToken', res.json()['access_token'])
            else:
                self.__get_refresh_token(headers)
        else:
            self.__get_refresh_token(headers)
        self.headers['Authorization'] = 'Bearer {}'.format(self.config.accessToken)

    def __get_refresh_token(self, headers):
        sys.stdout.write("invalid refresh token, requesting new one...\n")
        auth = spotipyAuth.SpotipyAuth(self.config)
        sys.stdout.write("got authorization code, requesting new token...\n")
        authCode = auth.get_auth_code()
        data = {
            'grant_type': 'authorization_code',
            'code': authCode,
            'redirect_uri': 'http://localhost:{}/{}'.format(auth.port, auth.path)
        }
        res = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
        if res.ok:
            self.config.store_token('accessToken', res.json()['access_token'])
            self.config.store_token('refreshToken', res.json()['refresh_token'])
            sys.stdout.write("got new token...\n")
        else:
            sys.stderr.write('failed to get token')

    def __request(self, method, uri, params={}, data={}, retry=True):
        res = None
        if method == 'GET':
            res = requests.get(uri, headers=self.headers, params=params, data=data)
        elif method == 'PUT':
            res = requests.put(uri, headers=self.headers, params=params, data=data)
        elif method == 'POST':
            res = requests.post(uri, headers=self.headers, params=params, data=data)
        if res.ok:
            if res.status_code == 200:
                return res.json()
            else:
                return None
        else:
            print('uri: {} sc: {} json: {}'.format(uri, res.status_code, data))
            if retry:
                if hasattr(self.config, 'refreshToken'):
                    self.__refresh_token()
                else:
                    self.__get_refresh_token()
                return self.__request(method, uri, params=params, data=data, retry=False)
            else:
                sys.stderr.write('Error: communication with API failed\n')
                return None
