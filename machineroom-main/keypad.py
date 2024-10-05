#globalMachines = ['Chop Saw', 'Laser Cutter', 'Bandsaw', 'Sanding Belt', 'Drill Press', 'Heat Gun', 'Dremels / Drills', 'Soldering']
globalMachines = []

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.uix.screenmanager import FadeTransition

import credentials as creds #file with db credentials
import pymysql.cursors

import time
from datetime import datetime
import threading

# import RPi.GPIO as GPIO
# from time import sleep
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(11, GPIO.OUT)
# Connecting to the Database
print("\033[96m" + "made it past imports! connecting to kiosk..." + "\033[0m")
try: 
    connection = pymysql.connect(host=creds.dbhost,
                             user=creds.dbuser,
                             password=creds.dbpass,
                             database=creds.dbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.Cursor)
    print("\033[1m\033[92m" + "connected to kiosk!" + "\033[0m")
except: 
    print("\x1b[1;25;37;41m" + "failed to connect." + "\033[0m")
    print("\033[4m\033[4m\033[1m\033[94m" + "connection debug info:" + "\033[0m\033[94m")
    print("host: " + creds.dbhost)
    print("user: " + creds.dbuser)
    print("password: " + creds.dbpass)
    print("dbname: " + creds.dbname)
    print("\033[0m")
    exit()
def fillmachines(): #populates machines list based on the server
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            machs = []
            cursor.execute("select machine from machines") 
            result = cursor.fetchall()
            for l in result:
                machs.append(l[0].title().replace("_"," "))
            return machs

def allowed_machines(id): #returns list of machine IDs that a student can use
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            machs = []
            cursor.execute("select mach_id from students_machines where sid="+id+" and can_use=1") 
            result = cursor.fetchall()
            if not result:
                print("Invalid ID")
                return -1
            for l in result:
                machs.append(l[0]) #being stored as ints
            return machs

def log(id, machs): #logs a student entering the room given an id and list of machines
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("insert into log (sid, time_in) values ("+str(id)+", '"+timestamp+"')")
            connection.commit()
            for m in machs:
                cursor.execute("insert into log_machines (time_in, machine_id) values ('"+timestamp+"', "+str(m)+")")
                connection.commit()

def checkID(id): #need to pass in id as a string
    if(int(id) == 00000):
        App.get_running_app().stop()
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("select exists(select * from students where student_id="+id+" and hide=0)")
            r = cursor.fetchall()
            return bool(r[0][0]) #returns true if student is in students and not hidden

def signOut(id): #signs out a student given their ID, only updates last entry in log
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("SELECT time_in FROM log l1 WHERE sid = "+str(id)+" and time_in = (SELECT MAX(time_in) FROM log l2 WHERE l1.sid = l2.sid) ORDER BY sid, time_in;")
            result = cursor.fetchall()
            if not result:
                return False
            r = result[0][0]
            cursor.execute("update log set time_out = '"+timestamp+"' where sid = "+str(id)+" and time_in = '"+str(r)+"';")
            connection.commit()
            return True

#def checkServer(): make it check if server is open
                       
def checkServer():
    connection.ping(True)
    with connection:
        with connection.cursor() as cursor:
            machs = []
            cursor.execute("select activated from kill_switch") 
            result = cursor.fetchall()
            for l in result:
                return l[0] == 0

