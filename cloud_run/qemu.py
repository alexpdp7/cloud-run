import dataclasses
import subprocess


@dataclasses.dataclass
class HostForward:
    host_port: int
    vm_port: int

    def __str__(self):
        return f"hostfwd=tcp::{self.host_port}-:{self.vm_port}"


def exec_qemu(mem, image, forwards, cloud_init=None):
    forward_str = ",".join(map(str, forwards))

    qemu_command = [
        "qemu-system-x86_64",
        "-accel",
        "kvm",
        "-m",
        mem,
        "-nographic",
        "-device",
        "virtio-net-pci,netdev=net0",
        "-netdev",
        f"user,id=net0,{forward_str}",
        "-drive",
        f"if=virtio,format=qcow2,file={image}",
    ]

    if cloud_init:
        subprocess.run(
            qemu_command + ["-drive", f"if=virtio,format=raw,file={cloud_init}"],
            check=True,
        )
    else:
        subprocess.run(qemu_command, check=True)
