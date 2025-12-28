#!/usr/bin/env python3
"""
Basescan Token Transactions Analyzer
Fetches and aggregates token transactions for a specific address and token contract
"""

import requests
import time
from datetime import datetime
from collections import defaultdict

# Target address and token contract
WALLET_ADDRESS = "0x5e3Af779Ef05544FF0D509458F3cb47341f2055b"
TOKEN_CONTRACT = "0xa1136031150e50b015b41f1ca6b2e99e49d8cb78"

# Basescan API endpoint (public API, no key required for basic queries)
BASESCAN_API = "https://api.basescan.org/api"


def get_token_transactions(address, contract_address, page=1, offset=10000):
    """Fetch token transactions from Basescan API"""
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "contractaddress": contract_address,
        "page": page,
        "offset": offset,
        "sort": "asc"
    }

    response = requests.get(BASESCAN_API, params=params)
    data = response.json()

    if data["status"] == "1":
        return data["result"]
    else:
        print(f"API Error: {data.get('message', 'Unknown error')}")
        return []


def analyze_transactions(transactions):
    """Analyze and aggregate transaction data"""
    stats = {
        "total_transactions": len(transactions),
        "total_received": 0,
        "total_sent": 0,
        "unique_senders": set(),
        "unique_receivers": set(),
        "transactions_by_date": defaultdict(int),
        "volume_by_date": defaultdict(float),
        "first_tx": None,
        "last_tx": None,
        "token_name": None,
        "token_symbol": None,
        "token_decimals": 18
    }

    if not transactions:
        return stats

    # Get token info from first transaction
    first_tx = transactions[0]
    stats["token_name"] = first_tx.get("tokenName", "Unknown")
    stats["token_symbol"] = first_tx.get("tokenSymbol", "Unknown")
    stats["token_decimals"] = int(first_tx.get("tokenDecimal", 18))

    wallet_lower = WALLET_ADDRESS.lower()

    for tx in transactions:
        # Parse amount with decimals
        value = int(tx["value"]) / (10 ** stats["token_decimals"])

        # Parse timestamp
        timestamp = int(tx["timeStamp"])
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

        # Track first and last transaction
        if stats["first_tx"] is None:
            stats["first_tx"] = datetime.fromtimestamp(timestamp)
        stats["last_tx"] = datetime.fromtimestamp(timestamp)

        # Determine if received or sent
        from_addr = tx["from"].lower()
        to_addr = tx["to"].lower()

        if to_addr == wallet_lower:
            # Received
            stats["total_received"] += value
            stats["unique_senders"].add(from_addr)
        elif from_addr == wallet_lower:
            # Sent
            stats["total_sent"] += value
            stats["unique_receivers"].add(to_addr)

        # Aggregate by date
        stats["transactions_by_date"][date_str] += 1
        stats["volume_by_date"][date_str] += value

    return stats


def print_report(stats):
    """Print formatted report"""
    print("=" * 60)
    print("Basescan Token Transaction Report")
    print("=" * 60)
    print(f"\nWallet Address: {WALLET_ADDRESS}")
    print(f"Token Contract: {TOKEN_CONTRACT}")
    print(f"Token Name: {stats['token_name']}")
    print(f"Token Symbol: {stats['token_symbol']}")
    print(f"Token Decimals: {stats['token_decimals']}")

    print("\n" + "-" * 60)
    print("Summary Statistics")
    print("-" * 60)
    print(f"Total Transactions: {stats['total_transactions']}")
    print(f"Total Received: {stats['total_received']:,.6f} {stats['token_symbol']}")
    print(f"Total Sent: {stats['total_sent']:,.6f} {stats['token_symbol']}")
    print(f"Net Balance Change: {stats['total_received'] - stats['total_sent']:,.6f} {stats['token_symbol']}")
    print(f"Unique Senders: {len(stats['unique_senders'])}")
    print(f"Unique Receivers: {len(stats['unique_receivers'])}")

    if stats['first_tx'] and stats['last_tx']:
        print(f"\nFirst Transaction: {stats['first_tx'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last Transaction: {stats['last_tx'].strftime('%Y-%m-%d %H:%M:%S')}")

    if stats['transactions_by_date']:
        print("\n" + "-" * 60)
        print("Transactions by Date")
        print("-" * 60)
        for date in sorted(stats['transactions_by_date'].keys()):
            tx_count = stats['transactions_by_date'][date]
            volume = stats['volume_by_date'][date]
            print(f"{date}: {tx_count} tx, {volume:,.6f} {stats['token_symbol']}")

    print("\n" + "=" * 60)


def main():
    print(f"Fetching token transactions from Basescan...")
    print(f"Address: {WALLET_ADDRESS}")
    print(f"Token: {TOKEN_CONTRACT}\n")

    # Fetch all transactions
    all_transactions = []
    page = 1

    while True:
        transactions = get_token_transactions(
            WALLET_ADDRESS,
            TOKEN_CONTRACT,
            page=page
        )

        if not transactions:
            break

        all_transactions.extend(transactions)
        print(f"Fetched page {page}: {len(transactions)} transactions")

        if len(transactions) < 10000:
            break

        page += 1
        time.sleep(0.3)  # Rate limiting

    print(f"\nTotal transactions fetched: {len(all_transactions)}")

    # Analyze transactions
    stats = analyze_transactions(all_transactions)

    # Print report
    print_report(stats)

    return all_transactions, stats


if __name__ == "__main__":
    transactions, stats = main()
