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
from watchfiles import watch
import os
import shutil
import sys
import time
from common import REPOSITORY,getLog,csvEncode

TAG = "FC"

if __name__ == '__main__':
    watch_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    rep_dir, log = getLog(watch_dir)

    try:
        for changes in watch(watch_dir, raise_interrupt=False):
            for change in changes:
                if not any(x in change[1] for x in [REPOSITORY, 'venv', '.git']):
                    relative_path = os.path.relpath(change[1], watch_dir)
                    file_name = os.path.splitext(relative_path)[0] #.replace(os.sep, '_')
                    file_ext = os.path.splitext(relative_path)[1]
                    new_name = f"{file_name}_{int(time.time())}{file_ext}"
                    if os.path.exists(change[1]):
                        if os.path.isdir(change[1]):
                            new_path = os.path.join(rep_dir, relative_path)
                            try:
                                os.makedirs(new_path)
                                log.info(csvEncode((TAG,) + change + (relative_path,)))
                            except Exception as e:
                                print("\033[91m" + "!!!!!!!!" + str(e) + "\033[0m")
                        else:
                            new_path = os.path.join(rep_dir, new_name)
                            try:
                                shutil.copy2(change[1], new_path)
                                log.info(csvEncode((TAG,) + change + (new_name,)))
                            except Exception as e:
                                print("\033[91m" + "!!!!!!!!" + str(e) + "\033[0m")

    except KeyboardInterrupt:
        print('stopped via KeyboardInterrupt')
