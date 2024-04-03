from collections import abc
import logging
import lzma
import shutil
import urllib.request

from cloud_run import directories


logger = logging.getLogger(__name__)


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


def get_omnios_stable_cloud_image_url():
    BASE = "https://downloads.omnios.org/media/stable"
    with urllib.request.urlopen(f"{BASE}/") as i:
        i_html = i.read().decode("utf8")
    lines = [line for line in i_html.splitlines() if 'cloud.raw.zst"' in line]
    line = lines[-1]
    parts = line.split('"')
    assert len(parts) == 7, f"{line} should have 7 parts when split by double quotes"
    return f"{BASE}/{parts[3]}"


_CLOUD_IMAGES = {
    "debian-bullseye": "https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.qcow2",  # noqa
    "debian-bookworm": "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2",  # noqa
    "fc35": "https://download.fedoraproject.org/pub/fedora/linux/releases/35/Cloud/x86_64/images/Fedora-Cloud-Base-35-1.2.x86_64.qcow2",  # noqa
    "fc36": "https://download.fedoraproject.org/pub/fedora/linux/releases/36/Cloud/x86_64/images/Fedora-Cloud-Base-36-1.5.x86_64.qcow2",  # noqa
    "fc37": "https://download.fedoraproject.org/pub/fedora/linux/releases/37/Cloud/x86_64/images/Fedora-Cloud-Base-37-1.7.x86_64.qcow2",  # noqa
    "fc38": "https://download.fedoraproject.org/pub/fedora/linux/releases/38/Cloud/x86_64/images/Fedora-Cloud-Base-38-1.6.x86_64.qcow2",  # noqa
    "fc39": "https://download.fedoraproject.org/pub/fedora/linux/releases/39/Cloud/x86_64/images/Fedora-Cloud-Base-39-1.5.x86_64.qcow2",  # noqa
    "c9-stream": get_centos_9_stream_cloud_image_url,
    "alma8": "https://repo.almalinux.org/almalinux/8/cloud/x86_64/images/AlmaLinux-8-GenericCloud-latest.x86_64.qcow2",  # noqa
    "ubuntu2204": "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64-disk-kvm.img",  # noqa
    "omnios": get_omnios_stable_cloud_image_url,
}


AVAILABLE_CLOUD_IMAGES = _CLOUD_IMAGES.keys()


def get_cloud_image_url(os: str) -> str:
    if os.startswith("https://"):
        return os
    return (
        _CLOUD_IMAGES[os]()
        if isinstance(_CLOUD_IMAGES[os], abc.Callable)
        else _CLOUD_IMAGES[os]
    )


def get_cloud_image_path(os):
    file = get_cloud_image_url(os).split("/")[-1]
    if file.endswith(".zst"):
        file = file.removesuffix(".zst")
    if file.endswith(".xz"):
        file = file.removesuffix(".xz")
    return directories.get_cache_dir() / file


def get_cloud_image(os):
    ofile = get_cloud_image_path(os)
    logger.info("Checking image at %s", ofile)
    if ofile.exists():
        logger.info("Exists!")
        return ofile
    url = get_cloud_image_url(os)
    logger.info("Does not exist, downloading from %s", url)
    if url.endswith(".qcow2") or url.endswith(".img"):
        with urllib.request.urlopen(url) as d:
            with open(ofile, "wb") as o:
                shutil.copyfileobj(d, o)
        return ofile
    if url.endswith(".zst"):
        import pyzstd

        with urllib.request.urlopen(url) as d:
            with open(ofile, "wb") as o:
                pyzstd.decompress_stream(d, o)
        return ofile

    if url.endswith(".xz"):
        with urllib.request.urlopen(url) as d:
            with lzma.open(d) as dd:
                with open(ofile, "wb") as o:
                    shutil.copyfileobj(dd, o)
        return ofile

    assert False, f"don't know what to do with {url}"
