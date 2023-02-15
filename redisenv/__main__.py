# This layout exists, specifically to make poetry+extras work
def main():
    from .commands import cli, cluster, replica, sentinel, standalone, enterprise

    cli.group(standalone.standalone).add_command(standalone.create)

    cli.group(sentinel.sentinel).add_command(sentinel.create)

    cli.group(replica.replica).add_command(replica.create)

    cli.group(cluster.cluster).add_command(cluster.create)

    cli.group(enterprise.enterprise).add_command(enterprise.create)

    cli()


if __name__ == "__main__":
    main()
