if __name__ == "__main__":
    from .commands import cli
    from .commands import standalone, sentinel, replica

    cli.group(standalone.standalone).add_command(standalone.create)
    
    cli.group(sentinel.sentinel).add_command(sentinel.create)
    
    cli.group(replica.replica).add_command(replica.create)
    
    cli()
