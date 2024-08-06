# Archival

I have found [Incus](https://linuxcontainers.org/incus/), which I think can address all the needs that `cloud-init` was supposed to cover (and more).
Therefore, I am archiving this repository.

# What is `cloud-run`

`cloud-run` is a wrapper around `qemu` that spins up VMs using cloud images (i.e. using `cloud-init`).

`qemu` is multiplatform and supposedly can integrate with KVM (Linux), Hypervisor.framework (macOS), and Hyper-V (Windows).
I develop `cloud-run` primarily on EL9 and an Arch Linux container, and I have tested it minimally on macOS and Debian.

`cloud-run` works with `qemu`'s regular user support.
VMs run as regular user processes.
VMs use slirp user networking, that does not require any special setup.
However, slirp user networking only allows accessing VMs by forwarded ports.

`cloud-run` is meant to be a simple local workstation tool for quickly running VMs.
For example, `cloud-run ansible-inventory` makes it easy to spin local VMs and run playbooks on them.

# Requirements

* Python 3
* `mkisofs`
* `qemu` working under the user you run `cloud-run` as.
* `qemu-img`

On macOS, run:

```
$ brew install cdrtools qemu
```

On Debian:

```
$ apt install genisoimage qemu-system-x86
```

On EL9:

```
$ dnf install xorriso qemu-kvm-core
```

# Installation

`cloud-run` is a Python module that exposes some scripts.
We recommend the use of [pipx](https://pypa.github.io/pipx/).

With `pipx` installed, run:

```
$ pipx install git+https://github.com/alexpdp7/cloud-run.git
```

# Usage

## Run a VM

Start a VM named `name` using `distro`:

```
$ cloud-run run --create-with-base-image <distro> <name>
```

* Check `cloud-run run --help` for supported cloud images.
* With `--create-with-base-image`, `cloud-run run` downloads the cloud image on first use and creates the VM.
* `cloud-run run` starts the VM.
* `cloud-run run` remains attached to the VM console.
  Shut down the VM to make `cloud-run run` exit.

### Emulating other CPUs

(This example has been tested only on Arch Linux.)

```
$ cloud-run run --create-with-base-image https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-generic-arm64.qcow2 --qemu-executable qemu-system-aarch64 --machine virt --cpu cortex-a53 --no-accel --extra-qemu-opts "-bios /usr/share/edk2/aarch64/QEMU_EFI.fd" debian-bullseye-arm64
```

See https://github.com/alexpdp7/raspberry-pi-headless-provision for a procedure to use this to provision a Raspberry Pi completely headlessly.

## Connect to a VM

Connect to a VM named `name`:

```
$ ssh $(cloud-run ssh <name>)
```

## Provide an Ansible dynamic inventory

Create an executable file containing:

```
#!/bin/sh

cloud-run ansible-inventory "$@"
```

Configure Ansible to use that file as inventory.
The inventory contains *running* VMs.

## Manage VMs

```
$ cloud-run ls-vms
$ cloud-run rm-vm <name>
```

# Similar tools

`cloud-run` is pretty opinionated, and probably not according to everyone's tastes.

Incus is much more.
I am switching to Incus and archiving `cloud-run` for now.

`kcli` is infinitely more featured.
I only started `cloud-run` because `kcli` does not do user mode VMs.
However, if you don't need that, `kcli` does much more stuff.

I think I had read about `waifud` before starting work on `cloud-run`, but I didn't realize the similarities until later.
`waifud` has also more features.

* https://github.com/Xe/waifud
* https://github.com/karmab/kcli
* https://linuxcontainers.org/incus/
