from web3 import Web3
import json
import requests

# ===== CONFIGURATION =====
RPC_URL = "https://sepolia.base.org/"
PRIVATE_KEY_FILE = "privatekey.txt"
CONTRACT_ADDRESS = "0xaf33add7918f685b2a82c1077bd8c07d220ffa04"
MINT_FUNCTION_SELECTOR = "0x40c10f19"
MINT_AMOUNT = Web3.to_wei(100000000, 'ether')
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "*/*"
}

# ===== CORE FUNCTIONS =====
def load_private_keys(path=PRIVATE_KEY_FILE):
    try:
        with open(path, "r") as file:
            keys = [line.strip() for line in file if line.strip()]
            if not keys:
                raise Exception("File privatekey.txt kosong.")
            return keys
    except FileNotFoundError:
        raise Exception("File privatekey.txt tidak ditemukan.")

def connect_web3(rpc_url):
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError("❌ Gagal terhubung ke Base Sepolia RPC.")
    return w3

def get_account_info(w3, private_key):
    account = w3.eth.account.from_key(private_key)
    address = account.address
    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    chain_id = w3.eth.chain_id

    return {
        "address": address,
        "balance_wei": balance_wei,
        "balance_eth": balance_eth,
        "chain_id": chain_id
    }

def send_rpc_request(method, params, id=1):
    payload = {
        "jsonrpc": "2.0",
        "id": id,
        "method": method,
        "params": params
    }
    response = requests.post(RPC_URL, headers=HEADERS, data=json.dumps(payload))
    return response.json()

def mint_token(w3, private_key, to_address, amount, chain_id):
    nonce = w3.eth.get_transaction_count(to_address)
    data = (
        MINT_FUNCTION_SELECTOR +
        to_address[2:].rjust(64, '0') +
        hex(amount)[2:].rjust(64, '0')
    )

    tx = {
        'nonce': nonce,
        'to': Web3.to_checksum_address(CONTRACT_ADDRESS),
        'value': 0,
        'gas': 100000,
        'gasPrice': w3.to_wei('2', 'gwei'),
        'data': data,
        'chainId': chain_id
    }

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"🚀 [MINT] Tx Hash: {tx_hash.hex()}")
    return tx_hash.hex()

# ===== MAIN FUNCTION =====
def main():
    keys = load_private_keys()
    w3 = connect_web3(RPC_URL)

    for idx, key in enumerate(keys, start=1):
        print(f"\n======= 🧾 Wallet #{idx} =======")
        try:
            info = get_account_info(w3, key)
            print(f"📍 Address: {info['address']}")
            print(f"💰 Balance: {info['balance_eth']} ETH")

            mint_hash = mint_token(w3, key, info['address'], MINT_AMOUNT, info['chain_id'])

            block_info = send_rpc_request("eth_blockNumber", [])
            print(f"📊 Block Number: {int(block_info['result'], 16)}")

        except Exception as e:
            print(f"❌ [Wallet #{idx}] Error: {e}")

if __name__ == "__main__":
    main()
