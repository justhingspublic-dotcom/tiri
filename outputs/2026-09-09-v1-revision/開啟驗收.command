#!/bin/zsh
set -eu
tiri_review_dir="${0:A:h}"
exec /usr/bin/env python3 "$tiri_review_dir/launch_review.py"
