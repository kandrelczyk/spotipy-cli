import click
import sys
import os
import time

from . import config
from . import webApi

pidFileName = '/tmp/spotipy-cli.pid'


@click.group()
@click.pass_context
def cli(ctx):
    """CLI client for Spotify using Web API"""
    cfg = config.Config()
    api = webApi.WebApi(cfg)
    ctx.obj = {
        'api': api
    }
    if not api.initialised:
        sys.exit('Exiting\n')


@cli.command()
@click.pass_context
def play(ctx):
    """Pause or resume playback"""
    ctx.obj['api'].play()


@cli.command()
@click.pass_context
def next(ctx):
    """Next song"""
    ctx.obj['api'].next()


@cli.command()
@click.pass_context
def prev(ctx):
    """Previous song"""
    ctx.obj['api'].prev()


@cli.command()
@click.pass_context
def next_list(ctx):
    """Switch to next playlist"""
    ctx.obj['api'].next_list()


@cli.command()
@click.pass_context
def prev_list(ctx):
    """Switch to previous playlist"""
    ctx.obj['api'].prev_list()


@cli.command()
@click.pass_context
def shuffle(ctx):
    """Toggle shuffle for playback"""
    ctx.obj['api'].shuffle()


def main():
    if os.path.isfile(pidFileName):
        sys.exit('Already running, exiting\n')
    pid = str(os.getpid())

    file = open(pidFileName, 'w').write(pid)
    try:
        cli(obj={})
    finally:
        time.sleep(1)
        os.unlink(pidFileName)


if __name__ == "__main__":
    main()
