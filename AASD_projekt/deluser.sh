#!/bin/sh

prosodyctl deluser environmentmanager@localhost


for number in $(seq 0 9)
do
	prosodyctl deluser mobileagent${number}@localhost
done
exit 0