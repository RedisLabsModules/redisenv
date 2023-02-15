# This layout exists, specifically to make poetry+extras work
def main():
    from .commands import cli, cluster, replica, sentinel, standalone

    cli.group(standalone.standalone).add_command(standalone.create)

    cli.group(sentinel.sentinel).add_command(sentinel.create)

    cli.group(replica.replica).add_command(replica.create)

    cli.group(cluster.cluster).add_command(cluster.create)

    cli()


if __name__ == "__main__":
    main()
