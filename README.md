# Banking App
 
A simple terminal-based banking app using SQLite. One file, no dependencies
beyond the Python standard library.
 
## Requirements
- Python 3.8+
 
## Run
```bash
python3 main.py
```
 
On first run, `bank.db` is created automatically in the current directory.
 
## Features
- Create accounts (name + initial deposit)
- Deposit / withdraw (with balance validation)
- Check balance
- List accounts
- Delete accounts
- All actions are logged in a `transactions` table
