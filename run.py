#!/usr/bin/env python
import yaml
import logging
import datetime
import os
from pprint import pformat

from checkers.replication import ReplicationChecker
from notifiers.slack import SlackNotifier

if __name__ == '__main__':
    directory = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config = yaml.load(
        (open(os.path.join(directory, 'config.yml'), 'r').read()))

    loglevel = getattr(logging,
        config.get('loglevel','debug').upper())
    logfile = config.get('logfile','replication.log')
    if logfile.lower() == 'stderr':
      lh = logging.StreamHandler()
    else:
      lh = logging.FileHandler(os.path.join(directory, logfile))

    logging.getLogger().setLevel(loglevel)
    logging.getLogger().addHandler(lh)

    logging.info('Logging to %s with %s level.' %
        (logfile, logging.getLevelName(loglevel)))
    logging.info('Checker started at: ' + datetime.datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S'))

    notifier = SlackNotifier(webhook_url=config['webhook_url'])
    checker = ReplicationChecker(
        project_directory=directory,
        lag_interval=config['mysql'].get('lag_interval', 300),
        lag_duration=config['mysql'].get('lag_duration', 1800),
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        host=config['mysql'].get('host', 'localhost'),
        port=config['mysql'].get('port', 3306)
    )
    checker.add_notifier(notifier)

    checker_vars = dict(vars(checker))
    del checker_vars['password']
    logging.debug(pformat(checker_vars))

    checker.check()
    logging.info('Checker ended at: ' + datetime.datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S'))
