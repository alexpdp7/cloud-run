import contextlib
import dataclasses
import json

from cloud_run import directories


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
