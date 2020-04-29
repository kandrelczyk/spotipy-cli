import click
from . import config
from . import webApi


@click.group()
@click.pass_context
def cli(ctx):
    """CLI client for Spotify using Web API"""
    cfg = config.Config()
    api = webApi.WebApi(cfg)
    ctx.obj = {
        'api': api
    }


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

if __name__ == "__main__":
    cli(obj={})
