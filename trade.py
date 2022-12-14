from web3 import Web3
import yaml
import json
import time
with open('info.yaml') as fh:
    conf = yaml.load(fh, Loader=yaml.FullLoader)

BSC_url = 'https://bsc-dataseed.binance.org/'
Auro_url = 'https://mainnet.aurora.dev'
Poly_url = 'https://polygon-rpc.com'

BSCtoken = '0x68784ffaa6Ff05E3e04575DF77960DC1D9F42b4a'
Polytoken = '0x04429fbb948BBD09327763214b45e505A5293346'
Aurotoken = '0x2BAe00C8BC1868a5F7a216E881Bae9e662630111'

# BSC_addr = input("Please input your BSC contract address: ")
# Poly_addr = input("Please input your Polygon contract address: ")
# Auro_addr = input("Please input your Aurora contract address: ")

# Auro_addr = 'https://aurorascan.dev/address/0x881C47502f192FF87D0B1c9573035EC0E23cf8f3'
# BSC_addr = 'https://bscscan.com/address/0x881C47502f192FF87D0B1c9573035EC0E23cf8f3'
# Poly_addr = 'https://polygonscan.com/address/0x881C47502f192FF87D0B1c9573035EC0E23cf8f3'

Auro_addr = '0x881C47502f192FF87D0B1c9573035EC0E23cf8f3'
BSC_addr = '0x881C47502f192FF87D0B1c9573035EC0E23cf8f3'
Poly_addr = '0x881C47502f192FF87D0B1c9573035EC0E23cf8f3'

f = open('router_abi.json')
router_abi = json.load(f)
f.close()
f = open('Synapse_abi.json')
Synapse_abi = json.load(f)
f.close()
f = open('trade_abi.json')
trade_abi = json.load(f)
f.close()
private_key = conf['key']
web3 = Web3(Web3.HTTPProvider(BSC_url))
account = web3.eth.account.from_key(private_key).address

balance = int(conf['balance'])

def getPrice(addr, url, path, decimal):
    web3 = Web3(Web3.HTTPProvider(url))
    router_contract = web3.eth.contract(address= addr,abi = router_abi)
    price = router_contract.functions.getAmountsOut((10**(decimal[0] + 2)), path).call()
    price[0] = float(price[1]/(10**decimal[1]))
    path.reverse()
    price1 = router_contract.functions.getAmountsIn((10**(decimal[0]+2)),path).call()
    price[1] = float(price1[0]/(10**decimal[1]))
    return price
    
def trading(buy_url, sell_url, buy_addr, sell_addr, buyamounts, tokenaddr, buynet, sellnet):
    result = 0
    # for i in range(9):
    web3 = Web3(Web3.HTTPProvider(buy_url))
    trade_contract = web3.eth.contract(address=buy_addr, abi= trade_abi)
    to = account + "000000000000000000000000"
    
    lockId = '2326436938591503159836224363336437055'

    print("aaaaaa")
    print(buyamounts)
    print(account)
    print(to)
    print(lockId)
    print(sellnet)

    buy = trade_contract.functions.buy(buyamounts, account, to, lockId, sellnet).build_transaction()
    sign_buy = web3.eth.account.sign_transaction(buy, private_key=private_key)
    buy_hash = web3.eth.send_raw_transaction(sign_buy.rawTransaction)
    web3.eth.wait_for_transaction_receipt(buy_hash)
    print(sign_buy.hash.hex())
    buyresult = trade_contract.call().buyresult()
    web3 = Web3(Web3.HTTPProvider(sell_url))
    trade_contract = web3.eth.contract(address=sell_addr, abi= trade_abi)
    tokensource = tokenaddr + '000000000000000000000000'
    sell = trade_contract.functions.sell(lockId, account, int(buyresult*0.997), buynet, tokensource, (sign_buy.hash.hex())).build_transaction()
    sign_sell = web3.eth.account.sign_transaction(sell, private_key=private_key)
    sell_hash = web3.eth.send_raw_transaction(sign_sell.rawTransaction)
    web3.eth.wait_for_transaction_receipt(sell_hash)
    print(sign_sell.hash.hex())
    sellresult = trade_contract.call().sellresult()
    result = result + sellresult
    return result

def Convert(addr, chainId, indexfrom, indexto, amount):
    trade_contract = web3.eth.contract(address=addr, abi= trade_abi)
    convert = trade_contract.functions.convert(account, chainId, indexfrom, indexto, amount).build_transaction()
    sign_convert = web3.eth.account.sign_transaction(convert, private_key= private_key)
    convert_hash = web3.eth.send_raw_transaction(sign_convert.rawTransaction)
    web3.eth.wait_for_transaction_receipt(convert_hash)
    print(sign_convert.hash)

