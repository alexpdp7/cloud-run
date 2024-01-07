import shlex

from cloud_run import cloud_init as ci  # FIXME, only works with the rename!
from cloud_run import images
from cloud_run import net
from cloud_run import qemu
from cloud_run import state


def run_vm(
    create_with_base_image,
    instance_id,
    mem,
    disk,
    smp,
    local_hostname=None,
    forwards=None,
    qemu_executable=None,
    machine=None,
    cpu=None,
    accel=True,
    extra_qemu_opts=None,
):
    if not local_hostname:
        local_hostname = instance_id
    vm_img_path = images.get_vm_img_path(instance_id)
    if create_with_base_image:
        images.create_vm_img(create_with_base_image, disk, vm_img_path)

    if not forwards:
        forwards = []
    forwards.append(qemu.HostForward(net.get_free_port(), 22))

    kwargs = {
        "mem": mem,
        "vm_img_path": vm_img_path,
        "forwards": forwards,
        "smp": smp,
        "qemu_executable": qemu_executable,
        "machine": machine,
        "cpu": cpu,
        "accel": accel,
        "extra_qemu_opts": shlex.split(extra_qemu_opts) if extra_qemu_opts else None,
    }

    with state.state(instance_id, forwards):
        if create_with_base_image:
            with ci.gen_cloud_init(instance_id, local_hostname) as cloud_init:
                qemu.exec_qemu(cloud_init=cloud_init, **kwargs)
        else:
            qemu.exec_qemu(**kwargs)
