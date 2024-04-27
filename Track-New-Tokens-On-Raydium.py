import asyncio  # Imports asyncio library for handling asynchronous operations.
import websockets  # Websockets library to enable WebSocket connections.
import json  # JSON library to handle JSON data formats.
from solana.rpc.api import Client  # Import the Client class from Solana's RPC API to interact with the Solana blockchain.
from solders.pubkey import Pubkey  # Pubkey for handling public keys within Solana's ecosystem.
from solders.signature import Signature  # Signature class to handle transaction signatures.
import pandas as pd  # Pandas library for handling data in tabular form.
from tabulate import tabulate  # Tabulate library to display tables in a readable format.

# The wallet address of the Raydium DEX on Solana which is used to identify transactions related to it.
wallet_address = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
seen_signatures = set()  # A set to store signatures of processed transactions to avoid reprocessing the same transactions.
solana_client = Client("https://api.mainnet-beta.solana.com")  # Initializes a client connected to the Solana mainnet.

def getTokens(str_signature):
    """
    This function extracts and prints information about new liquidity pools from transaction signatures.

    Parameters:
    str_signature (str): A string representing the transaction signature from which to extract token information.
    """
    signature = Signature.from_string(str_signature)  # Converts the string signature to a Signature object.
    # Retrieves the transaction details from the blockchain using the signature, requesting JSON parsed format.
    transaction = solana_client.get_transaction(signature, encoding="jsonParsed",
                                                max_supported_transaction_version=0).value
    # Extracts the list of instructions from the transaction; each instruction represents an operation in the transaction.
    instruction_list = transaction.transaction.transaction.message.instructions

    for instructions in instruction_list:
        # Check if the instruction is from the Raydium DEX program.
        if instructions.program_id == Pubkey.from_string(wallet_address):
            print("============NEW POOL DETECTED====================")
            Token0 = instructions.accounts[8]  # Extracts the first token account involved in the pool.
            Token1 = instructions.accounts[9]  # Extracts the second token account involved in the pool.
            # Creates a dictionary with token information to display.
            data = {'Token_Index': ['Token0', 'Token1'],
                    'Account Public Key': [Token0, Token1]}
            df = pd.DataFrame(data)  # Converts the dictionary into a pandas DataFrame for better formatting.
            table = tabulate(df, headers='keys', tablefmt='fancy_grid')  # Formats the DataFrame into a table using tabulate.
            print(table)  # Prints the table.

async def run():
    """
    This function sets up a WebSocket connection to the Solana blockchain and subscribes to logs mentioning the Raydium DEX wallet address.
    """
    uri = "wss://api.mainnet-beta.solana.com"  # Defines the WebSocket URI for connecting to Solana's mainnet.
    async with websockets.connect(uri) as websocket:
        # Send a subscription request via WebSocket to listen for logs that mention the Raydium DEX wallet address.
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "logsSubscribe",
            "params": [
                {"mentions": [wallet_address]},
                {"commitment": "finalized"}
            ]
        }))

        # Wait for and print the response from the subscription request.
        first_resp = await websocket.recv()  # Receives the first response from the WebSocket connection.
        response_dict = json.loads(first_resp)  # Parses the JSON response into a dictionary.
        if 'result' in response_dict:
            print("Subscription successful. Subscription ID: ", response_dict['result'])

        # Continuously process incoming WebSocket messages.
        async for response in websocket:
            response_dict = json.loads(response)  # Parses each incoming message from JSON format.

            # Check if there is no error in the response and if it contains new information.
            if response_dict['params']['result']['value']['err'] is None:
                signature = response_dict['params']['result']['value']['signature']  # Extracts the signature from the response.

                if signature not in seen_signatures:  # Check if the signature has not been processed before.
                    seen_signatures.add(signature)  # Add the new signature to the set of processed signatures.
                    log_messages_set = set(response_dict['params']['result']['value']['logs'])  # Extracts logs from the response.

                    search = "initialize2"  # This is a keyword associated with initializing new pools.
                    if any(search in message for message in log_messages_set):
                        print(f"New pool transaction detected: https://solscan.io/tx/{signature}")
                        getTokens(signature)  # Calls the getTokens function to process and display the new pool information.

async def main():
    """
    The main entry point for the asyncio program, which calls the run function to start the application.
    """
    await run()  # Calls the run function to begin the WebSocket subscription and processing loop.

asyncio.run(main())  # Starts the asyncio event loop and runs the main function.