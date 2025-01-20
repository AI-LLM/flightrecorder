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
                    file_name = os.path.splitext(relative_path)[0].replace(os.sep, '_')
                    file_ext = os.path.splitext(relative_path)[1]
                    new_name = f"{file_name}_{int(time.time())}{file_ext}"
                    if os.path.exists(change[1]):
                        new_path = os.path.join(rep_dir, new_name)
                        shutil.copy2(change[1], new_path)
                    log.info(csvEncode((TAG,) + change + (new_name,)))

    except KeyboardInterrupt:
        print('stopped via KeyboardInterrupt')
