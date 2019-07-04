import time
from tkinter import *
import tkinter.messagebox as tk
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    SETUP = 0
    PLAY = 1
    PAUSE = 2
    TEARDOWN = 3

    TESTING = 0

    # Initiation..
    def __init__(self, master, serveraddr, serverport, rtpport, filename):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
        self.createWidgets()
        self.serverAddr = serveraddr
        self.serverPort = int(serverport)
        self.rtpPort = int(rtpport)
        self.fileName = filename
        self.rtspSeq = 0
        self.sessionId = 0
        self.requestSent = -1
        self.teardownAcked = 0
        self.connectToServer()
        self.frameNbr = 0
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def createWidgets(self):
        """Build GUI."""
        # Create Setup button
        self.setup = Button(self.master, width=20, padx=3, pady=3)
        self.setup["text"] = "Preparando Setup"
        self.setup["command"] = self.setupMovie
        self.setup.grid(row=1, column=0, padx=2, pady=2)

        # Create Play button
        self.start = Button(self.master, width=20, padx=3, pady=3)
        self.start["text"] = "Reproduzir"
        self.start["command"] = self.playMovie
        self.start.grid(row=1, column=1, padx=2, pady=2)

        # Create Pause button
        self.pause = Button(self.master, width=20, padx=3, pady=3)
        self.pause["text"] = "Pausar"
        self.pause["command"] = self.pauseMovie
        self.pause.grid(row=1, column=2, padx=2, pady=2)

        # Create Teardown button
        self.teardown = Button(self.master, width=20, padx=3, pady=3)
        self.teardown["text"] = "Fechar janela"
        self.teardown["command"] =  self.exitClient
        self.teardown.grid(row=1, column=3, padx=2, pady=2)

        # Create a label to display the movie
        self.label = Label(self.master, height=25)
        self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5)

    def setupMovie(self):
        """Setup button handler."""
        if self.state == self.INIT:
            print("Botao Setup Selecionado .....")
            self.sendRtspRequest(self.SETUP)

    def exitClient(self):
        """Teardown button handler."""
        self.sendRtspRequest(self.TEARDOWN)
        self.master.destroy() # Close the gui window
        os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the cache image from video

    def pauseMovie(self):
        """Pause button handler."""
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.PAUSE)

    def playMovie(self):
        """Play button handler."""
        #print("Botao Play Selecionado .....", self.READY , self.state)
        self.state = 1
        if self.state == self.READY:
            #print("Entrou play....")
            # Create a new thread to listen for RTP packets
            threading.Thread(target=self.listenRtp).start()
            self.playEvent = threading.Event()
            self.playEvent.clear()
            self.sendRtspRequest(self.PLAY)

    def listenRtp(self):
        """Listen for RTP packets."""
        print("....................Try listening ...............")
        while True:
            try:
                data = self.rtpSocket.recv(20480)
                if data:
                    #print("Frame receieved : ")
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)

                    currFrameNbr = rtpPacket.seqNum()
                    print("---> Current Seq Number : " + str(currFrameNbr))

                    if currFrameNbr > self.frameNbr: # Discard the late packet
                        #print("Video on")
                        self.frameNbr = currFrameNbr
                        self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
            except:
                # Stop listening upon requesting PAUSE or TEARDOWN
                #if self.playEvent.isSet():
                    #break
                # Upon receiving ACK for TEARDOWN request,
                # close the RTP socket
                if self.teardownAcked == 1:
                    self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    self.rtpSocket.close()
                    break

    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()

        return cachename

    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        self.label.configure(image = photo, height=340)
        self.label.image = photo

    def connectToServer(self):
        """Connect to the Server. Start a new RTSP/TCP session."""
        self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.rtspSocket.connect((self.serverAddr, self.serverPort))
        except:
            print("ERRROR")
            #tkMessageBox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)

    def sendMessage(self, message):
        message = message.encode()
        self.rtspSocket.send(message)



    def sendRtspRequest(self, requestCode):
        """Send RTSP request to the server."""
        #-------------
        # TO COMPLETE
        #-------------
        print("Sending RTSP REQUEST To Sever ----",requestCode)

        # Setup request
        if requestCode == self.SETUP and self.state == self.INIT:
            threading.Thread(target=self.recvRtspReply).start()
            # Update RTSP sequence number.
            # ...
            self.rtspSeq =  1
            message = "SETUP " + str(self.fileName) + " RTSP/1.0\n"
            message = message +"CSeq: " + str(self.rtspSeq) + "\n"
            message = message + "Transport: RTP/UDP; client_port= " + str(self.rtpPort)
            print("Enviando " + str(message))
            #self.sendMessage(message)
            #self.rtspSeq = self.rtspSeq + 1
            # Write the RTSP request to be sent.
            # request = ...
            # Keep track of the sent request.
            # self.requestSent = ...
            self.requestSent = 0
            #self.recvRtspReply()
            # Play request
            self.rtspSocket.send(message.encode())
            #self.READY = 1

        elif requestCode == self.PAUSE and self.TESTING == 'stop':
            print("Command Play is working .... !!!")
            # Update RTSP sequence number.
            # ...
            self.rtspSeq = + 1
            # Write the RTSP request to be sent.
            # request = ...
            message = "PLAY " + str(self.fileName) + " RTSP/1.0\n"
            message = message + "CSeq: " + str(self.rtspSeq) + "\n"
            message = message + "Session: " + str(self.sessionId)

            # print("Enviando mensagem :",message)
            # self.sendMessage(message)
            self.rtspSocket.send(message.encode())
            self.requestSent = self.PLAY
            self.TESTING = 'play'

        elif (requestCode == self.PLAY and self.state == self.READY):

                print("Command Play is working .... !!!")
                # Update RTSP sequence number.
                # ...
                self.rtspSeq = + 1
                # Write the RTSP request to be sent.
                # request = ...
                message = "PLAY " + str(self.fileName) + " RTSP/1.0\n"
                message = message + "CSeq: " + str(self.rtspSeq) + "\n"
                message = message + "Session: " + str(self.sessionId)

                #print("Enviando mensagem :",message)
                #self.sendMessage(message)
                self.rtspSocket.send(message.encode())
                self.requestSent = self.PLAY




        elif requestCode == self.PAUSE and self.state == self.PLAYING:
            # Update RTSP sequence number.
            # ...
            self.rtspSeq = self.rtspSeq + 1
            # Write the RTSP request to be sent.
            # request = ...
            request = "PAUSE " + "\n" + str(self.rtspSeq)
            self.rtspSocket.send(request.encode())
            print('-' * 60 + "\nPAUSE request sent to Server...\n" + '-' * 60)
            # Keep track of the sent request.
            # self.requestSent = ...
            self.requestSent = self.PAUSE
            self.TESTING = 'stop'


        elif requestCode == self.TEARDOWN and not self.state == self.INIT:
            # Update RTSP sequence number.
            # ...
            self.rtspSeq = self.rtspSeq + 1
            # Write the RTSP request to be sent.
            # request = ...
            request = "TEARDOWN " + "\n" + str(self.rtspSeq)
            self.rtspSocket.send(request.encode())
            print('-' * 60 + "\nTEARDOWN request sent to Server...\n" + '-' * 60)
            # Keep track of the sent request.
            # self.requestSent = ...
            self.requestSent = self.TEARDOWN

            tk.askquestion('Fechar janela?','Deseja Fechara janela ?')

        else:
            return




    def recvRtspReply(self):
        """Receive RTSP reply from the server."""
        while True:
            reply = self.rtspSocket.recv(1024)
            if reply:
                print("\n--Menssage of the Server : ",reply)
                self.parseRtspReply(reply.decode("utf-8"))

            # Close the RTSP socket upon requesting Teardown
            if self.requestSent == self.TEARDOWN:
                self.rtspSocket.shutdown(socket.SHUT_RDWR)
                self.rtspSocket.close()
                print("Session close command Teardown !!!")
                break

    def parseRtspReply(self, data):
        print("Parsing Received Rtsp data...")

        """Parse the RTSP reply from the server."""
        lines = data.split('\n')
        seqNum = int(lines[1].split(' ')[1])

        # Process only if the server reply's sequence number is the same as the request's
        if seqNum == self.rtspSeq:
            session = int(lines[2].split(' ')[1])
            # New RTSP session ID
            if self.sessionId == 0:
                self.sessionId = session

            # Process only if the session ID is the same
            if self.sessionId == session:
                if int(lines[0].split(' ')[1]) == 200:
                    if self.requestSent == self.SETUP:
                        print("Updating RTSP state...")
                        # self.state = ...
                        self.state = self.READY
                        # Open RTP port.
                        # self.openRtpPort()
                        print("Setting Up RtpPort for Video Stream")
                        self.openRtpPort()

                    elif self.requestSent == self.PLAY:
                        self.state = self.PLAYING
                        print('-' * 60 + "\nClient is PLAYING...\n" + '-' * 60)

                    elif self.requestSent == self.PAUSE:
                        self.state = self.READY
                        # The play thread exits. A new thread is created on resume.
                        self.playEvent.set()

                    #TEARDOWN command
                    elif self.requestSent == self.TEARDOWN:
                        # self.state = ...

                        # Flag the teardownAcked to close the socket.
                        self.teardownAcked = 1

    def openRtpPort(self):
        """Open RTP socket binded to a specified port."""
        self.rtpSocket.settimeout(0.5)
        flag = False

        try:
            # self.rtpSocket.connect(self.serverAddr,self.rtpPort)
            self.rtpSocket.bind((self.serverAddr,self.rtpPort))  # WATCH OUT THE ADDRESS FORMAT!!!!!  rtpPort# should be bigger than 1024
            print("Bind RtpPort Success !!! ...")
            #tk._show()
            tk._show('Conection Status','Conection Successfuly Done, you are able to play the video!!!')
            flag = True
        except:
            flag = False

        #if (flag == False):
            #tk.showwarning('Connection Failed', 'Connection to rtpServer failed...')




    def handler(self):
        """Handler on explicitly closing the GUI window."""
        self.pauseMovie()
        if tk.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.exitClient()
        else:  # When the user presses cancel, resume playing.
            # self.playMovie()
            print("Playing Movie")
            threading.Thread(target=self.listenRtp).start()
            # self.playEvent = threading.Event()
            # self.playEvent.clear()
            self.sendRtspRequest(self.PLAY)


