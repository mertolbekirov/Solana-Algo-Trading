import requests
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import struct
import base58

# Initialize a client to connect to the Solana mainnet.
client = Client("http://api.mainnet-beta.solana.com")

# Define the Metaplex Program Id
METADATA_PROGRAM_ID = Pubkey.from_string('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s')
# Define the mint address you want to retrieve metadata for.
mintAddress = 'G6Hq9oVmugm6r3rYeigtujECmyWE2mk9rnh6TSZn8qRS'

def get_atts(mint_id):
    # Retrieve the metadata from the Solana blockchain.
    data = get_metadata(client, mint_id)['data']
    print(data)
    # Make an HTTP GET request to the URI specified in the metadata.
    # This URI usually points to a JSON file with more detailed information about the NFT.
    res = requests.get(data['uri'])
    return res.json()

# Main function to extract metadata.
def get_metadata(client, mint_key):
    # Calculate the account address where the metadata for the specified mint key is stored.
    metadata_account = get_metadata_account(mint_key)
    # Fetch the account data from Solana using the calculated metadata account.
    data = client.get_account_info(metadata_account).value.data
    # Decode the binary data into a readable format.
    metadata = unpack_metadata_account(data)
    return metadata

def get_metadata_account(mint_key):
    # The metadata account address is derived using the program ID and the mint key.
    # This address is where the NFT's metadata is stored on the blockchain.
    return Pubkey.find_program_address(
        [b'metadata', bytes(METADATA_PROGRAM_ID), bytes(Pubkey.from_string(mint_key))],
        METADATA_PROGRAM_ID
    )[0]

# Decode the binary data retrieved from the blockchain into a structured format.
def unpack_metadata_account(data):
    assert(data[0] == 4)  # The first byte is a version indicator; for now, it must be 4.
    i = 1
    # Extract the update authority and mint accounts from the data.
    source_account = base58.b58encode(bytes(struct.unpack('<' + "B"*32, data[i:i+32])))
    i += 32
    mint_account = base58.b58encode(bytes(struct.unpack('<' + "B"*32, data[i:i+32])))
    i += 32
    # Extract the name of the NFT.
    name_len = struct.unpack('<I', data[i:i+4])[0]
    i += 4
    name = struct.unpack('<' + "B"*name_len, data[i:i+name_len])
    i += name_len
    # Extract the symbol of the NFT.
    symbol_len = struct.unpack('<I', data[i:i+4])[0]
    i += 4 
    symbol = struct.unpack('<' + "B"*symbol_len, data[i:i+symbol_len])
    i += symbol_len
    # Extract the URI where more detailed metadata can be found.
    uri_len = struct.unpack('<I', data[i:i+4])[0]
    i += 4 
    uri = struct.unpack('<' + "B"*uri_len, data[i:i+uri_len])
    i += uri_len
    # Extract the seller fee.
    fee = struct.unpack('<h', data[i:i+2])[0]
    i += 2
    # Check if creators are present.
    has_creator = data[i] 
    i += 1
    creators = []
    verified = []
    share = []
    if has_creator:
        # If creators are present, extract their information.
        creator_len = struct.unpack('<I', data[i:i+4])[0]
        i += 4
        for _ in range(creator_len):
            creator = base58.b58encode(bytes(struct.unpack('<' + "B"*32, data[i:i+32])))
            creators.append(creator)
            i += 32
            verified.append(data[i])
            i += 1
            share.append(data[i])
            i += 1
    # Extract flags indicating if a primary sale has happened and if the metadata is mutable.
    primary_sale_happened = bool(data[i])
    i += 1
    is_mutable = bool(data[i])
    # Construct the metadata dictionary.
    metadata = {
        "update_authority": source_account,
        "mint": mint_account,
        "data": {
            "name": bytes(name).decode("utf-8").strip("\x00"),
            "symbol": bytes(symbol).decode("utf-8").strip("\x00"),
            "uri": bytes(uri).decode("utf-8").strip("\x00"),
            "seller_fee_basis_points": fee,
            "creators": creators,
            "verified": verified,
            "share": share,
        },
        "primary_sale_happened": primary_sale_happened,
        "is_mutable": is_mutable,
    }
    return metadata

print(get_atts(mintAddress))
