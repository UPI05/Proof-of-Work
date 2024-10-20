from flask import Flask, jsonify, request
import time
import json
import os
from Wallet.Wallet import Wallet
from P2pNetwork.Peer2peer import PeerToPeer
from Blockchain.Blockchain import Blockchain
import threading


lock = threading.Lock()

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

def triggerMinning(dif=4, max_txs_per_block=5):
    while True:
        status, txs_list = p2p.getTxsList(max_txs_per_block)
        preHash = chain.getLastBlockHash()

        if not status: # not enough txs
                continue
        
        for nOnce in range(0, 10**8): # Maybe larger
            if preHash != chain.getLastBlockHash(): # a new block received!
                break

            block = wallet.createBlock(preHash, txs_list, nOnce)
            hash = block.getHash()
            print(hash)
            if (hash[:dif] == '0'*dif): # Difficulty with 0s
                print('Found')
                # Save to blockchain before broadcast
                block_str = json.dumps({"data": block.getBlock(), "sig": block.getSignature()})
                
                if chain.addBlock(block_str):
                    print('block sent!')
                    p2p.send_message(block_str)
                    for txs in block.getTxsList():
                        p2p.removeTxs(txs)
                break


@app.route('/getShardConfig', methods=['GET'])
def getShardConfig():
    return jsonify(p2p.getShardConfig())

@app.route('/setShardConfig', methods=['POST'])
def setShardConfig():
    print('Reconfiguring shards...')
    data = request.get_json()
    p2p.send_message(json.dumps(data))
    del data['setShardConfig']
    p2p.setShardConfig(data)
    return jsonify({"status": 200})

@app.route('/getChainAtShardEpochX', methods=['GET'])
def getChainAtShardEpochX():
    epoch = int(request.args.get('epoch'))
    return jsonify(p2p.getChainAtShardEpochX(epoch))


### MAIN ###
if __name__ == "__main__":

    difficulty = 4 # num of 0s
    max_hosts = 3 # num of nodes

    # Blockchain
    chain = Blockchain(lock=lock)

    # Wallet
    wallet = Wallet()
    node_id = os.getenv('NODE')
    print(f'NODE: {node_id}')
    wallet.loadKey(f'keys/{node_id}.pem')
    print(f'PKey: {wallet.getPublicKey()}')

    # P2p network
    p2p = PeerToPeer(difficulty=difficulty, lock=lock, pkey=wallet.getPublicKey(), max_hosts=max_hosts, chain=chain, subnet='192.168.8.224/27')
    time.sleep(1)  # Ensure the listener is ready
    p2p.connect_to_peers()

    # Minning
    minning_thread = threading.Thread(target=triggerMinning, args=(difficulty, 6,))
    minning_thread.start()

    # API server
    app.run(debug=False, port=5679, host='0.0.0.0')

