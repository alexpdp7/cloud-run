import contextlib
import os
import pathlib
import shutil
import subprocess
import tempfile
import urllib.request

import appdirs
import yaml

APPNAME = "cloud_run"
APPAUTHOR = "alexpdp7"


CLOUD_IMAGES = {
    "debian-bullseye": "https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.qcow2",
}


def get_cache_dir():
    cache_dir = pathlib.Path(appdirs.user_cache_dir(APPNAME, APPAUTHOR))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_data_dir():
    data_dir = pathlib.Path(appdirs.user_data_dir(APPNAME, APPAUTHOR))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir




def get_cloud_image_path(os):
    return get_cache_dir() / CLOUD_IMAGES[os].split("/")[-1]


def get_cloud_image(os):
    ofile = get_cloud_image_path(os)
    if ofile.exists():
        return ofile
    url = CLOUD_IMAGES[os]
    with urllib.request.urlopen(url) as d:
        with open(ofile, "wb2") as o:
            o.write(d.read())
    return ofile


def gen_user_data(user, ssh_authorized_keys):
    return {
        "users": [{
            "name": user,
            "ssh_authorized_keys": ssh_authorized_keys,
            "sudo": "ALL=(ALL) NOPASSWD:ALL",
            "groups": "sudo",
            "shell": "/bin/bash",
        }],
    }


def gen_self_user_data():
    with open(os.environ["HOME"] + "/.ssh/id_rsa.pub") as pubkeyf:
        pubkey = pubkeyf.read()
    return gen_user_data(os.environ["USER"], pubkey)


def get_self_user_data_path():
    cache_dir = get_cache_dir()
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
            subprocess.run(["genisoimage", "-output", iso_path, "-V", "cidata", "-r", "-J", "-graft-points", f"user-data={user_data_path}", f"meta-data={meta_data_path}"], check=True)
            yield iso_path
        finally:
            iso_path.unlink()
    finally:
        meta_data_path.unlink()


def create_vm_img(os, size, name):
    vm_img_path = get_data_dir() / f"{name}.qcow2"
    if vm_img_path.exists():
        return vm_img_path, False
    shutil.copy(get_cloud_image(os), vm_img_path)
    subprocess.run(["qemu-img", "resize", vm_img_path, size], check=True)
    return vm_img_path, True


def run_vm(os, instance_id, local_hostname, mem, disk):
    image, newly_created = create_vm_img(os, disk, instance_id)

    qemu_command = [
        "qemu-system-x86_64",
        "-accel", "kvm",
        "-m", mem,
        "-nographic",
        "-device", "virtio-net-pci,netdev=net0", "-netdev", "user,id=net0,hostfwd=tcp::2222-:22",
        "-drive", f"if=virtio,format=qcow2,file={image}",
    ]

    if newly_created:
        with gen_cloud_init(instance_id, local_hostname) as cloud_init:
            subprocess.run(qemu_command + ["-drive", f"if=virtio,format=raw,file={cloud_init}"], check=True)
    else:
        subprocess.run(qemu_command, check=True)
