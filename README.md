# What is the purpose of this program?

There are two parts for this program:
	A 'host server' program which is designed for scanning a repertory containing CAD files, opening a temporary server that is going to send the paths of the CAD files to every computer that has started the 'client' program. Then, it get the time of import of every CAD files and write them in an Excel file for futur reviews.
 	A 'client' program conceived to get the paths of the CAD files and import them into a XRCenter.


 # What do you need to make the program valid ?

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


	-> To work, the repertory containing the CAD file must be accessible for all the computers that start the client program

# What if you want to use the program on one computer?
	->You can use the 'CAD_importer program', that will give you the same result (import all your files) but will not create a server
