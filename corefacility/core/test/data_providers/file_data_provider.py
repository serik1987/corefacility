import csv


def file_data_provider(filename):
    """
    Loads test data that contain in separate CSV file
    :param filename: full path to the CSV file
    :return: list of some function arguments
    """
    arg_list = []
    with open(filename, "r") as arg_file:
        arg_reader = csv.reader(arg_file)
        for args in arg_reader:
            arg_list.append(tuple(args))
    return arg_list
