import argparse
import json
import logging

import cloud_run
from cloud_run import images
from cloud_run import cloud_images
from cloud_run import qemu
from cloud_run import state


def ls_vms_cli():
    print("\n".join(images.get_vm_imgs()))


def get_ssh_forward(forwards):
    ssh_forwards = [f for f in forwards if f.vm_port == 22]
    assert len(ssh_forwards) == 1
    return ssh_forwards[0]


def ssh(instance_id, user=None):
    forwards = state.get_state(instance_id)
    ssh_forward = get_ssh_forward(forwards)
    user_prefix = f"{user}@" if user else ""
    return [
        "-p",
        str(ssh_forward.host_port),
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "StrictHostKeyChecking=no",
        f"{user_prefix}localhost",
    ]


def ssh_cli(instance_id, user=None):
    return " ".join(ssh(instance_id, user))


def _forwards_to_inventory(vm_forwards):
    return {
        "ansible_host": "localhost",
        "ansible_port": get_ssh_forward(vm_forwards).host_port,
    }


def ansible_inventory_cli(list_command, host):
    forwards = {}
    for vm in images.get_vm_imgs():
        vm_forwards = state.get_state_if_exists(vm)
        if vm_forwards:
            forwards[vm] = vm_forwards
    if list_command:
        inventory = {
            "_meta": {
                "hostvars": {
                    vm: _forwards_to_inventory(vm_forwards)
                    for vm, vm_forwards in forwards.items()
                },
            },
            "all": {
                "children": ["ungrouped"],
            },
            "ungrouped": {
                "hosts": list(forwards.keys()),
            },
        }
    else:
        inventory = _forwards_to_inventory(forwards[vm])
    print(json.dumps(inventory))


def parser():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers()

    run = sp.add_parser("run")
    available_images = " ".join(cloud_images.AVAILABLE_CLOUD_IMAGES)
    run.add_argument(
        "--create-with-base-image", help=f"Either an URL or one of {available_images}"
    )
    run.add_argument("instance_id")
    run.add_argument("--local-hostname")
    run.add_argument("--mem", default="1G", help="default %(default)s")
    run.add_argument(
        "--smp",
        default="cpus=1",
        help="default %(default)s, see qemu -smp",
    )
    run.add_argument("--disk", default="11G", help="default %(default)s")
    run.add_argument(
        "--forward",
        action="append",
        type=qemu.parse_host_forward,
        dest="forwards",
        metavar="HOST_PORT:VM_PORT",
    )
    run.add_argument("--qemu-executable")
    run.add_argument("--machine")
    run.add_argument("--cpu", default="max")
    run.add_argument("--no-accel", action="store_false", dest="accel")
    run.add_argument("--extra-qemu-opts")
    run.set_defaults(func=cloud_run.run_vm)

    rm_vm = sp.add_parser("rm-vm")
    rm_vm.add_argument("instance_id")
    rm_vm.set_defaults(func=images.rm_vm)

    ls_vms = sp.add_parser("ls-vms")
    ls_vms.set_defaults(func=ls_vms_cli)

    ssh = sp.add_parser("ssh")
    ssh.add_argument("instance_id")
    ssh.add_argument("--user", required=False)
    ssh.set_defaults(func=ssh_cli)

    ansible_inventory = sp.add_parser("ansible-inventory")
    ansible_inventory_action = ansible_inventory.add_mutually_exclusive_group(
        required=True
    )
    ansible_inventory_action.add_argument(
        "--list", action="store_true", dest="list_command"
    )
    ansible_inventory_action.add_argument("--host")
    ansible_inventory.set_defaults(func=ansible_inventory_cli)

    return p


def main():
    logging.basicConfig(level=logging.INFO)
    args = parser().parse_args()

    if "func" not in args:
        parser().error("no command supplied")

    func_args = args.__dict__.copy()
    del func_args["func"]
    args.func(**func_args)


if __name__ == "__main__":
    main()
