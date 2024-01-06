import dataclasses
import logging
import shutil
import subprocess


logger = logging.getLogger(__name__)


PLATFORM_ACCELERATORS = {
    "darwin": "hvf",
    "linux": "kvm",
}


QEMU_EXECUTABLES = [
    "qemu-system-aarch64",  # Debian
    "/usr/libexec/qemu-kvm",  # EL9
]


@dataclasses.dataclass
class HostForward:
    host_port: int
    vm_port: int

    def __str__(self):
        return f"hostfwd=tcp::{self.host_port}-:{self.vm_port}"


def parse_host_forward(s):
    host_port, vm_port = s.split(":")
    return HostForward(host_port, vm_port)


def get_qemu_executable():
    for exe in QEMU_EXECUTABLES:
        if shutil.which(exe):
            return exe
    assert False, f"no qemu found among {QEMU_EXECUTABLES}"


def exec_qemu(mem, image, forwards, smp, cloud_init=None):
    forward_str = ",".join(map(str, forwards))

    qemu_command = [
        get_qemu_executable(),
        "-machine",
        "virt",
        "-cpu",
        "cortex-a53",
        "-smp",
        smp,
        "-m",
        mem,
        "-nographic",
        "-device",
        "virtio-net-pci,netdev=net0",
        "-netdev",
        f"user,id=net0,{forward_str}",
        "-drive",
        f"if=virtio,format=qcow2,file={image}",
        "-bios",
        "/usr/share/edk2/aarch64/QEMU_EFI.fd",
    ]

    logging.info("%s", qemu_command)

    if cloud_init:
        subprocess.run(
            qemu_command + ["-cdrom", cloud_init],
            check=True,
        )
    else:
        subprocess.run(qemu_command, check=True)
