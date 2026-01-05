import argparse
import configparser


def read_args():
    '''
    Read the argument while execution.
    This function will take the config file.
    '''
    parser = argparse.ArgumentParser(
        description="Run data extraction pipeline")
    parser.add_argument('config', type=str, help="Config file name")
    return parser


def read_config(configfile):
    '''
    Function to read the config file.

    Input
    -----
    configfile: Name of the config file.

    Output
    -----
    config: Read config file. dict.
    '''
    config = configparser.ConfigParser()
    config.optionxform = str  # <-- preserve case
    config.read(configfile)
    return config
