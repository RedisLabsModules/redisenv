from invoke import task


@task
def linters(c):
    """Linters"""
    c.run("black --check --diff redisenv tests")