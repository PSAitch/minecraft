#!/bin/bash
# mc : Minecraft service

MC_ROOT="/srv/minecraft"
MC_VERSION="$(sudo grep server_version= /etc/minecraft.conf | awk -F'=' '{print $2}')"
MC_FILE_GET="https://s3.amazonaws.com/Minecraft.Download/versions/"$MC_VERSION"/minecraft_server."$MC_VERSION".jar"
MC_FILE="minecraft_server."$MC_VERSION".jar"
MC_EULA="eula.txt"
MC_FILE_LOC=$MC_ROOT"/"$MC_FILE
#MC_SERVER_NAME="$(sudo grep server= /etc/minecraft.conf | awk -F'=' '{print $2}')"
EULA_LOC=$MC_ROOT"/"$MC_EULA

cd_mc(){
	cd /srv/minecraft
}

run_mc(){
	cd_mc
	sudo java -Xms512M -Xmx512M -jar $MC_FILE nogui
}

rinse_mc(){
#        MC_FILE_LOC="/srv/minecraft/"$MC_FILE
#        EULA_LOC="/srv/minecraft/"$MC_EULA
        if [ -f $MC_FILE_LOC ] ; then
                echo "Removing "$MC_FILE_LOC
                rm $MC_FILE_LOC
        fi
        get_mc
}

check_mc(){
#	MC_FILE_LOC="/srv/minecraft/"$MC_FILE
#	EULA_LOC="/srv/minecraft/"$MC_EULA
	if [ -f $MC_FILE_LOC ] ; then
		echo "Minecraft Present "
	else
		echo "Minecraft JAR not found"
		return 1
	fi
	EULA_ACCEPT="$(sudo grep eula "$EULA_LOC" | awk -F'=' '{print $2}' | tr -d '[[:space:]]')"
#	echo "EULA:"$EULA_ACCEPT
	case $EULA_ACCEPT in
		true)
			echo "EULA Accepted"
			return 0
			;;
		false)
			echo "EULA not accepted"
			return 1
			;;
		*)
		        echo "EULA:"$EULA_ACCEPT
#			return 1
			;;
	esac
}

get_mc(){
	cd_mc
	sudo wget $MC_FILE_GET
	sudo chmod +x $MC_FILE
}

case $1 in
	parameters)
		echo "Version     : "$MC_VERSION
		echo "File        : "$MC_FILE
		echo "Remote File : "$MC_FILE_GET
#		echo "Server Name : "$MC_SERVER_NAME
		;;
	install)
		case $2 in
			force)
				get_mc
				;;
			*)
				if check_mc ; then
                                        echo "Minecraft is up to date"
				else
					get_mc
				fi
				;;
		esac
		;;
	check)
		if check_mc ; then
			echo "OK"
		else
			echo "Bad"
		fi
		;;
#	service)
#		case $2 in
#			deploy)
				# service deployment
#				sudo cp /home/ubuntu/minecraft.conf /etc/init/minecraft.conf
#				sudo initctl reload-configuration
#				;;
#			regress)
				# service regression
#				sudo rm /etc/init/minecraft.conf
#				;;
#			start)
#				sudo start minecraft
#				;;
#			stop)
#				sudo stop minecraft
#				;;
#			log)
#				sudo tail /var/log/upstart/minecraft.log
#				;;
#			*)
#				if [ -f /etc/init/minecraft.conf ] ; then
#					echo "Deployed"
#				else
#					echo "Not Deployed"
#				fi
#				;;
#		esac
#		;;
	test)
#		MC_OK=check_mc $1
#		if [[  $MC_OK==1 ]] ; then
#		if [ check_mc $1 ] ; then
#			echo "Minecraft not OK : "$MC_OK
#		elif [ $2 !="" ] ; then
#			run_mc $2
#		elif [ $SERVER_NAME !="" ] ; then
#			run_mc $SERVER_NAME
#		else
			run_mc
#		fi
		;;
#	start)
#		cd_mc
#		screen -S minecraft sudo java -Xms512M -Xmx512M -jar minecraft_server.jar nogui &
#		sudo stert minecraft
#		;;
#	stop)
#		cd_mc
#                screen -r minecraft sudo java -Xms512M -Xmx512M -jar minecraft_server.jar nogui
#		sudo stop minecraft
 #               ;;
	*)
		echo "Usage mc [ parameters | test | check ]"
		echo "Usage mc install [ force ]"
#		echo "Usage mc service [ deploy | regress | start | stop ]"
		;;
esac

