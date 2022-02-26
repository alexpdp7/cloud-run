from cloud_run import cloud_init as ci  # FIXME, only works with the rename!
from cloud_run import images
from cloud_run import net
from cloud_run import qemu
from cloud_run import state


def run_vm(os, instance_id, mem, disk, smp, local_hostname=None, forwards=None):
    if not local_hostname:
        local_hostname = instance_id
    image, newly_created = images.create_vm_img(os, disk, instance_id)

    if not forwards:
        forwards = []
    forwards.append(qemu.HostForward(net.get_free_port(), 22))

    with state.state(instance_id, forwards):
        if newly_created:
            with ci.gen_cloud_init(instance_id, local_hostname) as cloud_init:
                qemu.exec_qemu(mem, image, forwards, smp, cloud_init)
        else:
            qemu.exec_qemu(mem, image, forwards, smp)
