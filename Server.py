import sys, socket
from ServerWorker import Server_Class

class Server:
    def main(self):
        #SERVER_PORT = 3000
        try:
            SERVER_PORT = int(sys.argv[1])
            rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            rtspSocket.bind(('', SERVER_PORT))
            rtspSocket.listen(5)
        except:
            print("[Usage: Server.py Server_port]\n")

        # Receive client info (address,port) through RTSP/TCP session
        while True:
            print("Waiting Clients ...")
            clientInfo = {}  #dicionario
            clientInfo['rtspSocket'] = rtspSocket.accept()
            client = Server_Class(clientInfo)
            client.run()
            client.recvRtspRequest()

if __name__ == "__main__":
    (Server()).main()


