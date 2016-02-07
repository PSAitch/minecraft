#!/bin/bash
# mc : Minecraft service

MC_ROOT="/srv/minecraft"
MC_VERSION="$(sudo grep server_version= /etc/minecraft.conf | awk -F'=' '{print $2}')"
MC_FILE_GET="https://s3.amazonaws.com/Minecraft.Download/versions/"$MC_VERSION"/minecraft_server."$MC_VERSION".jar"
MC_FILE="minecraft_server."$MC_VERSION".jar"
MC_EULA="eula.txt"
MC_FILE_LOC=$MC_ROOT"/"$MC_FILE
EULA_LOC=$MC_ROOT"/"$MC_EULA

cd_mc(){
	cd /srv/minecraft
}

run_mc(){
	cd_mc
	sudo java -Xms512M -Xmx512M -jar $MC_FILE nogui
}

rinse_mc(){
        if [ -f $MC_FILE_LOC ] ; then
                echo "Removing "$MC_FILE_LOC
                rm $MC_FILE_LOC
        fi
        get_mc
}

check_mc(){
	if [ -f $MC_FILE_LOC ] ; then
		echo "Minecraft Present "
	else
		echo "Minecraft JAR not found"
		return 1
	fi
	EULA_ACCEPT="$(sudo grep eula "$EULA_LOC" | awk -F'=' '{print $2}' | tr -d '[[:space:]]')"
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
			return 1
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
	mods)
		if [ -d $MC_ROOT/mods ]; then
			sudo ls $MC_ROOT/mods
		else
			echo "No mods folder"
		fi
		;;
	properties)
		if [ -z $2 ] ; then
			sudo cat $MC_ROOT/server.properties
		else
		        MC_PROP="$(sudo grep "$2" "$MC_ROOT"/server.properties | awk -F'=' '{print $2}')"
			echo $2"="$MC_PROP
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
		if  check_mc  ; then
			run_mc
		else
			echo "Minecraft not OK : "$MC_OK
		fi
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
	status)
		MC_STATUS="$(sudo ps all | grep java | grep -v grep | tr -d '[[:space:]]')"
		if [ -z $MC_STATUS ] ; then
			echo "Minecraft Not Running"
			exit 1
		else
			echo $MC_STATUS
			echo "minecraft running"
			exit 0
		fi
		;;
	*)
		echo "Usage mc [ parameters | test | check ]"
		echo "Usage mc install [ force ]"
#		echo "Usage mc service [ deploy | regress | start | stop ]"
		;;
esac

