import os
from flask import Flask, send_from_directory
from ext_config import *

def robot():
    """
    This function handles the robot.txt file for the web application.
    It returns a string that specifies which user agents are allowed or disallowed to crawl the site.
    """
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Robot check")
    return send_from_directory(app.static_folder, "robots.txt")