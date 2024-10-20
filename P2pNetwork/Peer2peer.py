import socket
import threading
import ipaddress
import json
from P2pNetwork.TransactionPool import TransactionPool
from Wallet.Wallet import Wallet
from Blockchain.Block import Block

class PeerToPeer(TransactionPool):
    def __init__(self, difficulty, lock, pkey, max_hosts=5, chain=None, host='0.0.0.0', subnet='192.168.8.240/28', port=5678):
        super().__init__(lock)
        self.__host = host
        self.__port = port
        self.__sockets = []
        self.__lock = lock
        self.__max_hosts = max_hosts
        self.__subnet = subnet
        self.__shard_config = {"shard_1": []} # Only 1 shard at the beginning
        self.__pkey = pkey

        self.__difficulty = difficulty

        tmp_wallet = Wallet()
        for node in range(max_hosts):
            tmp_wallet.loadKey(f'keys/node{node + 1}.pem')
            self.__shard_config["shard_1"].append(tmp_wallet.getPublicKey())

        self.__chain = chain # Chain at current sharding epoch
        self.__chains = [] # Chains of previous sharding epochs 

        # Start listening thread
        self.listener_thread = threading.Thread(target=self._listen_for_connections)
        self.listener_thread.start()

    def getChainAtShardEpochX(self, x):
        if x >= len(self.__chains):
            return "err"
        return self.__chains[x]
    
    def getMyShardID(self):
        for shard_id, pkeys in self.__shard_config.items():
            if self.__pkey in pkeys:
                return shard_id
            
        return 'known_shard'

    def setShardConfig(self, shard_config):
        self.__shard_config = shard_config
        
        # Store current chain and reset current chain
        self.__chains.append(self.__chain.getBlockChain())
        self.__chain.resetChain(self.getMyShardID())

    def shameShard(self, pka, pkb):
        for shard_id, pkeys in self.__shard_config.items():
            if pka in pkeys and pkb in pkeys:
                return True
        
        return False
    
    def getShardConfig(self):
        return self.__shard_config

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
                msg = conn.recv(10000).decode()
                if msg and "setShardConfig" in msg:
                    print('Reconfiguring shards...')
                    message = json.loads(msg)
                    del message['setShardConfig']
                    self.setShardConfig(message)
                    
                    continue

                if msg:
                    message = json.loads(msg)
                    msg_type = json.loads(message['data'])['msg_type']
                    tmp_wallet = Wallet()

                    print('txs received!')

                    if msg_type == 'txs':
                        tmp_wallet.setPublicKey(json.loads(message['data'])['from'])
                        if self.shameShard(json.loads(message['data'])['from'], self.__pkey) and (tmp_wallet._verify(message['data'], message['sig'])) and not self._findTxs(msg):
                            self.addTxs(msg) # To pool
                            print('txs accepted!')
                            
                    if msg_type == 'block':
                        block = Block()
                        block.createFromStr(message['data'])
                        block.setSignature(message['sig'])
                        tmp_wallet.setPublicKey(block.getProducer())

                        print('block received!')

                        if self.shameShard(json.loads(message['data'])['producer'], self.__pkey) and tmp_wallet.verifyBlock(block):
                            # Check difficulty
                            if block.getHash()[:self.__difficulty] != '0'*self.__difficulty:
                                continue

                            # Check num of txs
                            # ...

                            #
                            if self.__chain.addBlock(msg):
                                print('block accepted!')
                                for txs in block.getTxsList():
                                    self.removeTxs(txs) # high cost
                        else:
                            print('block failed!')


            except Exception as e:
                print(f'Err reading msg. {e}')


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
                continue
        
    def send_message(self, message):
        self._broadcast(message)