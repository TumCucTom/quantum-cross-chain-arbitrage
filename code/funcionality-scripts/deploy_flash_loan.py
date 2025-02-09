# deploy_flash_loan.py

from ape import accounts, project

def main():
    """
    Deploy the Flash Loan Arbitrage contract and execute the flash loan.
    """
    deployer = accounts.load("my_account")  # Load your private key

    # Deploy Contract
    contract = deployer.deploy(project.FlashLoanArbitrage)
    print(f"✅ Contract Deployed at: {contract.address}")

    # Aave V3 Lending Pool Address
    aave_pool = "0x7d2768dE32b0b80b7a3454c06BdAc9FbFf95D10D"

    # DAI as asset for borrowing
    dai_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

    # Execute Flash Loan
    loan_amount = 10**18  # 1 DAI
    contract.execute_flash_loan(aave_pool, dai_address, loan_amount, sender=deployer)
    print("🚀 Flash Loan Executed!")
