#!/bin/bash
# mc : script for installing Minecraft
case $1 in
	install)
		sudo cp minecraft_server.py /usr/src
		sudo cp minecraft /etc/init.d
		sudo update-rc.d minecraft defaults
		;;
	regress)
                sudo update-rc.d minecraft remove
		sudo rm /usr/src/minecraft_server.py
		sudo rm /etc/init.d/minecraft
		;;
	enable)
                sudo update-rc.d minecraft enable
		;;
	disable)
                sudo update-rc.d minecraft disable
		;;
	test)
		sudo python /usr/src/minecraft_server.py $2
		;;
	*)
		echo "Usage deploy [ install | regress ]"
		;;
esac
