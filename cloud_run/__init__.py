import shutil
import subprocess

from cloud_run import directories
from cloud_run import cloud_images
from cloud_run import cloud_init
from cloud_run import images


def run_vm(os, instance_id, local_hostname, mem, disk):
    image, newly_created = images.create_vm_img(os, disk, instance_id)

    qemu_command = [
        "qemu-system-x86_64",
        "-accel", "kvm",
        "-m", mem,
        "-nographic",
        "-device", "virtio-net-pci,netdev=net0", "-netdev", "user,id=net0,hostfwd=tcp::2222-:22",
        "-drive", f"if=virtio,format=qcow2,file={image}",
    ]

    if newly_created:
        with cloud_init.gen_cloud_init(instance_id, local_hostname) as cloud_init:
            subprocess.run(qemu_command + ["-drive", f"if=virtio,format=raw,file={cloud_init}"], check=True)
    else:
        subprocess.run(qemu_command, check=True)


def rm_vm(instance_id):
    images.get_vm_img_path(instance_id).unlink()