def main():
    while(1):
        bscprice = getPrice('0x10ED43C718714eb63d5aA57B78B54704E256024E', BSC_url, path=["0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56", "0x68784ffaa6Ff05E3e04575DF77960DC1D9F42b4a"], decimal=[18,18])
        print('BSC price: ', bscprice)
        polyprice = getPrice('0xC0788A3aD43d79aa53B09c2EaCc313A787d1d607', Poly_url, path=['0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174','0x04429fbb948BBD09327763214b45e505A5293346'], decimal=[6, 18])
        print('Polygon price: ', polyprice)
        auroprice = getPrice('0x2CB45Edb4517d5947aFdE3BEAbF95A582506858B', Auro_url, path=['0xB12BFcA5A55806AaF64E99521918A4bf0fC40802','0x2BAe00C8BC1868a5F7a216E881Bae9e662630111'], decimal=[6,18])
        print('Aurora price: ',auroprice)
        if bscprice[0] > auroprice[0] and bscprice[0] > polyprice[0]:
            if auroprice[1]<polyprice[1]:
                print("From BSC to Aurora possible")
                eprofit = (bscprice[0] - auroprice[1]) * 0.32 - 1
                print("Expected profit: ",eprofit,'$')
                if eprofit > 0:
                    print("Progressing trade...")
                    # usdc = trading(BSC_url, Auro_url, BSC_addr, Auro_addr, [(10**20), (bscprice[0]*10**18)], BSCtoken, "0x42534300", "0x41555200" )
                    usdc = trading(BSC_url, Auro_url, BSC_addr, Auro_addr, [(10**18*balance), (bscprice[0]*10**18)], BSCtoken, '0x42534300', '0x41555200' )
                    Convert(Auro_addr, 56, 2, 1, usdc)
                    print("trade success!")
            if polyprice[1]<auroprice[1]:
                print("From BSC to Polygon possible")
                eprofit = (bscprice[0] - polyprice[1]) * 0.32 - 1
                print("Expected profit: ",eprofit,'$')
                if eprofit > 0:
                    print("Progressing trade...")
                    # usdc = trading(BSC_url, Poly_url, BSC_addr, Poly_addr, [(10**20), (bscprice[0]*10**18)], BSCtoken, "0x42534300", "0x504f4c00" )
                    usdc = trading(BSC_url, Poly_url, BSC_addr, Poly_addr, [(10**18*balance), (bscprice[0]*10**18)], BSCtoken, '0x42534300', '0x504f4c00' )
                    Convert(Poly_addr, 56, 2, 2, usdc)
                    print("trade success!")
        elif auroprice[0]>polyprice[0]:
            if bscprice[1]<polyprice[1]:
                print("From Aurora to BSC possible")
                eprofit = (auroprice[0] - bscprice[1]) * 0.32 - 1
                print("Expected profit: ",eprofit,'$')
                if eprofit > 0:
                    print("Progressing trade...")
                    # busd = trading(Auro_url, BSC_url, Auro_addr, BSC_addr, [(10**8), (auroprice[0]*10**18)], Aurotoken, "0x41555200", "0x42534300" )
                    busd = trading(Auro_url, BSC_url, Auro_addr, BSC_addr, [(balance*10**6), (auroprice[0]*10**18)], Aurotoken, "0x41555200", "0x42534300" )
                    Convert(BSC_addr, 1313161554, 1, 2, busd)
                    print("trade success!")
            if polyprice[1]<bscprice[1]:
                print("From Aurora to Polygon possible")
                eprofit = (auroprice[0] - polyprice[1]) * 0.32 - 1
                print("Expected profit: ",eprofit,'$')
                if eprofit > 0:
                    print("Progressing trade...")
                    # usdc = trading(Auro_url, Poly_url, Auro_addr, Poly_addr, [(10**8), (auroprice[0]*10**18)], Aurotoken, "0x41555200", "0x504f4c00")
                    usdc = trading(Auro_url, Poly_url, Auro_addr, Poly_addr, [(balance*10**6), (auroprice[0]*10**18)], Aurotoken, "0x41555200", "0x504f4c00")
                    Convert(Poly_addr, 1313161554, 2, 2, usdc)
                    print("trade success!")
        else:
            if bscprice[1]<auroprice[1]:
                print("From Polygon to BSC possible")
                eprofit = (polyprice[0] - bscprice[1]) * 0.32 - 1
                print("Expected profit: ",eprofit,'$')
                if eprofit > 0:
                    print("Progressing trade...")
                    # busd = trading(Poly_url, BSC_url, Poly_addr, BSC_addr, [(10**8), (polyprice[0]*10**18)], Polytoken, "0x504f4c00", "0x42534300" )
                    busd = trading(Poly_url, BSC_url, Poly_addr, BSC_addr, [(balance*10**6), (polyprice[0]*10**18)], Polytoken, "0x504f4c00", "0x42534300" )
                    Convert(BSC_addr, 137, 1, 2, busd)
                    print("trade success!")
            else:
                print('From Polygon to Aurora possible')
                eprofit = (polyprice[0] - auroprice[1]) * 0.32 - 1
                print("Expected profit: ",eprofit,'$')
                if eprofit > 0:
                    print("Progressing trade...")
                    # usdc = trading(Poly_url, Auro_url, Poly_addr, Auro_addr, [(10**8), (polyprice[0]*10**18)], Polytoken, "0x504f4c00", "0x41555200" )
                    usdc = trading(Poly_url, Auro_url, Poly_addr, Auro_addr, [(balance*10**6), (polyprice[0]*10**18)], Polytoken, "0x504f4c00", "0x41555200" )
                    Convert(Auro_addr, 137, 2, 2, usdc)
                    print("trade success!")
        time.sleep(10)

if __name__ == '__main__':
    main()