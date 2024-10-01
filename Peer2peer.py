import socket
import threading
import ipaddress
from Blockchain.TransactionPool import TransactionPool

class PeerToPeer:
    def __init__(self, host='0.0.0.0', subnet='192.168.8.240/28', port=5678):
        self.__host = host
        self.__port = port
        self.__sockets = []
        self.__lock = threading.Lock()
        self.__max_hosts = 5
        self.__subnet = subnet
            
        # Transactionpool
        self.__txs_pool = TransactionPool()

        # Start listening thread
        self.listener_thread = threading.Thread(target=self.listen_for_connections)
        self.listener_thread.start()

    def getSockets(self):
        return self.__sockets
    
    def getTxsPool(self):
        return self.__txs_pool.getAll()
    
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Kết nối đến Google DNS
            local_ip = s.getsockname()[0]
        finally:
            s.close()

        return local_ip

    def listen_for_connections(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.bind((self.__host, self.__port))
        conn.listen(self.__max_hosts)
        
        print(f"Listening for connections on {self.__host} port {self.__port}...")

        while True:
            con, addr = conn.accept()
        
            self.__lock.acquire()
            try:
                if not self.is_connected(con):
                    print(f"Connection from: {con}")

                    self.__sockets.append(con)

                    # Start a new thread to listen for messages from this peer
                    threading.Thread(target=self.handle_peer, args=(con,)).start()
            finally:
                self.__lock.release()

    def handle_peer(self, conn):
        while True:
            try:
                message = conn.recv(1024).decode()
                if message:
                    self.__txs_pool.addTxs(message)
                else:
                    break
            except:
                break
        
        conn.close()
        self.__lock.acquire()
        self.__sockets.remove(conn)
        self.__lock.release()

    def is_connected(self, conn):
        target_ipA = conn.getpeername()[0]
        target_ipB = conn.getsockname()[0]

        try:
            for peer in self.__sockets:
                ipA = peer.getpeername()[0]
                ipB = peer.getsockname()[0]

                if (target_ipA == ipA and target_ipB == ipB) or (target_ipA == ipB and target_ipB == ipA):
                    return True
                
        except Exception as e:
            print(f"An error occurred: {e}")

        return False


    def broadcast(self, message):
        self.__lock.acquire()
        for peer in self.__sockets:
            try:
                print('sent!!!')
                peer.send(message.encode())
            except:
                pass
        self.__lock.release()

    def connect_to_peers(self):
        net = ipaddress.ip_network(self.__subnet)
        myIP = self.get_local_ip()

        for ip in net:
            if str(ip) == myIP:
                continue

            try:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((str(ip), self.__port))

                self.__lock.acquire()
                try:
                    if not self.is_connected(conn):
                        print("Connected to: ", conn)
                        self.__sockets.append(conn)

                        # Start a thread to listen for messages from this peer
                        threading.Thread(target=self.handle_peer, args=(conn,)).start()
                finally:
                    self.__lock.release()
                
            except Exception as e:
                #print('ip: ', ip, ' - err', e)
                continue
        
    def send_message(self, message):
        self.broadcast(message)