
import streamlit as st

from datetime import date
from decimal import Decimal, InvalidOperation


from database import (
    initialize_database,
    add_transaction,
    get_transactions,
    delete_transaction
)


# --------------------------------------------------
# APPLICATION SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Our Personal Budget Tracker <3",
    page_icon="💚",
    layout="wide"
)

initialize_database()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def format_euros(amount_cents):

    euros = Decimal(amount_cents) / 100

    return f"€{euros:,.2f}"


# --------------------------------------------------
# APPLICATION TITLE
# --------------------------------------------------

st.title("Our Personal Budget Tracker <3")

st.write("Welcome to our personal finance dashboard!")


# --------------------------------------------------
# ADD TRANSACTION FORM
# --------------------------------------------------

st.subheader("Add a transaction")

with st.form("transaction_form", clear_on_submit=True):

    transaction_type = st.selectbox(
        "Transaction type",
        ["Expense", "Income"]
    )

    description = st.text_input(
        "Description"
    )

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Housing",
            "Subscriptions",
            "Entertainment",
            "Salary",
            "Other"
        ]
    )

    amount = st.text_input(
        "Amount (€)",
        placeholder="25.50"
    )

    transaction_date = st.date_input(
        "Date",
        value=date.today()
    )

    submitted = st.form_submit_button(
        "Save transaction"
    )


    if submitted:

        try:

            euros = Decimal(amount.strip())

            if (
                not euros.is_finite()
                or euros <= 0
                or euros != euros.quantize(Decimal("0.01"))
            ):

                st.error(
                    "Enter a positive amount with at most two decimal places."
                )

            elif not description.strip():

                st.error(
                    "Please enter a description."
                )

            else:

                amount_cents = int(euros * 100)

                add_transaction(
                    transaction_date.isoformat(),
                    description.strip(),
                    category,
                    transaction_type,
                    amount_cents
                )

                st.success("Transaction saved successfully!")

        except InvalidOperation:

            st.error(
                "Please enter a valid amount, for example 25.50."
            )


# --------------------------------------------------
# RETRIEVE TRANSACTIONS
# --------------------------------------------------

transactions = get_transactions()


# --------------------------------------------------
# CONFIRM TRANSACTION DELETION
# --------------------------------------------------

@st.dialog("Confirm transaction deletion")
def confirm_delete_transaction(transaction_id):

    transaction = next(
        (
            transaction
            for transaction in transactions
            if transaction["id"] == transaction_id
        ),
        None
    )

    if transaction is None:
        st.error("Transaction not found.")
        return

    st.warning(
        "Are you sure you want to delete this transaction?"
    )

    st.write(f"**Description:** {transaction['description']}")

    st.write(
        f"**Amount:** {format_euros(transaction['amount_cents'])}"
    )

    st.write(
        f"**Type:** {transaction['transaction_type']}"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Cancel", use_container_width=True):
            st.rerun()

    with col2:

        if st.button(
            "Yes, delete",
            type="primary",
            use_container_width=True
        ):

            delete_transaction(transaction_id)

            st.rerun()

# --------------------------------------------------
# CALCULATE MONTHLY TOTALS
# --------------------------------------------------

current_month = date.today().strftime("%Y-%m")

monthly_transactions = [
    transaction
    for transaction in transactions
    if transaction["transaction_date"].startswith(current_month)
]

monthly_income = sum(
    transaction["amount_cents"]
    for transaction in monthly_transactions
    if transaction["transaction_type"] == "Income"
)

monthly_expenses = sum(
    transaction["amount_cents"]
    for transaction in monthly_transactions
    if transaction["transaction_type"] == "Expense"
)

monthly_net = monthly_income - monthly_expenses


# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------

st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Monthly Income",
        format_euros(monthly_income)
    )

with col2:

    st.metric(
        "Monthly Expenses",
        format_euros(monthly_expenses)
    )

with col3:

    st.metric(
        "Monthly Net",
        format_euros(monthly_net)
    )


# --------------------------------------------------
# TRANSACTION HISTORY
# --------------------------------------------------

st.divider()

st.subheader("Transaction History")

if transactions:

    display_transactions = []

    for transaction in transactions:

        sign = (
            "+"
            if transaction["transaction_type"] == "Income"
            else "-"
        )

        display_transactions.append({

            "Date": transaction["transaction_date"],

            "Description": transaction["description"],

            "Category": transaction["category"],

            "Type": transaction["transaction_type"],

            "Amount": (
                sign
                + format_euros(transaction["amount_cents"])
            )

        })

    st.dataframe(
        display_transactions,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No transactions recorded yet.")


# --------------------------------------------------
# DELETE TRANSACTION
# --------------------------------------------------

st.divider()

st.subheader("Remove a transaction")

if transactions:

    selected_transaction_id = st.selectbox(
        "Select the transaction you want to delete",

        options=[
            transaction["id"]
            for transaction in transactions
        ],

        format_func=lambda transaction_id: next(
            (
                f'{transaction["description"]} '
                f'({transaction["transaction_type"]}, '
                f'{format_euros(transaction["amount_cents"])})'
            )
            for transaction in transactions
            if transaction["id"] == transaction_id
        )
    )

    if st.button("Delete selected transaction", type="primary"):

        confirm_delete_transaction(selected_transaction_id)

else:

    st.info("No transactions to delete.")
