from brownie import Contract, network, config, interface
from .helpful_scripts import get_account
from .get_weth import get_weth, get_weth_contract
from .get_lending_pool import get_lending_pool
from web3 import Web3
import json
import os

def approve_erc20(amount, lending_pool_address, erc20_address, account):
    print("Approving ERC20...")
    erc20 = interface.IERC20(erc20_address)
    tx_hash = erc20.approve(lending_pool_address, amount, {"from": account})
    tx_hash.wait(1)
    print("Approved!")
    return erc20

def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor
    ) = lending_pool.getUserAccountData(account.address)
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print("You have deposited this amount:", total_collateral_eth)
    print("You have borrowed this amount:", total_debt_eth)
    print("you can borrow this amount: ", available_borrow_eth)
    return (
        float(available_borrow_eth),
        float(total_debt_eth)
        )

def get_contract_from_abi(abi_filename, contract_address):
    ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    print(os.path.join(ROOT_DIR, 'interfaces', 'ABI', abi_filename))
    abi = json.load(open(os.path.join(ROOT_DIR, 'interfaces', 'ABI', abi_filename)))
    return Contract.from_abi("aggregatorV3InterfaceABI", contract_address, abi)

def get_dai_eth_price():
    if(network.show_active() == "mainnet-fork-dev"):
        dai_eth_price_feed = get_contract_from_abi('aggregator_v3_abi.json', config["networks"][network.show_active()]['dai_eth_price_feed'])
        (roundId, answer, startedAt, updatedAt, answeredInRound) = dai_eth_price_feed.latestRoundData()
        dai_eth_price = Web3.fromWei(answer, 'ether')
    else:
        dai_usd_price_feed = get_contract_from_abi('aggregator_v3_abi.json', config["networks"][network.show_active()]['dai_usd_price_feed'])
        (roundId, answer_dai, startedAt, updatedAt, answeredInRound) = dai_usd_price_feed.latestRoundData()
        eth_usd_price_feed = get_contract_from_abi('aggregator_v3_abi.json', config["networks"][network.show_active()]['eth_usd_price_feed'])
        (roundId, answer_eth, startedAt, updatedAt, answeredInRound) = eth_usd_price_feed.latestRoundData()
        dai_eth_price = answer_dai/answer_eth
    return float(dai_eth_price)

def repay_all(amount, lending_pool, account):
    print("WE WILL REPAY EVERYTHING NOW...")
    dai_address = config["networks"][network.show_active()]['dai_address']
    contract = approve_erc20(
        amount,
        lending_pool,
        dai_address,
        account
        )
    # function repay(address asset, uint256 amount, uint256 rateMode, address onBehalfOf)
    repay_tx = lending_pool.repay(dai_address, amount, 2, account, {"from": account})
    repay_tx.wait(1)
    print("Repayed!")

def main():
    amount = Web3.toWei(0.1, "ether")
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_address"]
    if network.show_active() in ["mainnet-fork-dev"]:
        get_weth()
    lending_pool = get_lending_pool()
    erc20 = approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(erc20_address, amount, account, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    # Now we will borrow some DAI
    # Get DAI conversion Rate in terms of ETH, since we are only allowed to borrow 80% of what we own
    dai_eth_price = get_dai_eth_price()
    print("This is 1 Dai in Ether:", dai_eth_price)
    print("This is how much Ether you can borrow", borrowable_eth)
    amount_dai_borrowable = 0.95 * (borrowable_eth / dai_eth_price)
    print("here is the amount of DAI to borrow in DAI:", amount_dai_borrowable)

    # Let's borrow some DAI
    # borrow(address asset, uint256 amount, uint256 interestRateMode, uint16 referralCode, address onBehalfOf)
    borrowing_tx = lending_pool.borrow(
        config["networks"][network.show_active()]['dai_address'],
        Web3.toWei(amount_dai_borrowable, 'ether'),
        2,
        0,
        account,
        {"from": account}
    )
    borrowing_tx.wait(1)
    print("Borrowed!")
    print("After borrowing DAI:")
    (borrowable_eth, total_debt) = get_borrowable_data(lending_pool, account)
    repay_all(amount, lending_pool, account)