# AI Flight Recorder
# Copyright (C) 2025 Wei Lu (mailwlu@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Any, Union
import logging
from logging import getLogger
from concurrent_log_handler import ConcurrentRotatingFileHandler
import os
import sys
import io
import csv

REPOSITORY = ".flightrecorder"
LOG_FILE = "activities.log"
formatter = logging.Formatter(fmt='%(asctime)s,%(levelname)-8s,%(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')

def csvEncode(data: Any)->str:
    output = io.StringIO()
    if isinstance(data, str):
        data = [data]
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(data)
    return output.getvalue().strip()

def getPaths(watch_dir: str) -> tuple[str, str]:
    # Use an absolute path to prevent file rotation trouble.
    rep_dir = os.path.join(os.path.abspath(watch_dir), REPOSITORY)
    if not os.path.exists(rep_dir):
        os.makedirs(rep_dir)
    return rep_dir, os.path.join(rep_dir, LOG_FILE)

def getLog(watch_dir: str) -> tuple[str, str]:
    log = getLogger(watch_dir)
    rep_dir, log_file = getPaths(watch_dir)
    # Rotate log after reaching 1024K, keep 5 old copies.
    rotateHandler = ConcurrentRotatingFileHandler(log_file, "a", 1024 * 1024, 5)
    rotateHandler.setFormatter(formatter)
    log.addHandler(rotateHandler)
    screen_handler = logging.StreamHandler(stream=sys.stderr)
    screen_handler.setFormatter(formatter)
    log.addHandler(screen_handler)
    log.setLevel(logging.INFO)
    return rep_dir, log

def findLastVersion(watch_dir: str, change_file_path:str) -> Union[str, None]:
    """return relative_path or None"""
    _, log_file = getPaths(watch_dir)

    if not os.path.exists(log_file):
        print("\033[31m"+"!"*8+f"log file {log_file} does not exist\033[0m")
        return None

    with open(log_file, 'r') as f:
        # Read file in reverse order to find most recent first
        lines = f.readlines()
        for line in reversed(lines):
            try:
                # Split CSV line
                reader = csv.reader([line.strip()])
                row = next(reader)
                if len(row) >= 6 and row[4] == change_file_path:
                    return row[5]
            except Exception as e:
                print("\033[31m"+"!"*8+f"Error parsing log line: {str(e)}\033[0m")
                continue

    return None
