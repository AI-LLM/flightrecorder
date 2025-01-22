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
from common import REPOSITORY,getLog,csvEncode

import sys
import re
import time
import dataclasses, json
from dataclasses import dataclass
from typing import Any, Union
import os
import argparse
from common import REPOSITORY,getLog,csvEncode

@dataclass
class HttpRecord:
    url: str
    method: str
    user_agent: str
    request_body: Union[dict, list, str]
    response_body: Union[dict, list, str]

def parse_json(text: str) -> Union[dict, list, str]:
    """Try to parse JSON text, return original text if parsing fails"""
    text = text.strip()
    if not text:
        return ""
    try:
        # Try parsing as a single JSON object
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            # Try parsing as multiple JSON objects
            objects = []
            for line in text.split('\n'):
                line = line.strip()
                if line:
                    objects.append(json.loads(line))
            return objects if objects else text
        except json.JSONDecodeError:
            return text

class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)

def dump(rec: HttpRecord, rep_dir, log):
    data = json.dumps(rec, cls=EnhancedJSONEncoder, indent=4)
    new_name = f"http_{int(time.time())}.json"
    new_path = os.path.join(rep_dir, new_name)
    data = json.dumps(rec, cls=EnhancedJSONEncoder, indent=4)
    with open(new_path, 'w') as f:
        f.write(data)
    log.info(csvEncode((
        rec.user_agent,
        rec.url,
        rec.request_body["model"] if isinstance(rec.request_body, dict) and "model" in rec.request_body else "",
        new_name
    )))

    def find_messages(obj):
        if isinstance(obj, dict):
            if "messages" in obj:
                for i, msg in enumerate(obj["messages"]):
                    if isinstance(msg, dict) and "content" in msg:
                        if isinstance(msg["content"], str):
                            print("_"*8+"Message " + str(i) + "_"*8)
                            print(msg["content"])
                        elif isinstance(msg["content"], list):
                            for item in msg["content"]:
                                if isinstance(item, dict) and "text" in item:
                                    print("_"*8+"Message " + str(i) + "_"*8)
                                    print(item["text"])
            for value in obj.values():
                find_messages(value)
        elif isinstance(obj, list):
            for item in obj:
                find_messages(item)

    if isinstance(rec.request_body, (dict, list)):
        find_messages(rec.request_body)

def process(rep_dir, log, include_url=None):
    current_request = []
    collecting = False

    url = ""
    method = ""
    user_agent = ""
    request_body = ""
    response_body = ""

    in_request_headers = False
    in_request_body = False
    in_response_headers = False
    in_response_body = False

    new_name = f"mitmdump_output.txt"
    new_path = os.path.join(rep_dir, new_name)

    for line in sys.stdin:
        with open(new_path, 'a') as f:
            f.write(line)

        line = line.rstrip()
        if line.startswith('127.0.0.1:0: ') and ('HTTP/' in line):
            # Start of new request
            if collecting:
                # Save previous record if exists
                dump(HttpRecord(
                    url=url,
                    method=method,
                    user_agent=user_agent,
                    request_body=parse_json(request_body),
                    response_body=parse_json(response_body)
                ), rep_dir, log)

            # Reset variables
            collecting = True
            url = ""
            method = ""
            user_agent = ""
            request_body = ""
            response_body = ""
            in_request_headers = True
            in_request_body = False
            in_response_headers = False
            in_response_body = False

            # Parse first line
            parts = line.strip().split(' ')
            if len(parts) >= 3:
                method = parts[1]
                url = parts[2].split(' ')[0]
                if include_url and not re.search(include_url, url):
                    collecting = False
                    continue

        elif collecting:
            if line.startswith(' << HTTP'):
                if re.match(r' << HTTP/[1-9]\.[0-9] 2', line):  # Success status codes
                    in_request_headers = False
                    in_request_body = False
                    in_response_headers = True
                    in_response_body = False
                else:
                    # Not a success response, skip this record
                    collecting = False
                continue

            if in_request_headers:
                if line.strip() == "":
                    in_request_headers = False
                    in_request_body = True
                elif line.startswith('    user-agent: '):
                    user_agent = line.replace('    user-agent: ', '')
            elif in_request_body:
                if line.strip():  # Skip empty lines in body
                    request_body += line + "\n"
            elif in_response_headers:
                if line.strip() == "":
                    in_response_headers = False
                    in_response_body = True
            elif in_response_body:
                if not line.startswith('[') and line.strip():
                    response_body += line + "\n"
                else:
                    collecting = False
                    in_response_body = False
                    dump(HttpRecord(
                        url=url,
                        method=method,
                        user_agent=user_agent,
                        request_body=parse_json(request_body),
                        response_body=parse_json(response_body)
                    ), rep_dir, log)

    # Don't forget to save the last record if exists
    if collecting:
        dump(HttpRecord(
            url=url,
            method=method,
            user_agent=user_agent,
            request_body=parse_json(request_body),
            response_body=parse_json(response_body)
        ), rep_dir, log)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP traffic logger')
    parser.add_argument('--dir', default='.', help='Log directory path (default: ".")')
    parser.add_argument('--include-url', help='URL regex pattern to include (optional)')
    args = parser.parse_args()

    rep_dir, log = getLog(args.dir)
    process(rep_dir, log, args.include_url)
