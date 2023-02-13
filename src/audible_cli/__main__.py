"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Audible Cli Hypermodern Test."""


if __name__ == "__main__":
    main(prog_name="audible-cli-hypermodern-test")  # pragma: no cover
