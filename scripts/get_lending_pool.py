from brownie import Contract, config, network, interface
import json

def get_lending_pool():
    lending_pool_addresses_provider = config['networks'][network.show_active()]['lending_pool_adr_provider']
    print("getting lending pool")
    with open('/Users/nourkaroui/Desktop/web3/aave-brownie/brownie/interfaces/ABI/lending_pool_provider_abi.json') as f:
        abi = json.load(f)
    lending_pool_addresses_provider = Contract.from_abi("LendingPoolAddressesProvider", lending_pool_addresses_provider, abi)
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    print("got here")
    with open('/Users/nourkaroui/Desktop/web3/aave-brownie/brownie/interfaces/ABI/lending_pool_abi.json') as f:
        abi = json.load(f)
    lending_pool = Contract.from_abi("LendingPool", lending_pool_address, abi)
    print(lending_pool)
    return lending_pool

def main():
    get_lending_pool()