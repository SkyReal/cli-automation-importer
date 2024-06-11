This program is designed to scan a repertory which contains CAD files, select them and put them in an XRCENTER, in a new workspace. 
It also measures the total time of the import and the time of import per files, and put it in an Excel file.

What do you need to make the program valid ? 

   -> You need to create this .json confil files
                               {
	                                "adresse_xrcenter": "",
                                  "adresse_cli": ""
                              }


adresse_xrcenter contains the path of the xrcenter on your computer.
adresse_cli contains the path of the cli.
In argument of the program, there is first the path of your repertory that will be scanned, and then the path of the json file.
# titre   
