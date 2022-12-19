from brownie import Contract, config, network
from .helpful_scripts import get_account
from web3 import Web3
import json

def get_weth_contract():
    with open('/Users/nourkaroui/Desktop/web3/aave-brownie/brownie/interfaces/ABI/weth_abi.json') as f:
      abi = json.load(f)
    weth = Contract.from_abi("WETHGateway", config["networks"][network.show_active()]["weth_address"], abi)
    return weth

def get_weth():
    account = get_account()
    weth = get_weth_contract()
    tx = weth.deposit({'value': Web3.toWei(0.1, 'ether'), 'from':account})
    tx.wait(1)
    print("received", weth.balanceOf(account))
    return tx

def main():
    get_weth()