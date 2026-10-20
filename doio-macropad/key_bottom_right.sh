#!/bin/zsh
exec >> /tmp/kb16-laser.log 2>&1
echo "== $(date +%T) start"
/Users/ariemeir/dev/diy/workshop/xtool-laser/power/laser toggle
echo "== $(date +%T) exit $?"
