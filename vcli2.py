from tkinter import filedialog; import tkinter as tk
from socket import *; from threading import *
from videoplayer import *
import pickle

Server = '172.16.40.4'
Port = 12345
filePath = 'c:\\Users\\Evan\\Downloads'

#Create socket
clientSocket = socket(AF_INET, SOCK_STREAM)

#Connect client to server
clientSocket.connect((Server, Port))

def PlayVideo(fileName):
    mainFrame.pack_forget()
    player = VideoPlayer(root)
    player.open_file(fileName)
    player.play_video()


def GetVideo(fileName, uploader):
    clientSocket.send('get'.encode())
    request = clientSocket.recv(1024).decode()
    if request == 'filename':
        clientSocket.send(fileName.encode())
    request = clientSocket.recv(1024).decode()
    if request == 'download':
        tempFile = filePath + 'temp-' + fileName
        with open(tempFile, 'wb') as file:
            while True:
                chunk = clientSocket.recv(1 << 20)
                if not chunk:
                    break
                file.write(chunk)
                if len(chunk) < (1 << 20):
                    break
        PlayVideo(tempFile)

def ListVideos():
    for widget in mainFrame.winfo_children():
        widget.pack_forget()
    clientSocket.send('list'.encode())
    sizeData = clientSocket.recv(1024)
    try:
        size = int(sizeData.decode().strip())
    except ValueError:
        print("Error: Received invalid size header")
        return
    buffer = b''
    while len(buffer) < size:
        data = clientSocket.recv(min(4096, size - len(buffer)))
        if not data:
            break
        buffer += data
    try:
        videolist = pickle.loads(buffer)
    except Exception as e:
        print("Error loading video list:", e)
        return
    if not videolist:
        emptyLabel = tk.Label(mainFrame, text="No videos available.")
        emptyLabel.pack(pady=10)
    for video in videolist:
        vButton = tk.Button(mainFrame, text=video + ' by ' + videolist[video],command=lambda v=video, u=videolist[video]: GetVideo(v, u))
        vButton.pack(pady=5)
    backButton = tk.Button(mainFrame, text='Back', command=MainScreen)
    backButton.pack(pady=10)

def MainScreen():
    root.title('Home')
    for widget in mainFrame.winfo_children():
        widget.pack_forget()

    welcomeLabel.pack()
    welcomeLabel.config(text='Welcome! Browse Videos or Upload a Video.')

    tk.Button(mainFrame, text='Browse Videos', command=ListVideos).pack(pady=5)
    tk.Button(mainFrame, text='Upload Video', command=UploadVideo).pack(pady=5)
    tk.Button(mainFrame, text='Delete Video').pack(pady=5)
    tk.Button(mainFrame, text='Log Out', command=LoginScreen).pack(pady=10)

def SendLoginInfo(userName, userPass):
    clientSocket.send('login'.encode())
    while True:
        request = clientSocket.recv(1024).decode()
        if request == 'username':
            clientSocket.send(userName.encode())
        elif request == 'password':
            clientSocket.send(userPass.encode())
        elif request == 'incorrect':
            welcomeLabel.pack()
            welcomeLabel.config(text='Username or Password is Incorrect')
            break
        elif request == 'login':
            MainScreen()
            break

def SendSignupInfo(userName, userPass):
    clientSocket.send('signup'.encode())
    while True:
        request = clientSocket.recv(1024).decode()
        if request == 'username':
            clientSocket.send(userName.encode())
        elif request == 'password':
            clientSocket.send(userPass.encode())
        elif request == 'reject':
            welcomeLabel.config(text='Username is Already Taken')
            break
        elif request == 'signup':
            LoginScreen()
            break

def LoginScreen():
    root.title('Log in')
    for widget in mainFrame.winfo_children():
        widget.pack_forget()

    userName = tk.StringVar()
    userPass = tk.StringVar()

    tk.Label(mainFrame, text='Enter Username:').pack(pady=2)
    tk.Entry(mainFrame, textvariable=userName).pack(pady=5)

    tk.Label(mainFrame, text='Enter Password:').pack(pady=2)
    tk.Entry(mainFrame, textvariable=userPass, show='*').pack(pady=5)

    tk.Button(mainFrame, text='Log In', command=lambda: SendLoginInfo(userName.get(), userPass.get())).pack(pady=5)

    tk.Label(mainFrame, text="Don't have an Account?").pack(pady=10)
    SignupButton.config(command=SignupScreen)
    SignupButton.pack()

def SignupScreen():
    root.title('Sign up')
    for widget in mainFrame.winfo_children():
        widget.pack_forget()

    userName = tk.StringVar()
    userPass = tk.StringVar()

    tk.Label(mainFrame, text='Choose Username:').pack(pady=2)
    tk.Entry(mainFrame, textvariable=userName).pack(pady=5)

    tk.Label(mainFrame, text='Choose Password:').pack(pady=2)
    tk.Entry(mainFrame, textvariable=userPass, show='*').pack(pady=5)

    SignupButton.pack(pady=5)
    SignupButton.config(command=lambda: SendSignupInfo(userName.get(), userPass.get()))

    tk.Label(mainFrame, text='Already have an Account?').pack(pady=10)
    loginButton.config(command=LoginScreen)
    loginButton.pack()


def UploadVideo():
    clientSocket.send('put'.encode())
    fileName = filedialog.askopenfilename(title='Select a Video File',filetypes=[('Video Files',"*.mp4;*.avi;*.mkv;*.mov"),('All Files','*.*')])
    file = open(fileName,'rb')
    while True:
        request = clientSocket.recv(1024).decode()
        if request == 'filename':
            fileShort = fileName.split('/')[-1]
            clientSocket.send(fileShort.encode())
        if request == 'reject':
            rejectLabel=tk.Label(mainFrame,text='A Video With That Name Already Exists.')
            rejectLabel.pack()
        if request == 'file':
            while chunk:=file.read(1 << 20):
                clientSocket.sendall(chunk)
            uploadLabel = tk.Label(mainFrame,text='File Uploaded succesfully')
            uploadLabel.pack()
            break
    file.close()


root = tk.Tk()
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()

root.title('Log in or Sign Up')
root.state('zoomed')

mainFrame = tk.Frame(root)
mainFrame.pack(pady=screenHeight / 3)

welcomeLabel = tk.Label(mainFrame, text='Welcome! Please Log in if you already have an account, or sign up to create one.')
welcomeLabel.pack()

loginButton = tk.Button(mainFrame, text='Log In', command=LoginScreen)
loginButton.pack(pady=5)

SignupButton = tk.Button(mainFrame, text='Sign Up', command=SignupScreen)
SignupButton.pack(pady=5)


root.mainloop()