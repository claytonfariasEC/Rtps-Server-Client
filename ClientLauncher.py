import sys
from tkinter import Tk
from Client import Client

if __name__ == "__main__":
    try:
        serverAddr = sys.argv[1] #"192.168.1.102"
        serverPort = sys.argv[2] # 3000
        rtpPort = sys.argv[3] #"3001"
        fileName = sys.argv[4] #"movie.Mjpeg"
    except:
        print("[Usage: ClientLauncher.py Server_name Server_port RTP_port Video_file]\n")

    root = Tk()
    # Create a new client
    app = Client(root, serverAddr, serverPort, rtpPort, fileName)
    app.master.title("RTPClient Player Clayton Edition")
    #pp.sendRtspRequest("testandooooooo")
    root.mainloop()
