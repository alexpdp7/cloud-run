from cloud_run import cloud_init as ci  # FIXME, only works with the rename!
from cloud_run import images
from cloud_run import qemu


def run_vm(os, instance_id, local_hostname, mem, disk):
    image, newly_created = images.create_vm_img(os, disk, instance_id)

    forwards = [qemu.HostForward(2222, 22)]

    if newly_created:
        with ci.gen_cloud_init(instance_id, local_hostname) as cloud_init:
            qemu.exec_qemu(mem, image, forwards, cloud_init)
    else:
        qemu.exec_qemu(mem, image, forwards)


def rm_vm(instance_id):
    images.get_vm_img_path(instance_id).unlink()
