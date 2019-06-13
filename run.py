import click
from loguru import logger
from pathlib import Path
import pandas as pd
# noinspection PyProtectedMember
from loguru._defaults import LOGURU_FORMAT


def load_docker(docker_tar_path: Path):
    pass


def simulate(image_path):
    pass


def evaluate(results):
    pass


@click.command("IOPS-Challenge-2019-Final")
@click.option('--team', required=True, help='team name without any special characters')
@click.option("--ground-truth", help='path to ground truth file', default='/srv/iops_final/ground_truth.csv', type=Path)
@click.option("--data", help='KPI data path', default='/srv/iops_final/data', type=Path)
@click.option("--docker", help='docker images parent path', default='/srv', type=Path)
@click.option(
    "--log", help="log file parent path", default='/var/log/',
    type=Path
)
@click.option("")
def main(**config):
    logger.add(
        config['log']/f"iops_final.{config['team']}.log", level='INFO',
        format=f"[{config['team_name']}] " + LOGURU_FORMAT,
        rotation="1 GB", compression="zip"
    )
    logger.info(f"config:\n{config}")
    ground_truth = pd.read_csv(config['ground_truth'])
    image_path = load_docker(config['docker'] / f"{config['team']}.tar")
    results = simulate(image_path, config['data'], ground_truth)
    f1_score = evaluate(results, ground_truth)


if __name__ == '__main__':
    main()
