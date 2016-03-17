#!/bin/bash

initdb /usr/local/var/postgres -E utf8
createuser -d -l -P -r -s -h localhost apiski
createdb -h localhost -U apiski --password apiski