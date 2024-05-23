"""
Aimilios Leftheriotis
Microlab@NTUA

AI@EDGE project

This module defines the MyServer class, which inherits from the XXXServer class defined in the servers module, depending on the target platform.

Methods:
- __init__(self, logger): Initializes the MyServer instance, sets up the logger, and calls the method to set experiment configurations.

EDIT these methods according to the needs of the experiment/platform
"""

# Custom module
import gpu_server

class MyServer(gpu_server.GpuServer):
    def __init__(self, logger):
        super().__init__(logger)