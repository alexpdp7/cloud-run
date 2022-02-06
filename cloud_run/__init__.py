from cloud_run import cloud_init as ci  # FIXME, only works with the rename!
from cloud_run import images
from cloud_run import qemu
from cloud_run import state


def run_vm(os, instance_id, mem, disk, local_hostname=None):
    if not local_hostname:
        local_hostname = instance_id
    image, newly_created = images.create_vm_img(os, disk, instance_id)

    forwards = [qemu.HostForward(2222, 22)]

    with state.state(instance_id, forwards):
        if newly_created:
            with ci.gen_cloud_init(instance_id, local_hostname) as cloud_init:
                qemu.exec_qemu(mem, image, forwards, cloud_init)
        else:
            qemu.exec_qemu(mem, image, forwards)
