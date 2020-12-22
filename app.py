import flask
from flask import request, jsonify
from pprint import pprint
from peerplays import PeerPlays
import random
import string
from os import environ

app = flask.Flask(__name__)
app.config["DEBUG"] = True

wifs = [x.strip() for x in environ.get('WIF_KEYS').split(',')]
owner_id = environ.get('OWNER_ID')

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def get_peerplays():
    return PeerPlays(
        "ws://3.6.53.92:8090",
        keys=wifs,
        nobroadcast=False
        )

@app.route('/', methods=['GET'])
def home():
    p = get_peerplays()
    return jsonify(p.info())

@app.route('/mint_nft', methods=['POST'])
def mint_nft():
    if 'token_uri' in request.form:
        token_uri = request.form['token_uri']
    else:
        return "Error: No token_uri field provided. Please specify a token_uri.", 400

    if 'name' in request.form:
        if len(request.form['name'].strip()) > 0:
            name = request.form['name']
        else:
            return "Error: name is empty.", 400
    else:
        return "Error: No name field provided. Please specify a name.", 400

    nameMetadata = get_random_string(5)
    if ('is_sellable' in request.form and request.form['is_sellable'].lower() == 'false'):
        is_sellable = False 
    else:
        is_sellable = True

    if ('is_transferable' in request.form and request.form['is_transferable'].lower() == 'false'):
        is_transferable = False 
    else:
        is_transferable = True

    peerplays = get_peerplays()
    peerplays.blocking = True
    md = peerplays.nft_metadata_create(owner_id, name, nameMetadata, '', revenue_partner="1.2.8", revenue_split=300, is_sellable=is_sellable, is_transferable=is_transferable)
    metadata_id = md["operation_results"][0][1]
    print("nft_metadata_create Success! metadataId:", metadata_id)

    tok = peerplays.nft_mint(owner_id, metadata_id, owner_id, owner_id, owner_id, token_uri)
    tok_id = tok["operation_results"][0][1]
    print("nft_mint Success! Token ID:", tok_id)

    # app = peerplays.nft_approve(owner_id, "1.2.8", tok_id)
    # print("nft_approve Success!")
    peerplays.blocking = False
    response = { "metadata": md, "token": tok }
    return jsonify(response)

@app.route('/get_nft', methods=['GET'])
def get_nft():
    if 'id' in request.args:
        nft_id = request.args['id']
    else:
        return "Error: No id field provided. Please specify an id.", 400
    
    peerplays = get_peerplays()
    tok = peerplays.rpc.get_object(nft_id)
    return jsonify(tok)

@app.route('/transfer_nft', methods=['POST'])
def transfer_nft():
    if 'nft_id' in request.form:
        nft_id = request.form['nft_id']
    else:
        return "Error: No nft_id field provided. Please specify an nft_id.", 400

    if 'to_id' in request.form:
        to_id = request.form['to_id']
    else:
        return "Error: No to_id field provided. Please specify an to_id.", 400

    peerplays = get_peerplays()
    tok = peerplays.rpc.get_object(nft_id)
    print(tok)

    transfer = peerplays.nft_safe_transfer_from(owner_id, owner_id, to_id, nft_id, "Test transfer")
    print("nft_safe_transfer_from Success!")
    print(transfer)

    # app = peerplays.nft_approve("1.2.9", "1.2.8", nft_id)
    # print("nft_approve Success!", app)

    return jsonify(transfer)

@app.route('/update_nft', methods=['GET'])
def update_nft():
    return jsonify({})

app.run()







# Running server in Production
# ----------------------------
# [Unit]
# Description=faucet
# After=network.target

# [Service]
# WorkingDirectory=/home/ubuntu/faucet
# User=ubuntu
# ExecStart=/home/ubuntu/faucet/env/bin/python manage.py runserver -h 0.0.0.0                           
# #ExecStart=/home/ubuntu/faucet/env/bin/uwsgi --ini /home/ubuntu/faucet/wsgi.ini
# Restart=always

# [Install]
# WantedBy=mult-user.target