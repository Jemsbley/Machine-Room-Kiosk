# 2022 README ( SEE 2021 README AS WELL )

# Intro

The Machining-ID system uses two apps (AdminApp and Keypad). The keypad app is used by the kiosk outside the machine room. Students can type in their machining id, select the machines they will use, then enter the room. The admin app is used to keep track of these sign ins. Mr. Seibert can app or remove students and their access to machines, as well as see who signed in and when. Additionally, Mr. Seibert can lock all students out of the machine room by activating a kill switch on his app. Both apps run on python, are visualized by Kivy, and communicate to a server in the mill via MySQL statements.

## The Server

In order to directly access the server, open the closet and turn on the monitor. Open the MySQL Workbench app. There you will see a server by the name of Localhost (then a bunch of numbers). Open that and type the password 'MILLDatabase2021!@#' The database has a bunch of tables that you can go through yourself ('select * from (tablename);') to figure out exactly what they are used for. Each student's name, ID, machine access, and times of entry are recorded in the database and accessed by the two apps. The killswitch is stored in the database as well. It is updated by the 'switch' stored procedure on the database. When the value 'activated' = 1, the machine room is locked, and when it = 0 it is open. All python functions that communicate with the server have the same outline of code, which you can see in its simplest form in the Checkserver() function. The server will always return a datastream in the form of a list (which is usually multidimensional). Changes can only be made to the server if the function has connection.commit() after all SQL statements (see log() function in keypad).

## Kivy

Kivy works in the simplest and most lightweight way possible. Every visible object that you can create must be restricted to what is called a GridLayout. the gridlayout is essentially a system to equally divide screen space into buttons, labels, textboxes, etc. For example, if you wanted to create two rows of 5 buttons each, you would set the gridlayout to 2 rows and 5 columns, then below that you would define each button, its id, and its function. If you wanted to make a single button it would just be a gridlayout of 1 row and 1 column. Each screen inherits its name from the class in the python file it runs along with (Ex: The AdminScreen class in the AdminApp runs along with the AdminScreen class in the Kivy file). The Kivy files themselves give you very little flexibility in code, but you can run any functions or access any variables in the parent file with the prefix 'root' (Ex: root.red will)

## Server Dependencies

(running these files on your own device requires you to be on the 'Hotspot' wifi network. Otherwise the code will repeatedly crash as it fails to access the server)

The list of machines (globalMachines) in both apps is entirely derived from the server, using the fillmachines() function. This means that by changing the name of any of the machines in the table: machines in the database will immediately change it on both the keypad and the adminapp. 

Both apps take advantage of allowedMachines() to determine which machines a student has access to. allowedMachines() returns a list of integers, each logically connected to each machine. For example (1,0,1,1,1,1,1,1) would have access to all machines but whichever is listed second (it will be listed second on the server as well as both apps, in the current version, this would be the laser cutter)

Both apps also must check the kill switch on the server using the checkServer() function (even though the admin app is what sets this value, it uses checkserver() to set its color appropriately on launch)

### Keypad Dependencies

The keypad uses the server to determine whether or not a student has access to the machine room (checkID), logging entrances to the room (log()), and signing people in out and (signIn() and signOut()). The rest of the code manipulates the data from these calls along with the Kivy

### AdminApp Dependencies

The Admin App uses the server to determine when machines were used (machsUsed), change Mr. Seibert's Password (changePass), retrieve Mr. Seibert's password (getPass), add, update, or remove students access to the machines (with those respective names), and populate the lists on the log and students pages (populate())

## Using Either App on Your Own Device

If you want to figure out what exactly EVERYTHING on the apps do, you can run them by connecting to the 'Hotspot' wifi network. You must comment out every line that is related to the raspberry pi (ctrl f 'gpio') on the keypad app. The keypad will run fine if you are connected to the wifi and those lines have been commented out. Try using the ID (13294) to test logging in (its not a real person so Seibert will know its you). The app will communicate with the server and create new entries, but not actually physically unlock the room (obviously).

The Admin app can only be opened if you bypass the password page. In order to do this, comment out the entire content of the getPass() function and replace it with (return 'test'). this will make the password 'test' and youll be able to get into the app. You will technically have permissions to change anything on the server and everyone's access to be careful what you click on.

## Help

If you need any help, the best person to contact is Jesse Andersen

PN: 973-309-3699
Preface the text by telling me you're working on the machine room because I'll probably ignore you otherwise









# 2021 README ( MAY BE OUTDATED )

# Machining-ID

Sign-in and administration system for the MILL's machining room


## Description

Machining-ID provides a simple sign-in/sign-out system for students using the MILL's machining room. When signing in students can view the machines they are allowed to use and indicate which machines they're using each time they enter. An administrative app is also available for Mr. Seibert, allowing him to manage students' access to the machines and monitor sign-in logs. Both apps are built primarily using the Kivy library for better support on touchscreen devices (especially for the sign-in keypad). 

## Getting Started

### Dependencies

* Windows: Packaged admin app is  available under 'Releases'
* If using the individual script files, you must download the requires packages listed in requirements.txt
    * Using a virtual environment is recomended
    * You must also manually add the credentials to connect to the database server in `credentials.py`

### Installing

* Windows: Simply download the latest release

* MacOS/Linux: Files can be manually downloaded and executed in terminal

### Executing program

* Windows: Launch the app, `adminApp.exe`
* MacOS/Linux: Run the python files in terminal


## Help

* If the keypad app does not launch, check to see if the MySQL server is running


## Authors

[Dhruv Pande](https://github.com/d-pande) (@Ganlas#8579)

[Ishaan Ghosh](https://github.com/22ghoshi) (@naahsi252#0008)

[Kylan Chen](https://github.com/Naylk) (@Kylan#2105)



