#!/bin/bash
# mc : script for installing Minecraft
case $1 in
	deploy)
		sudo cp minecraft_server.py /usr/src
		sudo cp minecraft /etc/init.d
		;;
	install)
		sudo update-rc.d minecraft defaults
		;;
	regress)
                sudo update-rc.d minecraft remove -f
		;;
	remove)
		sudo rm /usr/src/minecraft_server.py
		sudo rm /etc/init.d/minecraft
		;;
	enable)
                sudo update-rc.d minecraft enable
		;;
	disable)
                sudo update-rc.d minecraft disable
		;;
	configure)
		sudo adduser -U  minecraft -m -b /srv
		sudo passwd minecraft
		;;
	test)
#		sudo python /usr/src/minecraft_server.py $2
		if sudo service minecraft $2 ; then
			echo "Test Command Successful"
		else
	               sudo python /usr/src/minecraft_server.py $2
		fi
		;;
	*)
		echo "Usage"
		echo "	mc configure "
		echo "Set up user and root folder"
		echo "	mc [ deploy | remove ]"
		echo "copy files"
		echo "	mc [ install | regress ]"
		echo "register or deregister service"
		echo "	mc [ enable | disable ]"
		echo "control status of service"
		echo "	mc test [ start | stop | status ] "
		echo "test the minecraft server script"
		;;
esac
