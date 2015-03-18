
__author__ = ''
import os
from splunk.clilib import cli_common as cli
import json
import logging
import logging.handlers


def setup_logger(level):
    """
    setups logger
    :param level: Logging level
    :return: logger object
    """
    appname = os.path.dirname(os.path.realpath(__file__)).split('/')[-1]
    logger = logging.getLogger(appname)
    logger.propagate = False  # Prevent the log messages from being duplicated in the python.log file
    logger.setLevel(level)
    file_handler = logging.handlers.RotatingFileHandler(os.path.join('{0}.log'.format(appname)), maxBytes=5000000,
                                                        backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    consolehandler = logging.StreamHandler()
    consolehandler.setFormatter(formatter)
    logger.addHandler(consolehandler)
    return logger


def getstanza(conf, stanza):
    """
    Returns dict object of config file settings
    :param conf: Splunk conf file name
    :param stanza: stanza (entry) from conf file
    :return: returns dictionary of setting
    """
    appdir = os.path.dirname(os.path.dirname(__file__))
    conf = "%s.conf" % conf
    apikeyconfpath = os.path.join(appdir, "default", conf)
    apikeyconf = cli.readConfFile(apikeyconfpath)
    localconfpath = os.path.join(appdir, "local", conf)
    if os.path.exists(localconfpath):
        localconf = cli.readConfFile(localconfpath)
        for name, content in localconf.items():
            if name in apikeyconf:
                apikeyconf[name].update(content)
            else:
                apikeyconf[name] = content
    return apikeyconf[stanza]


def setproxy(local_conf, global_conf):
    """
    Sets up dict object for proxy settings
    :param local_conf:
    :param global_conf:
    :return:
    """
    proxy = None
    proxy_url = global_conf['proxy_url'] if 'proxy_url' in global_conf else None
    proxy_url = local_conf['proxy_url'] if 'proxy_url' in local_conf else proxy_url
    if proxy_url:
        proxy = dict()
        proxy_user = global_conf['proxy_user'] if 'proxy_user' in global_conf else None
        proxy_user = local_conf['proxy_user'] if 'proxy_user' in local_conf else proxy_user
        proxy_password = global_conf['proxy_password'] if 'proxy_password' in global_conf else None
        proxy_password = local_conf['proxy_password'] if 'proxy_password' in local_conf else proxy_password
        if proxy_password and proxy_user:
            proxy_url = '%s:%s@%s' % (proxy_user, proxy_password, proxy_url)
        elif proxy_user and not proxy_password:
            proxy_url = '%s@%s' % (proxy_user, proxy_url)
        elif not proxy_user and not proxy_password and proxy_url:
            proxy_url = '%s' % proxy_url
        else:
            proxy = None
        if proxy:
            proxy['https'] = 'https://%s' % proxy_url
            proxy['http'] = 'http://%s' % proxy_url
    return proxy


def tojson(jmessage):
    """
    Returns a pretty print json string
    :param jmessage: dict object
    :return: str
    """
    jmessage = json.dumps(json.loads(json.JSONEncoder().encode(jmessage)),
                          indent=4,
                          sort_keys=True,
                          ensure_ascii=True)
    return jmessage

