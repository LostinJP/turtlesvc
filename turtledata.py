import pandas as pd
import plotly.express as px
import pandas as pd
import requests
import json
import os
import time
import datetime as dt




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
        data = response.json()
    
        # Create the dataframe
        df = pd.json_normalize(data,'result',['account','owner','uiAmount','mint'], errors='ignore')
    
        # drop columns i dont care about
        df = df.drop(['pubkey','account.owner','account.rentEpoch','account.executable', 'account.data.parsed.info.isNative','account.data.parsed.info.state','account.data.parsed.type','account.data.program','account.data.space','account.lamports','mint','uiAmount','owner','account','account.data.parsed.info.tokenAmount.decimals','account.data.parsed.info.tokenAmount.amount','account.data.parsed.info.tokenAmount.uiAmountString'], axis=1)
    
        tokenname, supply = self.solscan(mint)
        # create new column called DealToken and Supply
        df["DealToken"] = tokenname
        df["Supply"] = supply
    
        # rename the columns into something readable
        df = df.rename(columns={"account.data.parsed.info.mint": "TokenAddress", "account.data.parsed.info.owner": "Wallet","account.data.parsed.info.tokenAmount.uiAmount": "Quantity"})
        df['SnapshotDate'] = dt.datetime.now()
        df['SnapshotDate'] = df['SnapshotDate'].dt.strftime('%Y-%m-%d %H:%M')
        df = df[['DealToken', 'TokenAddress', 'Wallet', "Quantity", "Supply", "SnapshotDate"]]
    
        return df