class IDScreen(Screen):
    id_label = ObjectProperty() #make id text accessible here
    curr_id = ''
    numid = ''
    def on_enter(self, *args):
        self.id_label.text = 'ID: '
        self.instructionsText = 'Enter your Student ID'
        globalMachines = fillmachines()
        return super().on_enter(*args)

    def updateID(self, key):
        if (key.isnumeric() and len(self.id_label.text) < 9): #add only 5 numbers
            self.id_label.text += '*'
            self.numid += key
        elif (key == 'Delete' and len(self.id_label.text) > 4): #don't delete 'ID: '
            self.id_label.text = self.id_label.text[:-1]
            self.numid = self.numid[:-1]
        elif (key == 'Clear'):
            self.id_label.text = 'ID: '
            self.numid = ''

    def signIn(self):
        id = self.numid
        if checkServer():
            if (len(id) == 5) and checkID(id) and allowed_machines(id) != -1:
                    IDScreen.curr_id = id
                    self.manager.current = 'machine' #switch screen
            else:
                self.ids.instructions.text = 'Invalid ID' 
                t = threading.Timer(3.0, lambda: IDScreen.resetInstructions(self))
                t.start()
        else:
           self.ids.instructions.text = "Someone did something wrong \nand Seibert's mad >:(" 
           t = threading.Timer(3.0, lambda: IDScreen.resetInstructions(self))
           t.start() 
        self.id_label.text = 'ID: '
        self.numid = ''

    def signOut(self):
        id = self.numid
        if (len(id) == 5 and checkID(id)):
            if not signOut(id):
                self.ids.instructions.text = 'Sign In Idiot'
            else:
                self.ids.instructions.text = 'Signed Out!'
                self.id_label.text = 'ID: '
                self.numid = ''
        else:
            self.ids.instructions.text = 'Invalid ID'
            self.id_label.text = 'ID: '
            self.numid = ''
        t = threading.Timer(3.0, lambda: IDScreen.resetInstructions(self))
        t.start()
                
    
    def resetInstructions(self):
        self.ids.instructions.text = 'Enter your Student ID'



class MachineScreen(Screen):
    red = [1, 0, 0, 1]
    green = [0, 1, 0, 1]
    black = [0, 0, 0, 0]
    white = [1, 1, 1, 1]
    gray = [1, 1, 1, 0.5]
    status = [red, green]

    machines = fillmachines()

    def on_pre_enter(self, *args):
        allowedMachs = allowed_machines(IDScreen.curr_id)
        for id in self.ids:
            if id.isnumeric():
                if int(id) in allowedMachs:
                    self.ids[id].background_color = MachineScreen.status[0]
                    self.ids[id].color = MachineScreen.white
                else:
                    self.ids[id].disabled = True
        return super().on_pre_enter(*args)
    
    def toggleColor(self, id, currColor):
        if currColor in MachineScreen.status:
            self.ids[str(id)].background_color = MachineScreen.status[1 - MachineScreen.status.index(currColor)]

    def sendMachines(self):
        selectedMachines = []
        for id in self.ids:
            if self.ids[id].background_color == MachineScreen.status[1]:
                selectedMachines.append(int(id))
        log(IDScreen.curr_id, selectedMachines)
        self.manager.current = 'confirmation'

    def on_leave(self, *args):
        for id in self.ids:
            self.ids[id].background_color = MachineScreen.black
            self.ids[id].color = MachineScreen.black
            self.ids[id].disabled = False
        return super().on_leave(*args)

class ConfirmationScreen(Screen):
    def on_enter(self, *args):
         self.t = threading.Timer(3.0, lambda: ConfirmationScreen.goToID(self))
         self.t.start()

        #  pwm=GPIO.PWM(11, 50)
        #  pwm.start(0)
        #  pwm.ChangeDutyCycle(2.5)
        #  time.sleep(0.185)
        #  pwm.ChangeDutyCycle(5.9)
        #  time.sleep(0.2)
        #  pwm.stop()

         return super().on_enter(*args)
    
    def goToID(self):
        self.manager.current = 'ID'

    def on_leave(self, *args):
        self.t.cancel()
        return super().on_leave(*args)

class KeypadApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        sm.add_widget(IDScreen(name = 'ID'))
        sm.add_widget(MachineScreen(name = 'machine'))
        sm.add_widget(ConfirmationScreen(name = 'confirmation'))
        return sm

if __name__ == "__main__":
    #Window.maximize() #if you want you can uncomment this but it is unnecessary
    KeypadApp().run()