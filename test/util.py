import os  # noqa: F401
import json  # noqa: F401
import time
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3
from Workspace.WorkspaceClient import Workspace

ws_name = None
ws_id = None


def get_token():
    return os.environ.get('KB_AUTH_TOKEN', None)


def get_ws_name():
    global ws_name
    if ws_name is None:
        _create_new_workspace()
    return ws_name


def get_ws_id():
    global ws_id
    if ws_id is None:
        _create_new_workspace()
    return ws_id


def get_ws_client():
    cfg = get_config()
    ws = Workspace(cfg['workspace-url'])
    return ws


def get_config():
    """
    Reads and returns the configuration file info.
    """
    config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
    cfg = {}
    config = ConfigParser()
    config.read(config_file)
    for nameval in config.items('jgi_mg_assembly'):
        cfg[nameval[0]] = nameval[1]
    return cfg


def tear_down_workspace():
    global ws_name
    if ws_name is not None:
        ws = get_ws_client()
        ws.delete_workspace({'workspace': ws_name})


def _create_new_workspace():
    global ws_name
    global ws_id
    ws = get_ws_client()
    suffix = int(time.time() * 1000)
    new_ws_name = "test_jgi_mg_assembly_" + str(suffix)
    ret = ws.create_workspace({'workspace': new_ws_name})
    ws_id = ret[0]
    ws_name = ret[1]
