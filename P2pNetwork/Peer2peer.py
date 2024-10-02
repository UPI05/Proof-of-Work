import socket
import threading
import ipaddress
from P2pNetwork.TransactionPool import TransactionPool

class PeerToPeer(TransactionPool):
    def __init__(self, max_hosts=5, chain=None, host='0.0.0.0', subnet='192.168.8.240/28', port=5678):
        super().__init__()
        self.__host = host
        self.__port = port
        self.__sockets = []
        self.__lock = threading.Lock()
        self.__max_hosts = max_hosts
        self.__subnet = subnet

        self.__chain = chain
            
        # Start listening thread
        self.listener_thread = threading.Thread(target=self._listen_for_connections)
        self.listener_thread.start()

    def getSockets(self):
        return self.__sockets
            
    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Kết nối đến Google DNS
            local_ip = s.getsockname()[0]
        finally:
            s.close()

        return local_ip

    def _listen_for_connections(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.bind((self.__host, self.__port))
        conn.listen(self.__max_hosts)
        
        print(f"Listening for connections on {self.__host} port {self.__port}...")

        while True:
            con, addr = conn.accept()
        
            self.__lock.acquire()
            try:
                if not self._is_connected(con):
                    print(f"Connection from: {con}")

                    self.__sockets.append(con)

                    # Start a new thread to listen for messages from this peer
                    threading.Thread(target=self._handle_peer, args=(con,)).start()
            finally:
                self.__lock.release()

    def _handle_peer(self, conn):
        while True:
            try:
                message = conn.recv(10000).decode()
                if message:
                    if 'producer' in message:
                        # Verify signature ...
                        # code here
                        self.__lock.acquire()
                        if self.__chain.addBlock(message):
                            print('Block received!')
                            # We also need to delete these txs from txs pool

                        self.__lock.release()

                    else:
                        self.addTxs(message) # To pool
                else:
                    break
            except:
                break
        
        conn.close()
        self.__lock.acquire()
        self.__sockets.remove(conn)
        self.__lock.release()


    # Vì khi node chạy lên, nó vừa nghe vừa connect nên sẽ có 2 connections cho mỗi cặp node, do đó để tối ưu thì cần check để
    # giảm bớt 1 connection, tuy nhiên đang bị lỗi vì xử lý đa luồng nên bị mất connection
    def _is_connected(self, conn):
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


    def _broadcast(self, message):
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
        myIP = self._get_local_ip()

        for ip in net:
            if str(ip) == myIP:
                continue

            try:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((str(ip), self.__port))

                self.__lock.acquire()
                try:
                    if not self._is_connected(conn):
                        print("Connected to: ", conn)
                        self.__sockets.append(conn)

                        # Start a thread to listen for messages from this peer
                        threading.Thread(target=self._handle_peer, args=(conn,)).start()
                finally:
                    self.__lock.release()
                
            except Exception as e:
                #print('ip: ', ip, ' - err', e)
                continue
        
    def send_message(self, message):
        self._broadcast(message)