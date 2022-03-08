import contextlib
import os
import pathlib
import subprocess
import tempfile

import yaml

from cloud_run import directories


def gen_user_data(user, ssh_authorized_keys):
    return {
        "users": [
            {
                "name": user,
                "ssh_authorized_keys": ssh_authorized_keys,
                "sudo": "ALL=(ALL) NOPASSWD:ALL",
                "groups": "sudo",
                "shell": "/bin/bash",
            }
        ],
    }


def gen_self_user_data():
    with open(os.environ["HOME"] + "/.ssh/id_rsa.pub") as pubkeyf:
        pubkey = pubkeyf.read()
    return gen_user_data(os.environ["USER"], pubkey)


def get_self_user_data_path():
    cache_dir = directories.get_cache_dir()
    user_data_path = cache_dir / "user-data"
    with open(user_data_path, "w") as f:
        f.write("#cloud-config\n")
        f.write(yaml.dump(gen_self_user_data()))
    return user_data_path


def gen_meta_data(instance_id, local_hostname):
    return {
        "instance-id": instance_id,
        "local-hostname": local_hostname,
    }


def write_meta_data(f, instance_id, local_hostname):
    f.write(yaml.dump(gen_meta_data(instance_id, local_hostname)))


@contextlib.contextmanager
def gen_cloud_init(instance_id, local_hostname):
    user_data_path = get_self_user_data_path()
    _, meta_data_path = tempfile.mkstemp()
    meta_data_path = pathlib.Path(meta_data_path)
    try:
        with open(meta_data_path, "w") as meta_dataf:
            write_meta_data(meta_dataf, instance_id, local_hostname)
        _, iso_path = tempfile.mkstemp()
        try:
            iso_path = pathlib.Path(iso_path)
            subprocess.run(
                [
                    "mkisofs",
                    "-output",
                    iso_path,
                    "-V",
                    "cidata",
                    "-r",
                    "-J",
                    "-graft-points",
                    f"user-data={user_data_path}",
                    f"meta-data={meta_data_path}",
                ],
                check=True,
            )
            yield iso_path
        finally:
            iso_path.unlink()
    finally:
        meta_data_path.unlink()
