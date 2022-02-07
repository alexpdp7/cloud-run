import contextlib
import dataclasses
import json

from cloud_run import directories
from cloud_run import qemu


@contextlib.contextmanager
def state(instance_id, forwards):
    state_file = directories.get_state_dir() / instance_id
    with open(state_file, "w") as f:
        json.dump(
            {
                "forwards": list(map(dataclasses.asdict, forwards)),
            },
            f,
        )

    yield None
    state_file.unlink()


def get_state_if_exists(instance_id):
    state_file = directories.get_state_dir() / instance_id
    if not state_file.exists():
        return
    return _parse_state_file(state_file)


def get_state(instance_id):
    state_file = directories.get_state_dir() / instance_id
    return _parse_state_file(state_file)


def _parse_state_file(state_file):
    with open(state_file) as f:
        json_state = json.load(f)
    return list(map(lambda j: qemu.HostForward(**j), json_state["forwards"]))
