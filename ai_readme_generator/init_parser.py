import argparse


def init_parser():
    parser = argparse.ArgumentParser(
        description='AI README Generator',
    )
    parser.add_argument(
        "-u", "--repo_url",
        default='',
        required=False,
        help="Git repository URL or local path",
    )
    parser.add_argument(
        "-b", "--branch",
        default='',
        required=False,
        help="Repository branch name. Default: main",
    )
    parser.add_argument(
        "-e", "--file_ext_filter",
        default='',
        required=False,
        help="Filter the files based on their extensions." +
             " For instance: 'py,md', 'js,jsx' or 'php'",
    )
    parser.add_argument(
        "-m", "--model",
        default='gpt-3.5-turbo-16k',
        required=False,
        choices=[
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"
        ],
        help="GPT model. Default: gpt-3.5-turbo-16k",
    )
    parser.add_argument(
        "-t", "--temperature",
        default='0.7',
        required=False,
        help="Temperature for the GPT model. Default: 0.7",
    )
    parser.add_argument(
        "-D", "--debug",
        default='0',
        required=False,
        help="Show debug information",
    )

    return parser
