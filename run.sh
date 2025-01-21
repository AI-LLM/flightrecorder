#!/bin/sh
#mitmproxy --mode local:"Zed" -s ./addon_log.py
mitmdump --mode local:"Zed" --flow-detail 3 | python log_mitmdump.py --include-url "/completion"
#cat mitmdump_output.txt | python log_mitmdump.py --include-url "/completion"