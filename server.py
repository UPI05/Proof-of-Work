from Wallet.Wallet import Wallet
from flask import Flask, jsonify, request
import time
import json
from Peer2peer import PeerToPeer

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

    p2p.send_message(json.dumps({"data": txs.getTxs(), "sig": txs.getSignature()}))

    return jsonify({'status': 200})


@app.route('/getTxsPool', methods=['GET'])
def getTxsPool():
    pool = p2p.getTxsPool()
    res = []
    while pool:
        res.append(json.loads(pool.popleft()))

    return jsonify({
        "txs_list": res
    })

### MAIN ###
if __name__ == "__main__":
    ## P2p network
    p2p = PeerToPeer()
    time.sleep(1)  # Ensure the listener is ready
    p2p.connect_to_peers()

    # Wallet
    wallet = Wallet()
    wallet._loadKey() # Or you can genKey()

    # API server
    app.run(debug=False, port=5679, host='0.0.0.0')

    # Cleanup and close all connections
    #for peer in p2p.sockets:
    #    peer.close()
