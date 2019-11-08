import logging

logging.basicConfig(filename="bin.log",
                    level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(message)s")


def log(log_rank, msg):
    log_rank(msg)