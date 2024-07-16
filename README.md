# What is the purpose of this program?

There are two parts for this program:
	A 'host server' program which is designed to scan a repertory containing CAD files, opening a temporary mapping that is going to send the paths of the CAD files to every computer that has started the 'client' program. Then, it get the time of import of every CAD files and write them in an Excel file for futur reviews.
 	A 'client' program conceived to get the paths of the CAD files and import them into a XRCenter.


 # What do you need to make the program valid ?
	-> First, you must be on the same network. 
	
   	-> You need to create this .json confil files
                            	   {
                           	       "adresse_cli": ""
                          	    }


	adresse_cli contains the path of the cli.

	-> You need to install the openpyxl library on your 'host' computer 
 
	 For the 'host server'
	 	-> In argument of the python function, there is first the path of the repertory that you want to scan and then the json file that we precendtly talked about
	  For the 'client' 
	  	-> In argument of the python function, there is first the path of the repertory that you want to scan and then the json file that we precendtly talked about


	-> To work, the repertory containing the CAD file must be accessible for all the computers that started the client program. It will work if it is a shared repertory and if you put the credentials of a person with access to this repertory

# What if you made a mistake anywhere in the process, or if it does not work on a client?

You can stop the server program whenever you want by using CTRL + C. It will also stop the clients.
About the clients, that are windows services, there is a log file in 'program data\ CLI_automation_importer' named 'report'. It will help you identify the problem.


# What if you want to use the program on one computer?
	->You can use the 'CAD_importer program', that will give you the same result (import all your files) but will not create a server
