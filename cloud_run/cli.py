import argparse

import cloud_run
from cloud_run import images
from cloud_run import cloud_images


def ls_vms_cli():
    print("\n".join(images.get_vm_imgs()))


def parser():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers()

    run = sp.add_parser("run")
    run.add_argument("os", choices=cloud_images.CLOUD_IMAGES.keys())
    run.add_argument("instance_id")
    run.add_argument("--local-hostname", required=False)
    run.add_argument("--mem", required=False, default="1G", help="default %(default)s")
    run.add_argument("--disk", required=False, default="8G", help="default %(default)s")
    run.set_defaults(func=cloud_run.run_vm)

    rm_vm = sp.add_parser("rm-vm")
    rm_vm.add_argument("instance_id")
    rm_vm.set_defaults(func=images.rm_vm)

    ls_vms = sp.add_parser("ls-vms")
    ls_vms.set_defaults(func=ls_vms_cli)

    return p


def main():
    args = parser().parse_args()
    func_args = args.__dict__.copy()
    del func_args["func"]
    args.func(**func_args)


if __name__ == "__main__":
    main()
