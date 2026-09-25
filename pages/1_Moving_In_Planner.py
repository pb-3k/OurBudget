
import streamlit as st

from datetime import date
from decimal import Decimal, InvalidOperation
from math import ceil

from database import (
    initialize_database,
    add_planned_item,
    get_planned_items,
    delete_planned_item
)


st.set_page_config(
    page_title="Our Moving-In Planner",
    page_icon="🏡",
    layout="wide"
)

initialize_database()

st.title("Our Moving-In Planner 🏡")

st.write(
    "Let's plan our future home together! 💚"
)

# --------------------------------------------------
# DISPLAY SUCCESS MESSAGE
# --------------------------------------------------

if st.session_state.pop("planned_item_saved", False):

    st.success("Added to our moving-in plan!")
# --------------------------------------------------
# SELECT PLANNING MONTH
# --------------------------------------------------

selected_date = st.date_input(
    "Which month are we planning?",
    value=date.today().replace(day=1)
)

plan_month = selected_date.strftime("%Y-%m")


            
# --------------------------------------------------
# RETRIEVE PLANNED ITEMS
# --------------------------------------------------

planned_items = get_planned_items(plan_month)

# --------------------------------------------------
# CALCULATE PLANNED TOTALS
# --------------------------------------------------

monthly_income = 0

monthly_expenses = 0

one_time_income = 0

one_time_expenses = 0


for item in planned_items:

    amount = item["amount_cents"]

    if item["frequency"] == "Monthly":

        if item["item_type"] == "Income":

            monthly_income += amount

        else:

            monthly_expenses += amount

    else:

        if item["item_type"] == "Income":

            one_time_income += amount

        else:

            one_time_expenses += amount


monthly_remaining = (
    monthly_income - monthly_expenses
)

moving_month_remaining = (
    monthly_remaining
    + one_time_income
    - one_time_expenses
)

# --------------------------------------------------
# FIND CURRENT PLANNED RENT
# --------------------------------------------------

planned_rent = sum(
    item["amount_cents"]
    for item in planned_items
    if (
        item["category"] == "Rent"
        and item["item_type"] == "Expense"
        and item["frequency"] == "Monthly"
    )
)
# --------------------------------------------------
# FORMATTING
# --------------------------------------------------

def format_euros(amount_cents):

    euros = Decimal(abs(amount_cents)) / 100

    sign = "-" if amount_cents < 0 else ""

    return f"{sign}€{euros:,.2f}"


# --------------------------------------------------
# DOUBLE SAFETY MODE - PLANNED ITEM DELETION
# --------------------------------------------------

@st.dialog("Confirm planned item deletion")
def confirm_delete_planned_item(item_id):

    # Find the selected planned item
    item = next(
        (
            item
            for item in planned_items
            if item["id"] == item_id
        ),
        None
    )

    if item is None:
        st.error("Planned item not found.")
        return

    # ----------------------------------------------
    # CUSTOM WARNING MESSAGES
    # ----------------------------------------------

    category = item["category"]
    item_type = item["item_type"]
    frequency = item["frequency"]

    if category == "Rent" and item_type == "Expense":

        warning_title = "🏡 You're removing a housing expense!"

        warning_message = (
            "Removing this rent entry will change your "
            "projected household expenses and may make "
            "your remaining budget appear higher."
        )

    elif category == "Salary" and item_type == "Income":

        warning_title = "💰 You're removing expected income!"

        warning_message = (
            "Removing this salary entry will reduce "
            "your projected household income and "
            "change your remaining budget."
        )

    elif category == "Deposit" and item_type == "Expense":

        warning_title = "🔑 You're removing a moving-in deposit!"

        warning_message = (
            "This deposit may represent an important "
            "upfront moving cost. Removing it will "
            "change your moving-in budget."
        )

    elif frequency == "One-time" and item_type == "Expense":

        warning_title = "📦 You're removing a one-time expense!"

        warning_message = (
            "This item represents a planned one-time "
            "purchase or moving expense. Removing it "
            "will change your moving-in budget."
        )

    else:

        warning_title = "⚠️ Delete this planned item?"

        warning_message = (
            "This item will be permanently removed "
            "from your moving-in plan."
        )

    # ----------------------------------------------
    # DISPLAY CONFIRMATION MESSAGE
    # ----------------------------------------------

    st.warning(warning_title)

    st.write(warning_message)

    st.divider()

    # ----------------------------------------------
    # DISPLAY ITEM DETAILS
    # ----------------------------------------------

    st.write(
        f"**Description:** {item['description']}"
    )

    st.write(
        f"**Amount:** {format_euros(item['amount_cents'])}"
    )

    st.write(
        f"**Category:** {category}"
    )

    st.write(
        f"**Type:** {item_type}"
    )

    st.write(
        f"**Frequency:** {frequency}"
    )

    st.divider()

    # ----------------------------------------------
    # CONFIRMATION BUTTONS
    # ----------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Cancel 💚",
            use_container_width=True
        ):

            st.rerun()

    with col2:

        if st.button(
            "Yes, delete",
            type="primary",
            use_container_width=True
        ):

            delete_planned_item(item_id)

            st.rerun()
