if __name__ == "__main__":
    from .commands import cli
    from .commands import standalone

    rg = cli.group(standalone.standalone)
    rg.add_command(standalone.create)
    cli()
