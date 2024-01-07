import subprocess

from cloud_run import directories
from cloud_run import cloud_images


def get_imgs_path():
    return directories.get_data_dir()


def get_vm_img_path(instance_id):
    return get_imgs_path() / f"{instance_id}.qcow2"


def create_vm_img(os, size, vm_img_path):
    assert not vm_img_path.exists(), f"{vm_img_path} already exists"

    subprocess.run(
        [
            "qemu-img",
            "convert",
            cloud_images.get_cloud_image(os),
            "-O",
            "qcow2",
            vm_img_path,
        ],
        check=True,
    )
    subprocess.run(["qemu-img", "resize", vm_img_path, size], check=True)


def rm_vm(instance_id):
    get_vm_img_path(instance_id).unlink()


def get_vm_imgs():
    return [p.stem for p in get_imgs_path().glob("*.qcow2")]
