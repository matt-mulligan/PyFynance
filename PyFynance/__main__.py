import argparse


def main():
    args = _parse_arguments()
    domain_analyser = DomainAnalyser(args._client_id, args._client_secret)
    analyser_tasks = {
        "analyse_suburb_sold": _run_analyse_suburb_sold
    }
    analyser_tasks[args.task](domain_analyser, args)


def _create_arg_parser():
    """
    this method will create an argument parser object
    :return:
    """

    parser = argparse.ArgumentParser(description="PyFy Argument parser")
    parser.add_argument("--task_type", metavar="task_type", help="task_type")
    parser.add_argument("", metavar="task_argument", help="task_argument")


    return parser


def _parse_arguments():
    """
    this method will setup and laod the arguments using the Arg Parser class
    :return:
    """
    arg_parser = _create_arg_parser()
    return arg_parser.parse_args()


def _run_analyse_suburb_sold(domain_analyser, args):
    """
    this method will setup and run the analyse_suburb_sold
    :param domain_analyser: an instance of the domain analyser class
    :param args: a python object containing all the command line arguments parsed
    :return:
    """

    location_info = build_location_info()

if __name__ == "__main__":
    main()