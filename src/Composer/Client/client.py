#!/usr/bin/python3

"""
Client Documentation

Overview:
=========
The `client.py` script is a main driver of the client application. It constructs a command line argument parser, and 
uses those arguments to run the client application. 

The client application can either ask the server for performance metrics or send a dataset for inference. 
The script creates an instance of `MyClient` (an extension of the `BaseClient` class) to perform these operations. 

Command Line Arguments:
=======================
1. --dataset_path: Path of the dataset. The default is obtained from the DATASET environment variable.
2. --address: Address to connect to. The default is given from the SERVER_IP and SERVER_PORT environment variables.
3. --ask_metrics: A flag to indicate whether to request performance metrics from the server instead of performing inference. The default is False.
4. --number_of_metrics: Specifies the number of metrics to retrieve from the server. -1 translates to all. The default is -1 (all).

Example usage:
python client.py --dataset_path <path_to_your_image> --address <server_url> --ask_metrics False --number_of_metrics -1

This script is a part of the AI@EDGE project, developed at ICCS, Microlab NTUA.

Contributors:
=============
- Aimilios Leftheriotis
- Achilleas Tzenetopoulos
"""
# Actual code starts here...

import argparse
import os
import my_client 
import logging
import logging.config

def strtobool(bool_str):
    my_bool = bool_str.lower() in ['true', 'yes', 'y']
    return my_bool

def main():
    # Construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    default_dataset_path = os.environ['DATASET']
    default_address = 'http://' + os.environ['SERVER_IP'] + ':' + os.environ['SERVER_PORT']
    ap.add_argument('-d', '--dataset_path',      type=str, default=default_dataset_path, help='Path of Dataset. Default is given from DATASET environmental variable')
    ap.add_argument('-a', '--address',           type=str, default=default_address, help='Address to connect to. Default is given from SERVER_IP and SERVER_PORT environmental variables')
    ap.add_argument('-m', '--ask_metrics',       type=str, default='False', help='Whether to ask for metrics instead of inference. Default is False')
    ap.add_argument('-n', '--number_of_metrics', type=int, default=-1, help='Number of metrics to get. -1 translates to all. Default is -1 (all)')
    args = ap.parse_args()

    # Configure logging based on the environmental variable 'LOG_CONFIG'
    logging.config.fileConfig(os.environ['LOG_CONFIG'], disable_existing_loggers=False)

    logging.info(' Command line options:')
    logging.info('--dataset_path      : {}'.format(args.dataset_path))
    logging.info('--address           : {}'.format(args.address))
    logging.info('--ask_metrics       : {}'.format(args.ask_metrics))
    logging.info('--number_of_metrics : {}'.format(args.number_of_metrics))
    client = my_client.MyClient(args.address)
    if(strtobool(args.ask_metrics)):
        client.ask_metrics(args.number_of_metrics)
    else:
        client.ask_inference(args.dataset_path)

if __name__ == '__main__':
    main()