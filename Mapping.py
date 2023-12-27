from web3 import Web3
import json
import requests
import csv

# Initialize a web3 instance 
web3 = Web3(Web3.HTTPProvider('https://arbitrum-one.publicnode.com'))

# Verify connection
if web3.is_connected():
    print("Connected to Arbitrum")
else:
    print("Failed to connect to Arbitrum")

# Get ABI from Arbiscan's API
def get_abi_from_arbiscan(contract_address, arbiscan_api_key):
    url = f"https://api.arbiscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={arbiscan_api_key}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == '1':
            abi = result['result']
            return abi
        else:
            print(f"Failed to retrieve ABI: {result['result']}")
            return None
    else:
        print(f"HTTP Error: {response.status_code}")
        return None

arbiscan_api_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
contract_address = Web3.to_checksum_address("0x1F98431c8aD98523631AE4a59f267346ea31F984")
contract_abi = get_abi_from_arbiscan(contract_address, arbiscan_api_key)
contract = web3.eth.contract(address=contract_address, abi=contract_abi)


if contract_abi:
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    # Filter signature : PoolCreated
    event_signature_hash = web3.keccak(text='PoolCreated(address,address,uint24,int24,address)').hex()

    start_block = 150000001
    latest_block = web3.eth.block_number
    max_block_range = 50000  # Fetching blocks 

    # Create a CSV
    with open('./pools.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Pool', 'Token0', 'Token1'])

        print(f"Last block: {latest_block}")

        while start_block < latest_block:
            end_block = min(start_block + max_block_range, latest_block)
            print(f"Fetching blocks: {start_block} to {end_block}")

            try:
                logs = web3.eth.get_logs({
                    'fromBlock': start_block,
                    'toBlock': end_block,
                    'address': contract_address,
                    'topics': [event_signature_hash]
                })
                print(f"Logs found : {len(logs)}")

                for log in logs:
                    # Decode events
                    decoded_event = contract.events.PoolCreated().process_log(log)
                    pool_address = decoded_event.args.pool
                    token0 = decoded_event.args.token0
                    token1 = decoded_event.args.token1
                    writer.writerow([pool_address, token0, token1])

            except Exception as e:
                print(f"Error: {e}")

            start_block = end_block + 1