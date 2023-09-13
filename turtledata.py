import pandas as pd
import plotly.express as px
import pandas as pd
import requests
import json
import os
import datetime as dt
import time


class TurtleData:
    def solscan(self, mint):
        url = "https://public-api.solscan.io/token/meta?tokenAddress=" + mint
        apikey = os.getenv('SOLSCAN')
        headers = {'accept': 'aplication/json','token': apikey, 'User-agent': 'Mozilla/5.0'}
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            text = response.text
            data = json.loads(text)
            name = data['name']
            supply = int(data['supply'])
            supply = int(supply / 1000000000)
        else:
            name = mint
            supply = "UnableToFindSupply"
        return name, supply

    def create_dataframe(self, url, mint):
        if "2WLg3FUhPntCNZJoPq2x3qBizPoP3oQuvnu3ANwARQhP" in mint:  # USDC
            return
        if "Bd1yED9VaZGzvJAo2L5g7jgy2ZMYvjv55KeEvZQAoy7Q" in mint: # BONK
            return
        if "9T7ZwVNzeJsrvmxoumGBhgU4CtaiYo1zn2sLQRij4RBo" in mint: # BONK
            return

        if "AebrVZPfSH7KPAxPwnuqTZB9QNepdktk7HSSY4SNj7BM" in mint: # Venture Coin
            return
        if "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB" in mint: # USD T
            return
        if "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" in mint: # USDC
            return
        if "DUStKbzrPMpPpdsy56GskKK7greQx9ExXYRnP5LrStv5" in mint: # AIRDROp
            return
        if "H2HX58D6HBMVpLRhWYzFWEgWQp3L2hYSqf5ah4uG3xco" in mint: # USDC
            return
        if "6pLXEJqKEiZHF9hwvrrF7XPTUrrpxtWqgfvr65vVSn2D" in mint: # ORCA
            return
        print("new mint received: " + mint)
        program = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
        payload = {
    	    "jsonrpc": "2.0",
    	    "id": 1,
    	    "method": "getProgramAccounts",
    	    "params": [
    	        program,
    	        {
    		        "encoding": "jsonParsed",
    		        "filters": [
    		            {
    			            "dataSize": 165 # The size of a token account in bytes
    		            },
    		            {
    			            "memcmp": {
    			                "offset": 0, # The offset of the mint address in the account data
    			                "bytes": mint # The mint address of the token
    			            }   
    		            }
    		        ]
    	        }
    	    ]
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
#        
#            # Create the dataframe
            df = pd.json_normalize(data,'result',['account','owner','uiAmount','mint'], errors='ignore')
#        
#            # drop columns i dont care about
            df = df.drop(['pubkey','account.owner','account.rentEpoch','account.executable', 'account.data.parsed.info.isNative','account.data.parsed.info.state','account.data.parsed.type','account.data.program','account.data.space','account.lamports','mint','uiAmount','owner','account','account.data.parsed.info.tokenAmount.decimals','account.data.parsed.info.tokenAmount.amount','account.data.parsed.info.tokenAmount.uiAmountString'], axis=1)
#        
            tokenname, supply = self.solscan(mint)
#
#            # create new column called DealToken and Supply
            df["DealToken"] = tokenname
            df["Supply"] = supply
#        
#            # rename the columns into something readable
            df = df.rename(columns={"account.data.parsed.info.mint": "TokenAddress", "account.data.parsed.info.owner": "Wallet","account.data.parsed.info.tokenAmount.uiAmount": "Quantity"})
            df['SnapshotDate'] = dt.datetime.now()
            df['SnapshotDate'] = df['SnapshotDate'].dt.strftime('%Y-%m-%d %H:%M')
            df = df[['DealToken', 'TokenAddress', 'Wallet', "Quantity", "Supply", "SnapshotDate"]]
        else:
            print("Error..")
            df = df[['DealToken', 'TokenAddress', 'Wallet', "Quantity", "Supply", "SnapshotDate"]]     
#    
        return df

    def get_dealtokens(self, url, mintlist):
        # Define the mint address and the program id
        mint_address = "A73pnYZpCcb24iTvNb3PJWsUsSG7gR3MQhXtFX3itoQW"
        # ^ does not include TNSRxTRTLS2 AFCJxSQggZxKC6QMJZg34EyEDFhafiw8GgQM6pE81KyC 
        program_id = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"


        # Define the JSON-RPC request payload for getTokenAccountsByOwner method
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getProgramAccounts",
            "params": [
                program_id,
                {
                    "encoding": "jsonParsed",
                    "filters": [
                        {
                            "dataSize": 165
                        },
                        {
                            "memcmp": {
                                "offset": 32,
                                "bytes": mint_address
                            }
                        }
                    ]
                }
            ]
        }

        # Send the request and get the response
        response = requests.post(url, json=payload)

                # Check if the response is successful
        if response.status_code == 200:
            result = response.json()
            accounts = result["result"]
            dealtokens = []
            for account in accounts:
                if account['account']['data']['parsed']['info']['mint'] not in mintlist:
                    mint = account['account']['data']['parsed']['info']['mint']
                    dealtokens.append(mint)
        else:
            dealtokens.append("ERROR_GETTING_DEALTOKENS")
        
        return dealtokens