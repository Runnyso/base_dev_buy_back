import requests, time

dev_wallets = {}  # pair → dev wallet

def dev_buy_back():
    print("Base — Dev Buy Back Detector (dev wallet buying own token)")
    seen_txs = set()

    while True:
        try:
            # Catch new pools → dev wallet
            r = requests.get("https://api.dexscreener.com/latest/dex/pairs/base")
            for pair in r.json().get("pairs", []):
                pair_addr = pair["pairAddress"]
                if pair_addr in dev_wallets:
                    continue

                age = time.time() - pair.get("pairCreatedAt", 0) / 1000
                if age > 300: continue

                tx_hash = pair.get("pairCreatedTxHash")
                if not tx_hash: continue

                tx = requests.get(f"https://api.basescan.org/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}").json()
                creator = tx["result"]["from"].lower()
                dev_wallets[pair_addr] = creator

            # Watch recent buys
            r2 = requests.get("https://api.dexscreener.com/latest/dex/transactions/base?limit=400")
            for tx in r2.json().get("transactions", []):
                txid = tx["hash"]
                if txid in seen_txs or tx.get("side") != "buy":
                    continue
                seen_txs.add(txid)

                buyer = tx["from"].lower()
                pair_addr = tx["pairAddress"]
                usd = tx.get("valueUSD", 0)

                if pair_addr not in dev_wallets or buyer != dev_wallets[pair_addr]:
                    continue

                token = pair["baseToken"]["symbol"]
                print(f"DEV BUYING BACK!\n"
                      f"{token} dev wallet just bought ${usd:,.0f}\n"
                      f"Dev: {buyer}\n"
                      f"https://dexscreener.com/base/{pair_addr}\n"
                      f"https://basescan.org/address/{buyer}\n"
                      f"→ Confidence signal or manipulation?\n"
                      f"{'DEV BUY'*20}")

        except:
            pass
        time.sleep(1.8)

if __name__ == "__main__":
    dev_buy_back()
