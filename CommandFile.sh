#!/bin/bash


sudo dmsetup table /dev/mapper/cachedev | grep "dirty blocks"

