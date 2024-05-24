import asyncio  # Imports asyncio library for handling asynchronous operations.
import websockets  # Websockets library to enable WebSocket connections.
import json  # JSON library to handle JSON data formats.
from solana.rpc.api import Client  # Import the Client class from Solana's RPC API to interact with the Solana blockchain.
from solders.pubkey import Pubkey  # Pubkey for handling public keys within Solana's ecosystem.
from solders.signature import Signature  # Signature class to handle transaction signatures.
from solders.transaction_status import UiPartiallyDecodedInstruction, ParsedInstruction
from solders.rpc.responses import GetTransactionResp
from pip._vendor.typing_extensions import Iterator
from termcolor import colored
from typing import List

URI = "https://api.mainnet-beta.solana.com"  # "https://api.devnet.solana.com" | "https://api.mainnet-beta.solana.com"
solana_client = Client(URI)
wallet_address = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"

def get_meta(
        transaction: GetTransactionResp
) -> List[UiPartiallyDecodedInstruction | ParsedInstruction]:
    meta = transaction \
        .value \
        .transaction \
        .meta
    return meta

def get_instructions(
        transaction: GetTransactionResp
) -> List[UiPartiallyDecodedInstruction | ParsedInstruction]:
    instructions = transaction \
        .value \
        .transaction \
        .transaction \
        .message \
        .instructions
    return instructions

def instructions_with_program_id(
        instructions: List[UiPartiallyDecodedInstruction | ParsedInstruction],
        program_id: str
) -> Iterator[UiPartiallyDecodedInstruction | ParsedInstruction]:
    return (instruction for instruction in instructions
            if instruction.program_id == program_id)

def calc_lpLockedPct(
        instruction: UiPartiallyDecodedInstruction,
        signature: Signature
        ):
    lpReserve = -69
    lpReserve_ = -69    # Initialize to -69
    
    # EXTRACT LPRESERVE
    accounts = instruction.accounts
    #lpmint = accounts[7]
     #lpReserve arbitrarily set to -69
    transaction_0 = solana_client.get_transaction(
        signature,
        encoding="jsonParsed",
        max_supported_transaction_version=0
    )
    meta_data = get_meta(transaction_0)
    innerInstructions_0 = meta_data.inner_instructions  # initializeMint
    
    is_new_pool = False


    for x in innerInstructions_0:
        for y in x.instructions:
            try:
                if Pubkey.from_string(y.parsed['info']['mint']) == accounts[7] and y.parsed['type'] == 'initializeMint':
                    lpDecimals = y.parsed['info']['decimals']
                    print(colored(f"lpDecimals: {lpDecimals}", "green", "on_white"))
                    is_new_pool = True
                elif Pubkey.from_string(y.parsed['info']['mint']) == accounts[7] and y.parsed['type'] == 'mintTo':
                    lpReserve = y.parsed['info']['amount']
                    lpReserve_ = y.parsed['info']['amount']
                    print(colored(f"lpReserve: {lpReserve}", "green", "on_white"))
                    #lpReserve: parseInt(lpMintInstruction.parsed.info.amount)
                else:
                    pass
            except:
                pass

            try:
                if Pubkey.from_string(y.parsed['type']) == accounts[7] and y.parsed['type'] == 'initializeMint':
                    lpDecimals = y.parsed['info']['decimals']

                else:
                    pass
            except:
                pass

    

    # LP BURN CALCULATION
    try:
        accInfo = solana_client.get_account_info_json_parsed(accounts[7])
        accdata_ = accInfo.value.data
        actual_supply = accdata_.parsed['info']['supply']
        print(colored(f"actual_supply: {actual_supply}", "red", "on_white"))
    except Exception as e:
        print(colored(f"Error parsing response: {e}"))
        print(colored(f"Response: {accInfo}"))

    if lpReserve_ == -69: 
        burnAmt = "Failed"
        burnPct = "Failed"

    else:
        #lpReserve = float(lpReserve) / math.pow(10, int(accdata_.parsed['info']['decimals']))
        # actual_supply = float(accdata_.parsed['info']['supply']) / math.pow(10, int(accdata_.parsed['info']['decimals']))
        print(colored(f"lpReserve supply: {lpReserve}", "yellow", "on_black"))
        print(colored(f"actual_supply: {actual_supply}", "green", "on_black"))
        # Calculate burn percentage
    
        actual_supply = float(actual_supply)
        lpReserve = float(lpReserve)
        burnAmt = lpReserve - actual_supply  # Token for Token burn amount
        print(colored(f"Burn Amount: {burnAmt}", "red", "on_white"))
        burnPct = (burnAmt / lpReserve) * 100  # Percentage burn calculation

        lpLockedPct_ = float("{:.20f}".format(burnPct))
        if is_new_pool:
            print(colored(f"New Locked %: {lpLockedPct_}", "green", "on_yellow"))

    return lpLockedPct_

tsxSig = Signature.from_string('3aGWkareQz7Wp2XB9XHT76CkZCsQukse2ePs6AL6jLgq39wXYsvgcqXGRr216ZagSJu3GeLX2YojAGpv2jMycKzZ')
transaction = solana_client.get_transaction(
                        tsxSig,
                        encoding="jsonParsed",
                        max_supported_transaction_version=0
                    )
instructions = get_instructions(transaction)
filtered_instuctions = instructions_with_program_id(instructions, Pubkey.from_string(wallet_address))
for inst in filtered_instuctions:
    lplockedPct = calc_lpLockedPct(inst, tsxSig)  # Calls the getTokens function to process and display the new pool information.
    print (colored(f"Locked LP PCT: {lplockedPct}"))
