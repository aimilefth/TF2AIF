import os
import subprocess
import sys
import json
import shutil
#import re
import time

def add_num_threads_to_instance_UID(instance_uid, metrics_data):
    # Check if the last dictionary has the key 'NUM_THREADS'
    if 'NUM_THREADS' in metrics_data[-1]:
        num_threads = metrics_data[-1]['NUM_THREADS']
        print(f"'NUM_THREADS' exists with value: {num_threads}")
        # Split the instance_UID and insert the NUM_THREADS value
        uid_parts = instance_uid.split(':')
        uid_parts[3] += f"_{num_threads}"
        instance_uid = ':'.join(uid_parts)
    return instance_uid

def check_output_format(output):
    lines = output.strip().split("\n")  # Split the output into lines
    if len(lines) < 2:  # There must be at least 2 lines to check
        return False
    # Check if the last two lines start with the expected strings
    correct_bool = lines[-2].startswith("E2E Latency") and lines[-1].startswith("Throughput")
    if(correct_bool):
        print(output)
    else:
        print('The request was not completed') 
    return correct_bool

def main():

    # Check if all required environment variables are set
    required_vars = ['NUMBER_OF_REQUESTS', 'CLIENT_APP', 'SERVER_IP', 'SERVER_PORT', 'MOUNTED_DIR', 'METRICS_OUTPUT', 'LOG_FILE']
    for var in required_vars:
        if var not in os.environ:
            sys.exit(f"Error: The environment variable {var} is not set.")

    NUMBER_OF_REQUESTS = int(os.environ['NUMBER_OF_REQUESTS'])
    CLIENT_APP = os.environ['CLIENT_APP']
    SERVER_IP = os.environ['SERVER_IP']
    SERVER_PORT = os.environ['SERVER_PORT']
    MOUNTED_DIR = os.environ['MOUNTED_DIR']
    METRICS_OUTPUT = os.environ['METRICS_OUTPUT']
    LOG_FILE = os.environ['LOG_FILE']

    # Run the get inference command for ${NUMBER_OF_REQUESTS} times
    for _ in range(NUMBER_OF_REQUESTS):
        result = subprocess.run(["python3", CLIENT_APP], stdout=subprocess.PIPE, text=True)
        while not check_output_format(result.stdout):
            time.sleep(2)
            result = subprocess.run(["python3", CLIENT_APP], stdout=subprocess.PIPE, text=True)


    # Run the get metrics command
    subprocess.run(["python3", CLIENT_APP, "-m", "True", "-n", str(NUMBER_OF_REQUESTS)])
    
    # Load the metrics.json file
    try:
        with open(METRICS_OUTPUT, 'r') as f:
            metrics_data = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Error: File {METRICS_OUTPUT} not found.")

    # Get the instance_UID from the first JSON object
    instance_uid = metrics_data[0].get('instance_UID')
    if not instance_uid:
        sys.exit("Error: instance_UID not found in the first JSON object.") 
    instance_uid = add_num_threads_to_instance_UID(instance_uid, metrics_data)
    # Copy the files to the mounted directory with the new name
    shutil.copy(METRICS_OUTPUT, os.path.join(MOUNTED_DIR, f'{instance_uid}.json'))
    shutil.copy(LOG_FILE, os.path.join(MOUNTED_DIR, f'{instance_uid}.log'))
    # Change the permissions of the files to full permissions (read, write, execute for owner, group, others)
    os.chmod(os.path.join(MOUNTED_DIR, f'{instance_uid}.json'), 0o777)
    os.chmod(os.path.join(MOUNTED_DIR, f'{instance_uid}.log'), 0o777)

if __name__ == '__main__':
    main()