# --------------------------------------------------
# FINANCIAL OVERVIEW
# --------------------------------------------------

st.divider()

st.subheader("Our projected household budget")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Expected Monthly Income",
        format_euros(monthly_income)
    )

with col2:

    st.metric(
        "Expected Monthly Expenses",
        format_euros(monthly_expenses)
    )

with col3:

    st.metric(
        "Monthly Remaining",
        format_euros(monthly_remaining)
    )


st.divider()

st.subheader("Moving-in month")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "One-time Moving Expenses",
        format_euros(one_time_expenses)
    )

with col2:

    st.metric(
        "Moving-month Remaining",
        format_euros(moving_month_remaining)
    )

# --------------------------------------------------
# OUR MOVING-IN SAVINGS FUND
# --------------------------------------------------

st.divider()

st.subheader("Our Moving-In Savings Fund 💚")

st.write(
    "Estimate how much money we want to have saved before moving day."
)

# --------------------------------------------------
# SAVINGS GOAL SETTINGS
# --------------------------------------------------

st.caption("Savings goal settings")

include_first_month_rent = st.checkbox(
    "Include first month's rent in the goal",
    value=True
)

settings_col1, settings_col2 = st.columns(
    2,
    gap="large"
)

with settings_col1:

    emergency_buffer_euros = st.number_input(
        "Emergency buffer (€)",
        min_value=0.0,
        value=300.00,
        step=50.0,
        format="%.2f"
    )

with settings_col2:

    already_saved_euros = st.number_input(
        "Already saved together (€)",
        min_value=0.0,
        value=0.00,
        step=50.0,
        format="%.2f"
    )


# --------------------------------------------------
# CALCULATE SAVINGS GOAL
# --------------------------------------------------

base_goal_cents = one_time_expenses

if include_first_month_rent:

    base_goal_cents += planned_rent

emergency_buffer_cents = int(
    Decimal(str(emergency_buffer_euros)) * 100
)

already_saved_cents = int(
    Decimal(str(already_saved_euros)) * 100
)

savings_goal_cents = (
    base_goal_cents + emergency_buffer_cents
)

remaining_to_save_cents = max(
    savings_goal_cents - already_saved_cents,
    0
)

if savings_goal_cents > 0:

    progress_ratio = min(
        already_saved_cents / savings_goal_cents,
        1
    )

else:

    progress_ratio = 0

progress_percent = int(progress_ratio * 100)


# --------------------------------------------------
# SAVINGS FUND VISUAL OVERVIEW
# --------------------------------------------------

