import logging

logging.basicConfig(filename="logs/backup.log",
                    level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(message)s")


def log(obj, log_rank, msg):
    try:
        header = "{}: ".format(obj.name.split('/')[-1])
        log_rank(header + msg)
    except:
        log_rank(msg)