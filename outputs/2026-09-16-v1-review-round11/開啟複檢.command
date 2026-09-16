#!/bin/zsh
set -eu
tiri_recheck_dir="${0:A:h}"
if [[ ! -f "$tiri_recheck_dir/launch_review.py" ]]; then
  tiri_recheck_dir='/Users/jonathanyu/Desktop/Travail/Justhings/投資人協會 TIRI/WEB DEMO/outputs/2026-09-16-v1-review-round11'
fi
exec /usr/bin/env python3 "$tiri_recheck_dir/launch_review.py"