with st.container(border=True):

    st.markdown("#### Our savings progress 🏡")

    goal_col1, goal_col2, goal_col3 = st.columns(3)

    with goal_col1:

        st.metric(
            "Savings Goal",
            format_euros(savings_goal_cents)
        )

    with goal_col2:

        st.metric(
            "Already Saved",
            format_euros(already_saved_cents)
        )

    with goal_col3:

        st.metric(
            "Still Needed",
            format_euros(remaining_to_save_cents)
        )

    st.divider()

    st.progress(progress_percent)

    st.caption(
        f"{progress_percent}% of our goal reached."
    )

    # ----------------------------------------------
    # SAVINGS STATUS MESSAGE
    # ----------------------------------------------

    if savings_goal_cents == 0:

        st.info(
            "Add planned moving expenses to calculate "
            "your savings goal. 💚"
        )

    elif remaining_to_save_cents == 0:

        st.success(
            "You've already reached your current "
            "moving-in savings goal! 💚"
        )

    elif monthly_remaining > 0:

        months_to_goal = ceil(
            remaining_to_save_cents / monthly_remaining
        )

        st.info(
            f"If you save your projected monthly remaining "
            f"amount, you could reach this goal in about "
            f"{months_to_goal} month(s)."
        )

    else:

        st.warning(
            "Your current monthly plan does not leave "
            "money remaining for savings yet."
        )

# --------------------------------------------------
# PLANNED ITEMS TABLE
# --------------------------------------------------

st.divider()

st.subheader("Our planned items")

if planned_items:

    display_items = []

    for item in planned_items:

        sign = (
            "+"
            if item["item_type"] == "Income"
            else "-"
        )

        display_items.append({

            "Description": item["description"],

            "Category": item["category"],

            "Type": item["item_type"],

            "Frequency": item["frequency"],

            "Amount": (
                sign
                + format_euros(item["amount_cents"])
            )

        })

    st.dataframe(
        display_items,
        use_container_width=True,
        hide_index=True,
        height="content"
    )

else:

    st.info(
        "No planned items for this month yet."
    )
# --------------------------------------------------
# ADD PLANNED ITEM
# --------------------------------------------------

with st.expander("➕ Add a planned item", expanded=False):

    with st.form("planned_item_form", clear_on_submit=True):

        item_type = st.selectbox(
            "Income or expense?",
            ["Expense", "Income"]
        )

        description = st.text_input(
            "Description",
            placeholder="e.g. Apartment rent"
        )

        category = st.selectbox(
            "Category",
            [
                "Rent",
                "Utilities",
                "Groceries",
                "Internet",
                "Household",
                "Furniture",
                "Deposit",
                "Moving",
                "Salary",
                "Savings",
                "Other"
            ]
        )

        frequency = st.selectbox(
            "Frequency",
            ["Monthly", "One-time"]
        )

        amount = st.text_input(
            "Expected amount (€)",
            placeholder="700.00"
        )

        submitted = st.form_submit_button(
            "Add to our plan 💚"
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

                    add_planned_item(
                        plan_month,
                        description.strip(),
                        category,
                        item_type,
                        frequency,
                        amount_cents
                    )

                    st.session_state["planned_item_saved"] = True

                    st.rerun()

            except InvalidOperation:

                st.error(
                    "Please enter a valid amount."
                )    
# --------------------------------------------------
# APARTMENT RENT COMPARISON
# --------------------------------------------------

st.divider()

with st.expander("🏡 Compare apartment rent", expanded=False):

    st.write(
        "Try changing the rent to see how it affects "
        "our projected monthly budget."
    )

    alternative_rent = st.number_input(
        "Alternative monthly rent (€)",
        min_value=0.0,
        value=float(planned_rent / 100),
        step=25.0,
        format="%.2f"
    )

    alternative_rent_cents = int(
        Decimal(str(alternative_rent)) * 100
    )

    alternative_remaining = (
        monthly_remaining
        + planned_rent
        - alternative_rent_cents
    )

    st.metric(
        "Remaining with this apartment",
        format_euros(alternative_remaining)
    )
# --------------------------------------------------
# DELETE PLANNED ITEM
# --------------------------------------------------

st.divider()

with st.expander("🗑️ Remove a planned item", expanded=False):

    if planned_items:

        selected_item_id = st.selectbox(
            "Select the item you want to delete",

            options=[
                item["id"]
                for item in planned_items
            ],

            format_func=lambda item_id: next(
                (
                    f'{item["description"]} '
                    f'({item["item_type"]}, '
                    f'{format_euros(item["amount_cents"])})'
                )
                for item in planned_items
                if item["id"] == item_id
            )
        )

        if st.button("Delete selected item", type="primary"):

            confirm_delete_planned_item(selected_item_id)

    else:

        st.info("No planned items to delete.")