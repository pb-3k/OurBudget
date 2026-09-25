
import sqlite3
from pathlib import Path


# Location of our database file
DB_PATH = Path(__file__).resolve().parent / "data" / "budget.db"


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

def initialize_database():

    # Create the data folder if it does not exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to our database
    connection = sqlite3.connect(DB_PATH)

    # Create the transactions table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            transaction_date TEXT NOT NULL,

            description TEXT NOT NULL,

            category TEXT NOT NULL,

            transaction_type TEXT NOT NULL
                CHECK(transaction_type IN ('Income', 'Expense')),

            amount_cents INTEGER NOT NULL
                CHECK(amount_cents > 0)

        )
    """)

    # Create the planned items table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS planned_items (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            plan_month TEXT NOT NULL,

            description TEXT NOT NULL,

            category TEXT NOT NULL,

            item_type TEXT NOT NULL
                CHECK(item_type IN ('Income', 'Expense')),

            frequency TEXT NOT NULL
                CHECK(frequency IN ('Monthly', 'One-time')),

            amount_cents INTEGER NOT NULL
                CHECK(amount_cents > 0)

        )
    """)
    # Save database changes
    connection.commit()

    # Close the connection
    connection.close()


# --------------------------------------------------
# ADD TRANSACTION
# --------------------------------------------------

def add_transaction(
    transaction_date,
    description,
    category,
    transaction_type,
    amount_cents
):

    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        INSERT INTO transactions (
            transaction_date,
            description,
            category,
            transaction_type,
            amount_cents
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        transaction_date,
        description,
        category,
        transaction_type,
        amount_cents
    ))

    connection.commit()
    connection.close()


# --------------------------------------------------
# GET TRANSACTIONS
# --------------------------------------------------

def get_transactions():

    connection = sqlite3.connect(DB_PATH)

    # Return rows that behave like dictionaries
    connection.row_factory = sqlite3.Row

    cursor = connection.execute("""
        SELECT *
        FROM transactions
        ORDER BY transaction_date DESC, id DESC
    """)

    transactions = [
        dict(row) for row in cursor.fetchall()
    ]

    connection.close()


    

    return transactions

# --------------------------------------------------
# ADD PLANNED ITEM
# --------------------------------------------------

def add_planned_item(
    plan_month,
    description,
    category,
    item_type,
    frequency,
    amount_cents
):

    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        INSERT INTO planned_items (
            plan_month,
            description,
            category,
            item_type,
            frequency,
            amount_cents
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        plan_month,
        description,
        category,
        item_type,
        frequency,
        amount_cents
    ))

    connection.commit()

    connection.close()
    
# --------------------------------------------------
# GET PLANNED ITEMS
# --------------------------------------------------

def get_planned_items(plan_month):

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    cursor = connection.execute("""
        SELECT *
        FROM planned_items
        WHERE plan_month = ?
        ORDER BY id DESC
    """, (plan_month,))

    planned_items = [
        dict(row) for row in cursor.fetchall()
    ]

    connection.close()

    return planned_items

# --------------------------------------------------
# DELETE PLANNED ITEM
# --------------------------------------------------

def delete_planned_item(item_id):

    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        DELETE FROM planned_items
        WHERE id = ?
    """, (item_id,))

    connection.commit()

    connection.close()
    
# --------------------------------------------------
# DELETE TRANSACTION
# --------------------------------------------------

def delete_transaction(transaction_id):

    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    connection.commit()

    connection.close()