import glob
import os

"""
The helpers module is a collection of useful public functions that can be called in multiple other classes.

The aim of of this module is to encapsulate all of the useful functions that are shared between multiple classes to 
ensure that they are accessible from anywhere
"""


def find_all_files(path, patterns, recursive=False, full_path=True):
    """
    This method will find all the file in a specified path that match one of the patterns provided. this method also
    allows you to define if it should look recursivly or only at the top level

    :param path: string, path to search for files
    :param patterns: list, of patterns to search for
    :param recursive: boolean, indicating if the search should be recursive. default value is False
    :param full_path: boolean, indicates if the returned values should eb full paths or just file names. default value
           is True
    :return: list: either full file paths for just file names based on the value of full_path
    """

    matches = []
    for pattern in patterns:
        search_value = os.sep.join([path, pattern])
        matches.extend(glob.glob(search_value, recursive=recursive))

    if full_path:
        cleaned_matches = matches
    else:
        cleaned_matches = []
        for match in matches:
            cleaned_matches.append(match.split(os.sep)[-1])

    return cleaned_matches


def convert_tuple_to_dict(data_tuple, keys_list):
    """
    this helper method will convert a tuple of data to a dictionary with the specified column names

    :param data_tuple: a tuple containign the data you wish to convert to a dictionary
    :type data_tuple: tuple
    :param keys_list: a list of strings which will be used for dictionary keys
    :type keys_list: list
    :return: Dictionary containing the tuple data with appropriate key values
    """

    if len(data_tuple) != len(keys_list):
        raise AttributeError(
            f"Length of data_tuple ({len(data_tuple)}) and keys_list ({len(keys_list)}) do not match. "
            "Both parameters must be the same length to convert them to a dictionary"
        )

    if type(data_tuple) != tuple:
        raise AttributeError(
            f"Data type of argument 'data_tuple' is {type(data_tuple)}. Expected type is tuple."
        )

    if type(keys_list) != list:
        raise AttributeError(
            f"Data type of argument 'keys_list' is {type(keys_list)}. Expected type is list."
        )

    return dict(zip(keys_list, list(data_tuple)))
