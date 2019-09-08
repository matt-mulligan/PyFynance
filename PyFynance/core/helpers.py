import os


def makedirs(path):
    """
    will create the directory if it does not already exist
    :param path:
    :return:
    """

    if not os.path.isdir(path):
        path = os.path.dirname(path)

    if not os.path.exists(path):
        os.makedirs(path)
