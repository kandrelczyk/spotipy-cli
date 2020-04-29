import requests
import sys
import base64
import json


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

        self.params = {
            'device_id': self.__get_device(),
            'volume_percent': config.volume
        }

    def play(self):
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
        isPlaying = res['is_playing']
        if not isPlaying:
            return
        playlistUir = res['context']['uri']
        if not 'playlist' in playlistUir:
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
        devices = res['devices']
        for device in devices:
            if device['name'] == self.config.deviceName:
                return device['id']
        if not self.deviceId:
            sys.exit('Device {} not found'.format(self.config.deviceName))

    def __refresh_token(self):
        base64token = base64.b64encode(bytes('{}:{}'.format(self.config.clientId, self.config.clientSecret), 'utf-8'))
        headers = {
            'Authorization': 'Basic {}'.format(str(base64token, 'utf-8')),
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.config.refreshToken
        }
        res = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
        if res.ok:
            self.config.store_token('accessToken', res.json()['access_token'])
            self.headers['Authorization'] = 'Bearer {}'.format(res.json()['access_token'])
        else:
            self.__get_refresh_token()

    def __get_refresh_token(self):
        print("Get new refresh token")

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
            if retry:
                if hasattr(self.config, 'refreshToken'):
                    self.__refresh_token()
                else:
                    self.__get_refresh_token()
                self.__request(method, uri, params=params, data=data, retry=False)
            else:
                sys.stderr.write('ERROR: {} {}\n'.format(res.status_code, res.json()))
                sys.exit("Communication with API failed")
