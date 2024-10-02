from flask import Flask, jsonify, request
import time
import json
from Wallet.Wallet import Wallet
from P2pNetwork.Peer2peer import PeerToPeer
from Blockchain.Blockchain import Blockchain
import threading


### API ###
app = Flask(__name__)

@app.route('/api', methods=['GET'])
def get_data():
    
    return jsonify({'@': 'Hieu Vo'})

@app.route('/createTxs', methods=['POST'])
def createTxs():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    txs = wallet.createTxs(data.get('to'), data.get('tokens'))

    message = json.dumps({"data": txs.getTxs(), "sig": txs.getSignature()})

    # Save to mempool before broadcast
    p2p.addTxs(message)
    p2p.send_message(message)

    return jsonify({'status': 200})


@app.route('/getBlockchain', methods=['GET'])
def getBlockchain():
    return jsonify({
        "Blockchain": chain.getBlockChain()
    })

@app.route('/getTxsPool', methods=['GET'])
def getTxsPool():
    pool = p2p.getAllTxs()
    res = []
    while pool:
        res.append(json.loads(pool.popleft()))

    return jsonify({
        "txs_list": res
    })

@app.route('/triggerMinning', methods=['GET'])
def triggerMinning():
    # Mine a new block
    max_txs_per_block = 5
    status, txs_list = p2p.getTxsList(max_txs_per_block)
    preHash = chain.getLastBlockHash()

    if not status:
            return jsonify({'status': 500, 'msg': 'Txs not enough.'})
    
    for nOnce in range(0, 10**8): # Maybe larger
        block = wallet.createBlock(preHash, txs_list, nOnce)        
        hash = block.getHash()
        print(hash)
        if (hash[:4] == '0'*4): # Difficulty with 2 0s
            print('Found')
            # Save to blockchain before broadcast
            lock = threading.Lock()
            block_str = json.dumps({"data": block.getBlock(), "producer_sig": block.getSignature()})
            
            lock.acquire()
            if chain.addBlock(block_str):
                p2p.send_message(block_str)
            
            lock.release()

            break
    
    return jsonify({'status': 200})

### MAIN ###
if __name__ == "__main__":
    # Blockchain
    chain = Blockchain()

    # Wallet
    wallet = Wallet()
    wallet.loadKey() # Or you can genKey()

    # P2p network
    p2p = PeerToPeer(max_hosts=5, chain=chain)
    time.sleep(1)  # Ensure the listener is ready
    p2p.connect_to_peers()

    # API server
    app.run(debug=False, port=5679, host='0.0.0.0')


    # Cleanup and close all connections
    #for peer in p2p.sockets:
    #    peer.close()
