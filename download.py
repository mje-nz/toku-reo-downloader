import itertools
from pathlib import Path

import click
from tqdm import tqdm

import toku_reo


@click.command()
@click.argument("dest")
def main(dest):
    dest = Path(dest)
    (dest / "tvshow.nfo").write_text(toku_reo.generate_tvshow_nfo())

    seasons = toku_reo.get_seasons()
    episodes = list(itertools.chain.from_iterable(s.episodes for s in seasons))
    for episode in tqdm(episodes, "Downloading", unit="ep"):
        episode.download(dest / f"Season {episode.season_number}")


if __name__ == "__main__":
    main()
