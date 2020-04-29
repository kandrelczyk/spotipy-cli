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
            parser['app'] = {}
            sys.stdout.write("No configuration found. Follow the instructions at "
                             "https://developer.spotify.com/documentation/general/guides/app-settings/ and provide "
                             "obtained values.\n")
            parser['app']['clientId'] = input("Client ID: ")
            parser['app']['clientSecret'] = input("Client Secret: ")
            parser['app']['deviceName'] = input("Name of the device to controll: ")
            parser['app']['volume'] = input("Set volume to: ")
            parser['token'] = {}
            path = os.path.dirname(self.configLocation)
            os.makedirs(path, exist_ok=True)
            with open(self.configLocation, 'w') as configfile:
                parser.write(configfile)
        else:
            try:
                self.refreshToken = parser['token']['refreshToken']
                self.accessToken = parser['token']['accessToken']
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
        parser = configparser.ConfigParser()
        parser.read(self.configLocation)
        parser['token'][token_type] = token
        with open(self.configLocation, 'w') as configfile:
            parser.write(configfile)
