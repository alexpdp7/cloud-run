import shutil
import subprocess

from cloud_run import directories
from cloud_run import cloud_images


def get_vm_img_path(instance_id):
    return directories.get_data_dir() / f"{instance_id}.qcow2"


def create_vm_img(os, size, instance_id):
    vm_img_path = get_vm_img_path(instance_id)
    if vm_img_path.exists():
        return vm_img_path, False
    shutil.copy(cloud_images.get_cloud_image(os), vm_img_path)
    subprocess.run(["qemu-img", "resize", vm_img_path, size], check=True)
    return vm_img_path, True