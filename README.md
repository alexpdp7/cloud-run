# What is `cloud-run`

`cloud-run` is a wrapper around `qemu` that spins up VMs using cloud images (i.e. using `cloud-init`).

`qemu` is multiplatform and supposedly can integrate with KVM (Linux), Hypervisor.framework (macOS), and Hyper-V (Windows).
However, `cloud-run` has only been tested under Debian, and it has some additional dependencies.

`cloud-run` works with `qemu`'s regular user support.
VMs run as regular user processes.
VMs use slirp user networking, that does not require any special setup.
However, slirp user networking only allows accessing VMs by forwarded ports.

# Requirements

* Python 3
* `genisoimage`
* `qemu` working under the user you run `cloud-run` as.
* `qemu-img`

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
$ cloud-run run <distro> <name>
```

* Check `cloud-run run --help` for supported cloud images.
* `cloud-run run` downloads the cloud image on first use.
* `cloud-run run` creates and start the VM, or starts the VM if it had already been created.
* `cloud-run run` remains attached to the VM console.
  Shut down the VM to make `cloud-run run` exit.

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

* https://github.com/Xe/waifud
* https://github.com/karmab/kcli
