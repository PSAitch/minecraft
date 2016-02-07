#!/bin/bash
# mc : script for installing Minecraft
case $1 in
	install)
		sudo cp minecraft_server.py /usr/src
		sudo cp mc /etc/init
		;;
	regress)
		sudo rm /usr/src/minecraft_server.py
		sudo rm /etc/init.d/minecraft
		;;
	test)
		sudo python /usr/src/minecraft_server.py $2
		;;
	*)
		echo "Usage deploy [ install | regress ]"
		;;
esac
