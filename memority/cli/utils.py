class Exit(Exception):
    pass


def get_url(path, port):
    return f'http://127.0.0.1:{port}{path}'
