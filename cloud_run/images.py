import urllib.request

from cloud_run import directories


CLOUD_IMAGES = {
    "debian-bullseye": "https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.qcow2",
}


def get_cloud_image_path(os):
    return directories.get_cache_dir() / CLOUD_IMAGES[os].split("/")[-1]


def get_cloud_image(os):
    ofile = get_cloud_image_path(os)
    if ofile.exists():
        return ofile
    url = CLOUD_IMAGES[os]
    with urllib.request.urlopen(url) as d:
        with open(ofile, "wb2") as o:
            o.write(d.read())
    return ofile
