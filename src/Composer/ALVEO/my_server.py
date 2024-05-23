"""
Aimilios Leftheriotis
Microlab@NTUA

AI@EDGE project

This module defines the MyServer class, which inherits from the XXXServer class defined in the servers module, depending on the target platform.

Methods:
- __init__(self, logger): Initializes the MyServer instance, sets up the logger, and calls the method to set experiment configurations.

DO-NOT Edit this file
"""

# Custom module
import alveo_server

class MyServer(alveo_server.AlveoServer):
    def __init__(self, logger):
        super().__init__(logger)