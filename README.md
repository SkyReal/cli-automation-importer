# What is the purpose of this program?

There are two parts for this program:
	A 'host server' program which is designed to scan a repertory containing CAD files, opening a temporary mapping that is going to send the paths of the CAD files to every computer that has started the 'client' program. Then, it get the time of import of every CAD files and write them in an Excel file for futur reviews.
 	A 'client' program conceived to get the paths of the CAD files and import them into a XRCenter.


 # What do you need to make the program valid ?
 
	-> First, you must be on the same network. 
	
   	->  Do not forget to set up the config file correctly. 
				-> path_CLI contains the local path of your CLI. You dont have to change the default path if you are not on master and if you did not made any changes.
				-> share path is the path of the repertory that will be mapped. This line is essential if you are working with repertories that are not accessible by everyone.
				-> extensions is the extensions that the program handles. You can use only a few or even just one, but it should always be a list on the config file.

    -> Your files must be readable by other users. 
	
	-> If you use the WakeOnLan, you must enable it in the bios setting and in the parameters of your network card. You also must be on the same ETHERNET.

# What if you made a mistake anywhere in the process, or if it does not work on a client?

You can stop the server program whenever you want by using CTRL + C. It will also stop the clients if they were connected.
About the clients, that are windows services, there is a log file in 'program data\ CLI_automation_importer' named 'report'. It will help you identify the problem if it does not work.


# What if you want to use the program on one computer?

	->You can use the 'CAD_importer program', that will give you the same result (import all your files) but will not create a server

# How does the installer work??

The installer is designed for the cad importer client program. To start the server program, you just have to download it and run it in a powershell.
First, it is highly recommanded to start the installer in your powershell. It is mandatory to run it as an admin. You will have to run it twice, the second time while putting the cad importer client
program in the CLI automation importer repertory that was just created. Then, if you set up correctly the config file, you will be able to import cad whenever you want.

# About the arguments of the server program :

Mandatory arguments:

	--rep 	: It is the repertory where the CAD files are. 

Others argument: 

	-W 					: Enable the WakeOnLan. Takes two values : True / False.
	--excel_filename 	: If you want to chose the name of the excel that will have the results. If you put twice the same, it will create the report in the last sheet available. 	
	--id_workspace 		: The id of the workspace CAD files will be put in. If this argument is not filled. It will create a new workspace. 
	--json_mac			: Name of your json with the mac addresses in it. the default name is mac_addresses.json. You should avoid changing this parameter
	
# WakeOnLan

As previously said, if you want to use the wake on lan, you have to be on the same ethernet, and your computer need to be set up. After that, you will need the mac addresses of the clients. 
There is a program that will do it for you. For the clients 'get_mac_addresses_client.exe' required the following argument : --IP_host. It is the ip address of the computer that will receive the mac addresses. 
For the main computer, just launch the mac_addresses_host program. 

# some remarks

All your log files and excel files will be created in the CLI automation importer repertory and need to be there.

