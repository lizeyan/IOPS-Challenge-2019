import os
import re
import signal
import sys
import time
import click
from loguru import logger
from pathlib import Path
import pandas as pd
import numpy as np
from subprocess import check_call, Popen, PIPE
# noinspection PyProtectedMember
from loguru._defaults import LOGURU_FORMAT
from tempfile import TemporaryDirectory
from evaluation_d4 import root_evaluation
from concurrent.futures import ThreadPoolExecutor
import select


def load_docker(docker_tar_path: Path):
    logger.info(f"load docker image from {docker_tar_path}")
    check_call(f"sudo docker load -i {docker_tar_path.resolve()}", shell=True)


def simulate(ground_truth: pd.DataFrame, config: dict):
    image_name = config['team']
    data_path = config['data']
    logger.info(f"using image: {image_name}, data: {data_path}")
    anomaly_timestamps = ground_truth.timestamp.values
    all_timestamps = np.asarray([int(str(_.name).rstrip('.csv')) for _ in data_path.glob("*.csv")])
    assert np.all(np.isin(anomaly_timestamps, all_timestamps)), "data do not contain all anomalies"
    with TemporaryDirectory() as temp_data:
        client = Popen(
            f"sudo docker run -i --rm --cpus={config['cpu_limit']} "
            f"--memory={config['memory_limit']} "
            f"-v {temp_data}:/data --ipc=private {image_name}",
            shell=True, stdin=PIPE, stdout=PIPE, universal_newlines=True, bufsize=0,
            preexec_fn=os.setsid
        )
        send_time = {}
        results = []

        def sender():
            last_time = float('-inf')
            for anomaly_time in sorted(anomaly_timestamps):
                logger.info(f"send {anomaly_time}")
                list(map(
                    lambda x: os.symlink(str(data_path / f"{x}.csv"), f"{temp_data}/{x}.csv"),
                    all_timestamps[(all_timestamps <= anomaly_time) & (all_timestamps > last_time)]
                ))
                send_time[int(anomaly_time)] = time.time()
                print(anomaly_time, file=client.stdin, flush=True)
                time.sleep(config['interval'])
                last_time = anomaly_time
                if client.poll() is not None:
                    break
            os.killpg(os.getpgid(client.pid), signal.SIGTERM)
            logger.info("sender finished")

        def receiver():
            ret_re = re.compile(r'\s*(?P<timestamp>\d+)\s*,\s*(?P<rc_set>[iecpl\d&;]+)\s*')
            y = select.poll()
            y.register(client.stdout, select.POLLIN)
            while client.poll() is None:
                if y.poll(1):
                    line = client.stdout.readline()
                else:
                    continue
                match = ret_re.match(line)
                if not match:
                    logger.info(f"unrecognized line: {line}")
                    continue
                timestamp, rc_set = match.group("timestamp"), match.group('rc_set')
                timestamp = int(timestamp)
                interval = time.time() - send_time[timestamp]
                logger.info(f"receive: {timestamp},{rc_set}, interval: {interval:.3f}s")
                if timestamp in send_time and interval <= config['interval']:
                    results.append({
                        'timestamp': timestamp,
                        'set': rc_set
                    })

        with ThreadPoolExecutor(max_workers=5) as pool:
            pool.submit(sender)
            receiver()

        result_df = pd.DataFrame.from_records(results, columns=['timestamp', 'set'])
        logger.debug(f"\n{result_df}")
        return result_df


def evaluate(ground_truth: pd.DataFrame, results: pd.DataFrame) -> float:
    ret = root_evaluation(truth_df=ground_truth, result_df=results)
    return ret['data']


@click.command("IOPS-Challenge-2019-Final")
@click.option('--team', required=True, help='team name without any special characters')
@click.option("--ground-truth", help='path to ground truth file', default='/srv/iops_final/ground_truth.csv', type=Path)
@click.option("--data", help='KPI data path', default='/srv/iops_final/data', type=Path)
@click.option("--docker", help='docker images parent path', default='/srv', type=Path)
@click.option("--cpu-limit", help='client docker cpu limit', default=8)
@click.option("--memory-limit", help='client docker memory limit', default="64G")
@click.option("--storage-limit", help='client docker storage limit', default="200G")
@click.option("--interval", help='interval between every two points in seconds', default=60)
@click.option(
    "--log", help="log file parent path", default='/var/log/',
    type=Path
)
def main(**config):
    logger.remove()
    logger.add(
        sys.stderr, level='DEBUG',
        format=f"[{config['team']}] " + LOGURU_FORMAT,
        backtrace=True, catch=True
    )
    logger.add(
        config['log'] / f"iops_final.{config['team']}.log", level='INFO',
        format=f"[{config['team']}] " + LOGURU_FORMAT,
        rotation="1 GB", compression="zip", backtrace=True, catch=True
    )
    logger.info(f"config:\n{config}")
    ground_truth = pd.read_csv(config['ground_truth'])
    load_docker(config['docker'] / f"{config['team']}.tar")
    results = simulate(ground_truth, config)
    f1_score = evaluate(ground_truth, results)
    logger.info(f"Final F1-score: {f1_score}")
    raise SystemExit


if __name__ == '__main__':
    main()
