import datetime
import json
import random
import string
import hashlib

import requests
from flask import render_template, redirect, request
from flask import flash
from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_SERVICE_ADDRESS = "http://127.0.0.1:8000"
POLITICAL_PARTIES = ["Gerindra","Demokrat","Golkar","PDIP","PKS","Nasdem","PKB"]
VOTER_IDS=[
    "eb2ce07109855abc",
    "71686a8bee6d6bdc",
    "915c35b1f6d1870f",
    "ce7d5f6a75fa4520",
    "5e0d33ff570948ba",
    "2f2253c3a3bfe1df",
    "55caf716795ae151",
    "bd0fd255ecc7eee8",
    "5bfe5defd7c22b4e",
    "485e427940674412",
    "483523a9aaca8942",
    "ef45bdff8447adc8",
    "60041ac1e31d1e0a",
    "39489ac63da7e00d",
    "67da4adbf39b9253"]

vote_check=[]

posts = []

def generate_random_id():
    """Generate a random string and hash it with SHA256."""
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    hashed_id = hashlib.sha256(random_string.encode()).hexdigest()
    return hashed_id

def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_SERVICE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        vote_count = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                tx["voter_id"] = generate_random_id()
                content.append(tx)


        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()

    vote_gain = []

    for post in posts:
        vote_gain.append(post["party"])

    return render_template('index.html',
                           title='Pemilu',
                           posts=posts,
                           vote_gain=vote_gain,
                           node_address=CONNECTED_SERVICE_ADDRESS,
                           readable_time=timestamp_to_string,
                           political_parties=POLITICAL_PARTIES,
                           voter_ids=VOTER_IDS)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    party = request.form["party"]
    voter_id = request.form["voter_id"]

    post_object = {
        'voter_id': voter_id,
        'party': party,
    }
    if voter_id not in VOTER_IDS:
        flash('ID pemilih tidak valid, silakan pilih ID pemilih dari contoh!', 'error')
        return redirect('/')
    if voter_id in vote_check:
        flash('ID pemilih ('+voter_id+') sudah memberikan suara', 'error')
        return redirect('/')
    else:
        vote_check.append(voter_id)
    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_SERVICE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})
    # print(vote_check)
    flash('Sukses memilih')
    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
