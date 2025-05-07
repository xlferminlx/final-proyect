from socket import * 
from threading import *
import pickle; from datetime import *
import tkinter as tk; from tkinter import filedialog
import os

fileStorage = {}
userLoginInfo = {}
connections = []


def NewClient(clientSocket, address):
    global fileStorage
    global userLoginInfo
    global connections

    connections.append(clientSocket)
    currentUser = None

    while True:
        try:
            IncomingCommand = clientSocket.recv(1024).decode()
        except:
            break
        else:
            if IncomingCommand == 'login':
                clientSocket.send('username'.encode())
                userName = clientSocket.recv(1024).decode()
                clientSocket.send('password'.encode())
                userPass = clientSocket.recv(1024).decode()
                if userName in userLoginInfo and userLoginInfo[userName] == userPass:
                    currentUser = userName
                    clientSocket.send('login'.encode())
                else:
                    clientSocket.send('incorrect'.encode())

            elif IncomingCommand == 'signup':
                clientSocket.send('username'.encode())
                userName = clientSocket.recv(1024).decode()
                clientSocket.send('password'.encode())
                userPass = clientSocket.recv(1024).decode()
                if userName in userLoginInfo:
                    clientSocket.send('reject'.encode())
                else:
                    userLoginInfo[userName] = userPass
                    clientSocket.send('signup'.encode())

            elif IncomingCommand == 'put':
                if not currentUser:
                    continue
                clientSocket.send('filename'.encode())
                fileName = clientSocket.recv(1024).decode()
                if fileName in fileStorage:
                    clientSocket.send('reject'.encode())
                else:
                    clientSocket.send('file'.encode())
                    with open(filePath + fileName, 'wb') as file:
                        while True:
                            chunk = clientSocket.recv(1 << 20)
                            if not chunk:
                                break
                            file.write(chunk)
                            if len(chunk) < (1 << 20):
                                break
                    fileStorage[fileName] = currentUser
                    print(f"Uploaded: {fileName} by {currentUser}")

            elif IncomingCommand == 'list':
                data = pickle.dumps(fileStorage, -1)
                size_header = str(len(data)).encode().ljust(1024) 
                clientSocket.send(size_header)
                clientSocket.sendall(data)

            elif IncomingCommand == 'get':
                clientSocket.send('filename'.encode())
                fileName = clientSocket.recv(1024).decode()
                if fileName in fileStorage:
                    clientSocket.send('download'.encode())
                    with open(filePath + fileName, 'rb') as videofile:
                        while chunk := videofile.read(1 << 20):
                            clientSocket.sendall(chunk)


def SaveFiles():
    global fileStorage
    saveFile = open(filePath + 'backup' + datetime.now().strftime('%Y-%m-%d-%H%M%S') +'.txt','wb')
    pickle.dump(fileStorage, saveFile)
    saveFile.close()


def LoadFiles():
    global fileStorage
    fileName = filedialog.askopenfilename(title='Select Backup File to Load',filetypes=[('All Files','*.*')])
    loadFile = open(fileName,'rb')
    fileStorage = pickle.load(loadFile)


def SaveCredentials():
    with open(os.path.join(filePath, 'usercredentials.txt'), 'wb') as saveFile:
        pickle.dump(userLoginInfo, saveFile)


def LoadCredentials():
    global userLoginInfo
    try:
        with open(os.path.join(filePath, 'usercredentials.txt'), 'rb') as loadFile:
            userLoginInfo = pickle.load(loadFile)
    except:
        pass


def InputListener():
    while True:
        serverInput = input()
        if serverInput == 'save':
            SaveCredentials()
        elif serverInput == 'list':
            for file in fileStorage:
                print(f"{file}, Uploaded by - {fileStorage[file]}")
        elif serverInput.startswith('delete '):
            fileDelete = serverInput.removeprefix('delete ')
            if fileDelete in fileStorage:
                os.remove(os.path.join(filePath, fileDelete))
                del fileStorage[fileDelete]
        elif serverInput == 'close':
            for connection in connections:
                connection.close()
            SaveCredentials()
            serverSocket.close()
            break


def main():
    #Initiliazation
    global filePath
    filePath = 'c:\\Users\\Evan\\Downloads'
    Host = '0.0.0.0'
    Port = 12345
    LoadCredentials()
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((Host, Port))
    serverSocket.listen(5)
    print('Listening for clients to connect...')

    Thread(target=InputListener).start()
    Thread(target=lambda: tk.Tk().withdraw()).start()

    while True:
        try:
            connection, address = serverSocket.accept()
            print('Got connection from', address)
            Thread(target=NewClient, args=(connection, address)).start()
        except:
            break


#Start

    #Create Socket
serverSocket = socket(AF_INET, SOCK_STREAM)

if __name__ == '__main__':
    main()