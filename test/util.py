"""
Contains useful utilities for testing. Fetching configs, building and tearing down workspaces, etc.
Doesn't have any actual tests.
"""
import os  # noqa: F401
import json  # noqa: F401
import time
import shutil
import sys
from contextlib import contextmanager
from StringIO import StringIO
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3
from Workspace.WorkspaceClient import Workspace
from ReadsUtils.ReadsUtilsClient import ReadsUtils

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
    global ws_id
    if ws_name is not None:
        ws = get_ws_client()
        ws.delete_workspace({'workspace': ws_name})
        ws_id = None
        ws_name = None


def _create_new_workspace():
    global ws_name
    global ws_id
    ws = get_ws_client()
    suffix = int(time.time() * 1000)
    new_ws_name = "test_jgi_mg_assembly_" + str(suffix)
    ret = ws.create_workspace({'workspace': new_ws_name})
    ws_id = ret[0]
    ws_name = ret[1]


def file_to_scratch(source_file, overwrite=False):
    """
    Copies a file to the scratch directory. By default, will raise an exception instead of
    overwriting. set overwrite=True to override the overwrite protection.
    """
    scratch_dir = get_config()['scratch']
    scratch_file_path = os.path.join(scratch_dir, os.path.basename(source_file))
    if os.path.exists(scratch_file_path) and not overwrite:
        raise ValueError("File exists already! Running this will overwrite it")
    shutil.copy(source_file, scratch_file_path)
    return scratch_file_path


def load_pe_reads(fwd_file, rev_file):
    """
    Copies from given dir to scratch. Then calls ReadsUtils to upload from scratch.
    """
    callback_url = os.environ['SDK_CALLBACK_URL']
    fwd_file_path = file_to_scratch(fwd_file, overwrite=True)
    rev_file_path = file_to_scratch(rev_file, overwrite=True)
    ru = ReadsUtils(callback_url)
    pe_reads_params = {
        'fwd_file': fwd_file_path,
        'rev_file': rev_file_path,
        'sequencing_tech': 'Illumina',
        'wsname': get_ws_name(),
        'name': 'MyPairedEndLibrary'
    }
    return ru.upload_reads(pe_reads_params)['obj_ref']

@contextmanager
def captured_stdout():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err