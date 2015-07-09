# Datalocker #

## Reason for this Repo ##

This repo contains every python file, Python, CSS, HTML, and JS page that was written to operate this application. Any changes that are made to the application are done inside this repository. This is the main location for the entire datalocker application.

## What it does ##

This application is to be tied together with a web form. It will accept the submission of a web form and turn the labels and the associated input fields and convert the data into JSON formatted records in a database. Then when you log access the web application it will display any 'locker' (web form) that you have access to or own. If you click on the 'locker' name it will direct you to all of the submissions for that specific 'locker'. If you want to see all of the data for a specific submission you can scroll through the records and find the exact submission and click on the timestamp. If you click that it will direct you to another page that has all the information from the web form in the same order as the form. It is a nice formatted way to recall the form submission. The application only allows you to see 'lockers' that you have ownership of or 'lockers' that are shared with you by another user in the system. Only the owner of the 'locker' has the ability to add or delete shares on a 'locker'.

## How to use this Repo ##

This repo is also automatically cloned onto the datalocker-vm whenever you run vagrant up from the root directory of the datalocker-vm repo. There wouldn't be any required work or installation of this software unless you wanted to add it to an existing VM or the bootstrap file failed to operate.

To manually clone down this repo:

You will want this repo to be on your virtual machine inside your project directory so cannot do this via windows unless you use [sourceTree](https://www.sourcetreeapp.com/) or another similar product.

### To clone from  a terminal window ###
* You must be inside your project directory
```
    git clone https://<your username>@bitbucket.org/psueduequity/datalocker.git
```

### To clone using sourceTree ###
* Open sourceTree
* In the top menu click Clone/New
* Click the Clone Repository Tab (if not already selected)
* In the Source Path / URL box paste the bitbucket url (example: https://<your username>@bitbucket.org/psueduequity/datalocker.git)
* In the Destination Path enter your django project directory
* Click the Clone button on the bottom

You should now have a cloned version of the datalocker application on your virtual machine.