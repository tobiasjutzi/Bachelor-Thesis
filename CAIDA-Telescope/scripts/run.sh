#!/bin/bash

#
# script based on https://github.com/thisni1s/telescope/
#

sudo docker run -it --rm -v ./code:/code -v /home/limbo/swift-scripts/logs/concat-conn.log:/conn-log -v /home/limbo/swift-scripts/logs/concat-notice.log:/notice-log  py bash
