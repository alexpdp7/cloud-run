import dataclasses
import logging
import pathlib
import shutil
import subprocess
import sys


logger = logging.getLogger(__name__)


PLATFORM_ACCELERATORS = {
    "darwin": "hvf",
    "linux": "kvm",
}


QEMU_EXECUTABLES = [
    "qemu-system-x86_64",  # Debian, macOS
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


def get_qemu_executable(qemu_executable=None):
    if qemu_executable:
        return qemu_executable
    for exe in QEMU_EXECUTABLES:
        if shutil.which(exe):
            return exe
    assert False, f"no qemu found among {QEMU_EXECUTABLES}"


def exec_qemu(
    mem,
    vm_img_path: pathlib.Path,
    forwards,
    smp,
    cloud_init=None,
    machine=None,
    cpu="max",
    extra_qemu_opts=None,
    accel=True,
    qemu_executable=None,
):
    forward_str = ",".join(map(str, forwards))

    qemu_command = [
        get_qemu_executable(qemu_executable),
        "-cpu",
        cpu,
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
        f"if=virtio,format=qcow2,file={vm_img_path}",
    ]

    if accel:
        qemu_command += ["-accel", PLATFORM_ACCELERATORS[sys.platform]]

    if extra_qemu_opts:
        qemu_command += extra_qemu_opts

    if machine:
        qemu_command += ["-machine", machine]

    if cloud_init:
        qemu_command += ["-cdrom", cloud_init]

    logging.info("%s", qemu_command)

    subprocess.run(qemu_command, check=True)
