#!/bin/bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

cd $ROOT_DIR
MENU_ID=$(whiptail --clear --title 'Get info about host' \
--menu "Enter your choice:" 15 60 5 \
	"1" "local" \
	"2" "archhost" \
	"3" "archnote" \
	"4" "archsrv" \
	"5" "Quit" \
	3>&1 1>&2 2>&3)

if [ $? != 0 ]; then
	exit 1
fi

HOST_NAME=""
case $MENU_ID in
  "1")
	HOST_NAME="local"
	;;
  "2")
	HOST_NAME="archhost"
	;;
  "3")
	HOST_NAME="archnote"
	;;
  "4")
	HOST_NAME="archsrv"
	;;
  "5")
	exit 1
	;;
esac

/usr/bin/ansible-playbook update.yml --ask-become-pass --ask-vault-pass --extra-vars "variable_host=${HOST_NAME}" $@
