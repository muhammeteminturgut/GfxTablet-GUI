from tkinter import ttk
from tkinter import *
from ttkthemes import ThemedTk
from tkinter import messagebox
import socket, subprocess, webbrowser, threading, os, signal, time, requests

class GfxTabletGui:
    def __init__(self):
        self.main_window=ThemedTk(theme="breeze",background=True)
        #CenterScreen(self.main_window)
        self.main_window.protocol("WM_DELETE_WINDOW", lambda: self.main_window.iconify())
        self.main_window.resizable(False,False)
        self.main_window.title("GfxTablet GUI 1.0")
        #Status Group
        self.main_group=ttk.LabelFrame(self.main_window,text="Server Status",width=20)
        ##Server Hostname
        ttk.Label(self.main_group,text="Server Name: ",width=25).pack(padx=10,pady=(10,0),anchor="w")
        self.lbl_server_name=ttk.Label(self.main_group,text="NaN")
        self.lbl_server_name.pack(padx=(30,0),anchor="w")
        ##Server IP
        ttk.Label(self.main_group,text="Server IP: ").pack(padx=10,pady=(10,0),anchor="w")
        self.lbl_server_ip=ttk.Label(self.main_group,text="NaN")
        self.lbl_server_ip.pack(padx=(30,0),anchor="w")
        ##Screen Resolution
        ttk.Label(self.main_group,text="Selected Screen: ").pack(padx=10,pady=(10,0),anchor="w")
        self.lbl_screen_resolution=ttk.Label(self.main_group,text="NaN")
        self.lbl_screen_resolution.pack(padx=(30,0),anchor="w")
        ##Status
        ttk.Label(self.main_group,text="Status: ").pack(padx=10,pady=(10,0),anchor="w")
        self.lbl_status=ttk.Label(self.main_group,text="Waiting")
        self.lbl_status.pack(padx=(30,0),anchor="w")
        ##Refresh Button
        self.btn_refresh=ttk.Button(self.main_group,text="Refresh", command=self.refresh)
        self.btn_refresh.pack(pady=(20,5))
        ##Help Button
        self.btn_help=ttk.Button(self.main_group,text="Help",command=self.help)
        self.btn_help.pack(pady=(5,5)) 
        ##About Button
        self.btn_about=ttk.Button(self.main_group,text="About",command=self.show_about)
        self.btn_about.pack(pady=(5,5))        
        ##Exit Button
        self.btn_close=ttk.Button(self.main_group,text="Quit",command=self.exit_program)
        self.btn_close.pack(pady=(5,5))
        ##Download APK
        self.lbl_down_apk=Label(self.main_group,text="Download GfxTablet\nAndroid Package",fg="blue", font="Verdana 9 underline",cursor="hand2")
        self.lbl_down_apk.bind("<1>",self.down_apk)
        self.lbl_down_apk.pack(pady=5) 
        #End Status Group
        self.main_group.pack(expand=False,fill="both",padx=(10,5),pady=10,side="left")
        #Log Group
        self.log_group=ttk.LabelFrame(self.main_window,text="Logs")
        ##Log Text
        self.txt_log=Text(self.log_group,width=50,bg="white",relief="solid", font=("Verdana", 10))
        self.txt_log.pack(expand=True,fill="both",padx=5,pady=5,side="left")
        self.txt_scrollbar = ttk.Scrollbar(self.log_group, command=self.txt_log.yview)
        self.txt_log.config(yscrollcommand=self.txt_scrollbar.set)
        self.txt_scrollbar.pack(expand=True,fill="y",side="left")
        #End Log Group
        self.log_group.pack(expand=True,fill="both",padx=(10,5),pady=10,side="right")
        self.load_values()
        threading.Thread(target=self.connect_cli).start()
        #Check Sudo
        if not os.geteuid() == 0:
            self.main_window.withdraw()
            messagebox.showerror("Error","You need root permissions to using GfxTablet GUI")
            exit()
        self.center_screen(self.main_window)
        self.main_window.mainloop()
    
    def load_values(self):
        self.lbl_server_name.config(text=self.get_server_name())
        self.lbl_server_ip.config(text=self.get_server_ip())
        self.lbl_screen_resolution.config(text=self.get_screen_resolution().decode("utf-8").rstrip("\n"))

    def get_server_name(self):
        return socket.getfqdn()
    
    def get_screen_resolution(self):
        return subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]

    def get_server_ip(self):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            conn.connect(('8.8.8.8', 1))
            return conn.getsockname()[0]
        except:
            return "No Network Connection"
    
    def connect_cli(self):
        list_files = os.listdir(os.curdir)
        if "networktablet" in list_files:
            subprocess.check_call(['chmod','a+x','./networktablet'],cwd=os.path.dirname(os.path.realpath(__file__)))
            self.gfx_process = subprocess.Popen(['./networktablet'], stdout=subprocess.DEVNULL,shell=True,cwd=os.path.dirname(os.path.realpath(__file__)))
            self.log_insert("Starting gfxtablet.")
            time.sleep(5)
            try:
                self.gfx_result = subprocess.check_output(['xinput', 'list'])
            except:
                self.gfx_result = subprocess.check_output(['libinput', 'list-devices']) #For Arch and Wayland
            if not self.gfx_result.decode(encoding="utf-8").find("Network Tablet") == -1:
                self.log_insert("Gfxtablet input driver is ready!")
                self.log_insert("Now you can connect to "+self.lbl_server_ip["text"]+" ip address from your Android device.")
                self.lbl_status["text"]="Ready"
            else:
                self.log_insert("Gfxtablet input driver was not found.")
        else:
            self.log_insert("Gfxtablet not found.")
            self.btn_refresh["state"]="disabled"
            try:
                downloadUrlGet = requests.get("https://github.com/rfc2822/GfxTablet/releases/download/android-app-1.4-linux-driver-1.5/networktablet")
                with open('networktablet', 'wb') as newFile:
                    newFile.write(downloadUrlGet.content)
                self.log_insert("Downloading...")
                self.log_insert("Gfxtablet has been downloaded successfully.")
                self.btn_refresh["state"]="normal"
                self.refresh()
            except:
                self.log_insert("No Network Connection.")

    def help(self): #For running xdg-open without root. This is bad code.
        pid = os.fork()
        if pid == 0:
            try:
                self.btn_help["state"]="disabled"
                os.setuid(1000)
                webbrowser.open("https://rfc2822.github.io/GfxTablet/")
            finally:
                os._exit(0)
                self.btn_help["state"]="normal"
    
    def down_apk(self,event): #For running xdg-open without root. This is bad code.
        pid = os.fork()
        if pid == 0:
            try:
                self.lbl_down_apk.unbind("<1>")
                os.setuid(1000)
                webbrowser.open("https://github.com/rfc2822/GfxTablet/releases/download/android-app-1.4-linux-driver-1.5/gfxtablet_1_4.apk")
            finally:
                os._exit(0)
                self.lbl_down_apk.bind("<1>",self.down_apk)

    def refresh(self):
        try:
            os.killpg(os.getpgid(self.gfx_process.pid), signal.SIGINT)
        except:
            pass
        finally:
            self.lbl_status["text"]="Waiting"
            self.log_insert("Refreshing...")
            self.load_values()
            threading.Thread(target=self.connect_cli).start()

    def log_insert(self,text):
        self.txt_log.config(state="normal")
        self.txt_log.insert(END, text + '\n')
        self.txt_log.config(state="disabled")

    def center_screen(self,win):
        win.update_idletasks()
        width = win.winfo_width()
        frm_width = win.winfo_rootx() - win.winfo_x()
        win_width = width + 2 * frm_width
        height = win.winfo_height()
        titlebar_height = win.winfo_rooty() - win.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = win.winfo_screenwidth() // 2 - win_width // 2
        y = win.winfo_screenheight() // 2 - win_height // 2
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        win.deiconify()

    def show_about(self):
        messagebox.showinfo("About Gfxtablet GUI","gfxtablet 1.4\nAuthor: Ricki Hirner hirner@bitfire.at\n\nGfxtablet GUI 1.0\nAuthor: Muhammet Emin TURGUT m.emin@protonmail.com") 
    
    def exit_program(self):
        try:
            os.killpg(os.getpgid(self.gfx_process.pid), signal.SIGINT)
        except:
            pass
        os._exit(0)

if __name__ == '__main__':
    GfxTabletGui()
