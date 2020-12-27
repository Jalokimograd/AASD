#!/bin/sh

sudo prosodyctl register environmentmanager localhost environmentmanager

for number in $(seq 0 9)
do
	sudo prosodyctl register mobileagent${number} localhost mobileagent${number}
done
exit 0
