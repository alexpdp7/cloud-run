from socket import socket


def get_free_port():
    with socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]
