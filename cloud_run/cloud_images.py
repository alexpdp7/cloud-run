from collections import abc
import shutil
import urllib.request

from cloud_run import directories


def get_centos_9_stream_cloud_image_url():
    BASE = "https://cloud.centos.org/centos/9-stream/x86_64/images/"
    with urllib.request.urlopen(BASE) as i:
        i_html = i.read().decode("utf8")
    name = [
        line
        for line in i_html.splitlines()
        if "GenericCloud" in line and 'qcow2"' in line
    ][-1].split('"')[11]
    return BASE + name


_CLOUD_IMAGES = {
    "debian-bullseye": "https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.qcow2",  # noqa
    "fc35": "https://download.fedoraproject.org/pub/fedora/linux/releases/35/Cloud/x86_64/images/Fedora-Cloud-Base-35-1.2.x86_64.qcow2",  # noqa
    "fc36": "https://download.fedoraproject.org/pub/fedora/linux/releases/36/Cloud/x86_64/images/Fedora-Cloud-Base-36-1.5.x86_64.qcow2",  # noqa
    "c9-stream": get_centos_9_stream_cloud_image_url,
    "alma8": "https://repo.almalinux.org/almalinux/8/cloud/x86_64/images/AlmaLinux-8-GenericCloud-latest.x86_64.qcow2",  # noqa
}


AVAILABLE_CLOUD_IMAGES = _CLOUD_IMAGES.keys()


def get_cloud_image_url(os):
    return (
        _CLOUD_IMAGES[os]()
        if isinstance(_CLOUD_IMAGES[os], abc.Callable)
        else _CLOUD_IMAGES[os]
    )


def get_cloud_image_path(os):
    return directories.get_cache_dir() / get_cloud_image_url(os).split("/")[-1]


def get_cloud_image(os):
    ofile = get_cloud_image_path(os)
    if ofile.exists():
        return ofile
    url = get_cloud_image_url(os)
    with urllib.request.urlopen(url) as d:
        with open(ofile, "wb") as o:
            shutil.copyfileobj(d, o)
    return ofile
