#!/bin/sh

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

# Trap ctrl-c to ensure clean exit and cleanup watchdir.py
cleanup() {
    kill $(jobs -p) 2>/dev/null
    pkill -f "watchdir.py" 2>/dev/null
}
trap cleanup INT

if ! pgrep -f "watchdir.py" > /dev/null; then
    python watchdir.py $1 &
fi

#mitmproxy --mode local:"Zed" -s ./addon_log.py
#cat mitmdump_output.txt | python log_mitmdump.py --include-url "/completion"
mitmdump --mode local:"Zed" --flow-detail 3 | python log_mitmdump.py $([ -n "$2" ] && echo "--include-url $2" || echo "--include-url /completion") $([ -n "$1" ] && echo "--dir $1")
