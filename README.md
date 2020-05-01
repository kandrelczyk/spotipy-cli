# spotipy-cli

CLI for Spotify written in Python. It uses Spotify Web API to control Spotify Connect
devices. This can be used to control headless players like Raspberry Pi running [raspotify](https://github.com/dtcooper/raspotify). 

## Instalation

```commandline
pip3 install spotipy-cli
```
At least python3.6 is required.

## Setup

To use Web API you will have to create a Spotify App in you account. Follow the instructions 
provided here: https://developer.spotify.com/documentation/general/guides/app-settings/
Set the redirect URL to  http://localhost:9999/callback When done you will have a Client ID and
Client Secret. When you will run the app for the first time it will ask you for this information.
You will also have to provide the name of the device you will control using **spotipy-cli**. 
 
## Authentication

When run for the first time **spotipy-cli** will try to authenticate automatically. To get
the access token you will have to log in into your Spotify account. This requires opening 
a browser which can be tricky on a headless player. You can use ```ssh -X``` or do this locally and then copy the configuration file
created in *~/.conf/spotipy-cli/*

## Usage 

Run
```commandline
spotipy-cli --help
```
to get the list of available commands. This tool was designed to be controlled with a
remote so only basic commands are supported. 

## Troubleshooting

In case of any problems try removing the configuration file and initializing again. 