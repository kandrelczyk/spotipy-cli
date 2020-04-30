import configparser
import sys
import os
from os.path import expanduser


class Config:
    configLocation = expanduser('~/.config/spotipy-cli/spotipy-clirc')
    clientId = ''
    clientSecret = ''

    def __init__(self):
        parser = configparser.ConfigParser()
        parser.read(self.configLocation)
        if len(parser.sections()) == 0:
            parser.add_section('app')
            sys.stdout.write("No configuration found. Follow the instructions at "
                             "https://developer.spotify.com/documentation/general/guides/app-settings/ and provide "
                             "obtained values. Set the redirect URL to http://localhost:9999/callback\n")
            parser['app']['clientId'] = input("Client ID: ")
            parser['app']['clientSecret'] = input("Client Secret: ")
            parser['app']['deviceName'] = input("Name of the device to control: ")
            parser['app']['volume'] = input("Set volume to: ")
            parser.add_section('token')
            parser.add_section('device')
            path = os.path.dirname(self.configLocation)
            os.makedirs(path, exist_ok=True)
            with open(self.configLocation, 'w') as configfile:
                parser.write(configfile)

        try:
            self.refreshToken = parser['token']['refreshToken']
            self.accessToken = parser['token']['accessToken']
            self.deviceId = parser['device']['deviceId']
        except KeyError:
            pass

        try:
            self.clientId = parser['app']['clientId']
            self.clientSecret = parser['app']['clientSecret']
            self.deviceName = parser['app']['deviceName']
            self.volume = parser['app']['volume']
        except KeyError:
            sys.stderr.write('Invalid config file found: {}\n'.format(self.configLocation))
            sys.exit()

    def store_token(self, token_type, token):
        self.__store_config('token', token_type, token)

        if token_type == 'refreshToken':
            self.refreshToken = token
        elif token_type == 'accessToken':
            self.accessToken = token

    def store_device_id(self, device_id):
        if device_id is None:
            return
        self.__store_config('device', 'deviceId', device_id)
        self.deviceId = device_id

    def __store_config(self, section, config, value):
        parser = configparser.ConfigParser()
        parser.read(self.configLocation)
        if not parser.has_section(section):
            parser.add_section(section)
        parser[section][config] = value
        with open(self.configLocation, 'w') as configfile:
            parser.write(configfile)
