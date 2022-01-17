import shutil
import subprocess

from cloud_run import directories
from cloud_run import cloud_images
from cloud_run import cloud_init


def create_vm_img(os, size, name):
    vm_img_path = directories.get_data_dir() / f"{name}.qcow2"
    if vm_img_path.exists():
        return vm_img_path, False
    shutil.copy(cloud_images.get_cloud_image(os), vm_img_path)
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
        with cloud_init.gen_cloud_init(instance_id, local_hostname) as cloud_init:
            subprocess.run(qemu_command + ["-drive", f"if=virtio,format=raw,file={cloud_init}"], check=True)
    else:
        subprocess.run(qemu_command, check=True)
