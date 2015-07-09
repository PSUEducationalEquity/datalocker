# Datalocker #

## Reason for this Repo ##

This repo contains every python file, Python, CSS, HTML, and JS page that was written to operate this application. Any changes that are made to the application are done inside this repository. This is the main location for the entire datalocker application.

## What it does ##

This application is to be tied together with a web form. It will accept the submission of a web form and turn the labels and the associated input fields and convert the data into JSON formatted records in a database. Then when you log access the web application it will display any `locker` (web form) that you have access to or own. If you click on the 'locker' name it will direct you to all of the submissions for that specific 'locker'. If you want to see all of the data for a specific submission you can scroll through the records and find the exact submission and click on the timestamp. If you click that it will direct you to another page that has all the information from the web form in the same order as the form. It is a nice formatted way to recall the form submission. The application only allows you to see 'lockers' that you have ownership of or 'lockers' that are shared with you by another user in the system. Only the owner of the 'locker' has the ability to add or delete shares on a 'locker'.

## How to use this Repo ##

This repo is also automatically cloned onto the datalocker-vm whenever you run vagrant up from the root directory of the datalocker-vm repo. There wouldn't be any required work or installation of this software unless you wanted to add it to an existing VM or the bootstrap file failed to operate.

To manually clone down this repo:

You will want this repo to be on your virtual machine inside your project directory so cannot do this via windows unless you use [sourceTree](https://www.sourcetreeapp.com/) or another similar product.

### To clone from  a terminal window ###
* You must be inside your project directory
```
    git clone https://<your username>@bitbucket.org/psueduequity/datalocker.git
```

### To clone using SourceTree ###
* Open 'SourceTree'
* In the top menu click 'Clone/New'
* Click the 'Clone Repository' Tab (if not already selected)
* In the Source Path / URL box paste the bitbucket url '(example: https://<your username>@bitbucket.org/psueduequity/datalocker.git)'
* In the Destination Path enter your django project directory
* Click the Clone button on the bottom

You should now have a cloned version of the datalocker application on your virtual machine.

### Accessing the web application ###
* Open the terminal to your VM
* Type 'datalocker' press 'ENTER'
* Type 'djserve' press 'ENTER'
    * This runs the webserver allowing you to access the webpage
* Open a browser of choice
* The VM is setup to run with the ip of '10.18.55.20' on port '8000'
* In the address bar type '10.18.55.20:8000/datalocker'
    * This will bring you to the DataLocker homepage which should show nothing because you aren't logged in. You will have to log in first with one of the users that were created by the fixture. You can find one by navigating to the fixtures folder and looking in the yaml file named dev-users.yaml.
* Once you have a user and log in you can click on any submissions that you have if any and you can explore the application.

### Adding your own data to the database ###

** Note: Anytime you destroy the database or the VM the data you add here will not be saved. In order to keep data every time you reload the database or run the 'dataBaseBuild.sh' script you will want to add any data the correct fixtures file.

* Open putty and connect to your VM or use the terminal inside the VM, you will need to be on the VM to run these commands.
run the following commands and in order to add a locker with a submission

```
Username: vagrant
Password: vagrant

datalocker
djserve

```
* Those commands will log you into the VM and also run the webserver now what you want to do is go to '10.18.55.20:8000/datalocker/admin' and log in with one of the users from the fixtures file. From here you will be redirected to the app with the test data loaded. You can go back up in the url and type '10.18.55.20:8000/datalocker/admin' in again and you will be at the admin site where you can add and delete records from the table.


** Ultimately you will still want to add data in the fixtures for test because then it will always upload. The format in the fixtures is how the database needs it to read correctly so copy and pasting would be the best way to add fixtures and alter the data in the fields.