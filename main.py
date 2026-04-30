import sqlite3
 
DB_FILE = "bank.db"
 
 
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
 
 
def init_db():
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0
            );
 
            CREATE TABLE IF NOT EXISTS transactions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                kind       TEXT NOT NULL CHECK (kind IN ('deposit','withdraw','open')),
                amount     REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            );
            """
        )
 
 
# ---------- operations ----------
 
def create_account(name, initial_deposit):
    if initial_deposit < 0:
        raise ValueError("Initial deposit cannot be negative.")
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO accounts (name, balance) VALUES (?, ?)",
            (name, initial_deposit),
        )
        account_id = cur.lastrowid
        conn.execute(
            "INSERT INTO transactions (account_id, kind, amount) VALUES (?, 'open', ?)",
            (account_id, initial_deposit),
        )
        return account_id
 
 
def deposit(account_id, amount):
    if amount <= 0:
        raise ValueError("Deposit must be positive.")
    with get_db() as conn:
        cur = conn.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount, account_id),
        )
        if cur.rowcount == 0:
            raise ValueError(f"Account {account_id} not found.")
        conn.execute(
            "INSERT INTO transactions (account_id, kind, amount) VALUES (?, 'deposit', ?)",
            (account_id, amount),
        )
 
 
def withdraw(account_id, amount):
    if amount <= 0:
        raise ValueError("Withdrawal must be positive.")
    with get_db() as conn:
        row = conn.execute(
            "SELECT balance FROM accounts WHERE id = ?", (account_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Account {account_id} not found.")
        if row[0] < amount:
            raise ValueError("Insufficient funds.")
        conn.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, account_id),
        )
        conn.execute(
            "INSERT INTO transactions (account_id, kind, amount) VALUES (?, 'withdraw', ?)",
            (account_id, amount),
        )
 
 
def get_balance(account_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT name, balance FROM accounts WHERE id = ?", (account_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Account {account_id} not found.")
        return row  # (name, balance)
 
 
def list_accounts():
    with get_db() as conn:
        return conn.execute(
            "SELECT id, name, balance FROM accounts ORDER BY id"
        ).fetchall()
 
 
def delete_account(account_id):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        if cur.rowcount == 0:
            raise ValueError(f"Account {account_id} not found.")
 
 
# ---------- menu UI ----------
 
def prompt_int(msg):
    return int(input(msg).strip())
 
 
def prompt_float(msg):
    return float(input(msg).strip())
 
 
def menu():
    actions = {
        "1": ("Create account", do_create),
        "2": ("Deposit", do_deposit),
        "3": ("Withdraw", do_withdraw),
        "4": ("Check balance", do_balance),
        "5": ("List accounts", do_list),
        "6": ("Delete account", do_delete),
        "0": ("Quit", None),
    }
    while True:
        print("\n=== Banking App ===")
        for key, (label, _) in actions.items():
            print(f"  {key}) {label}")
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Bye!")
            return
        action = actions.get(choice)
        if not action:
            print("Invalid choice.")
            continue
        try:
            action[1]()
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

def do_create():
    name = input("Account holder name: ").strip()
    if not name:
        raise ValueError("Name required.")
    deposit_amt = prompt_float("Initial deposit: ")
    acct_id = create_account(name, deposit_amt)
    print(f"Created account #{acct_id} for {name} with balance {deposit_amt:.2f}.")
    print(f"Your account number is {acct_id} — keep it for deposits/withdrawals.")
 
 
def do_deposit():
    acct_id = prompt_int("Account id: ")
    amount = prompt_float("Amount to deposit: ")
    deposit(acct_id, amount)
    _, balance = get_balance(acct_id)
    print(f"Deposited {amount:.2f}. New balance: {balance:.2f}.")
 
 
def do_withdraw():
    acct_id = prompt_int("Account id: ")
    amount = prompt_float("Amount to withdraw: ")
    withdraw(acct_id, amount)
    _, balance = get_balance(acct_id)
    print(f"Withdrew {amount:.2f}. New balance: {balance:.2f}.")
 
 
def do_balance():
    acct_id = prompt_int("Account id: ")
    name, balance = get_balance(acct_id)
    print(f"Account #{acct_id} ({name}): {balance:.2f}")
 
 
def do_list():
    rows = list_accounts()
    if not rows:
        print("No accounts yet.")
        return
    print(f"{'ID':<5}{'Name':<25}{'Balance':>12}")
    print("-" * 42)
    for acct_id, name, balance in rows:
        print(f"{acct_id:<5}{name:<25}{balance:>12.2f}")
 
 
def do_delete():
    acct_id = prompt_int("Account id to delete: ")
    confirm = input(f"Delete account #{acct_id}? (y/N): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return
    delete_account(acct_id)
    print(f"Account #{acct_id} deleted.")
 
 
if __name__ == "__main__":
    init_db()
    menu()

README.md
