# services/data_generator.py
import json, uuid, random
from faker import Faker
from datetime import datetime, timedelta
from pathlib import Path

fake = Faker("en_IN")  # use Indian locale for ₹ formatting

CATEGORIES = ["Food", "Shopping", "Rent", "Salary", "Utilities", "Entertainment", "Travel", "Others"]

def gen_txn(user_id, n=200, start_date="2024-01-01", out_path="data/transactions.json"):
    start = datetime.fromisoformat(start_date)
    txns = []
    balance = 100000  # starting balance for demo
    for i in range(n):
        delta_days = random.randint(0, 365)
        date = (start + timedelta(days=delta_days)).date().isoformat()
        amount = random.randint(50, 55000)
        ttype = random.choices(["Debit","Credit"], weights=[0.7,0.3])[0]
        category = random.choice(CATEGORIES)
        # Prevent negative balance for debits
        if ttype == "Debit" and balance - amount < 0:
            continue  # Skip this transaction to avoid negative balance
        if ttype == "Debit":
            balance -= amount
        else:
            balance += amount
        txn = {
            "id": f"txn_{user_id}_{i}",
            "userId": user_id,
            "date": date,
            "description": fake.sentence(nb_words=4),
            "amount": amount,
            "type": ttype,
            "category": category,
            "balance": balance
        }
        txns.append(txn)
    # append or create
    p = Path(out_path)
    if p.exists():
        existing = json.loads(p.read_text())
    else:
        existing = []
    existing.extend(txns)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(existing, indent=2))
    print(f"Wrote {len(txns)} txns for {user_id} to {out_path}")

if __name__ == "__main__":
    # generate for 3 users quickly
    gen_txn("user_1", n=200)
    gen_txn("user_2", n=200)
    gen_txn("user_3", n=200)