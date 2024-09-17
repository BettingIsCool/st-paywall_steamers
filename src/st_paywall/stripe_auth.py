import streamlit as st
import stripe
import urllib.parse


def get_api_key() -> str:
    testing_mode = st.secrets.get("testing_mode", False)
    return (
        st.secrets["stripe_api_key_test"]
        if testing_mode
        else st.secrets["stripe_api_key"]
    )


def redirect_button(
    text: str,
    customer_email: str,
    color="#FD504D",
    payment_provider: str = "stripe",
):
    testing_mode = st.secrets.get("testing_mode", False)
    encoded_email = urllib.parse.quote(customer_email)
    if payment_provider == "stripe":
        stripe.api_key = get_api_key()
        stripe_link = (
            st.secrets["stripe_link_test"]
            if testing_mode
            else st.secrets["stripe_link"]
        )
        button_url = f"{stripe_link}?prefilled_email={encoded_email}"
    elif payment_provider == "bmac":
        button_url = f"{st.secrets['bmac_link']}"
    else:
        raise ValueError("payment_provider must be 'stripe' or 'bmac'")

    st.sidebar.markdown(
        f"""
    <a href="{button_url}" target="_blank">
        <div style="
            display: inline-block;
            padding: 0.5em 1em;
            color: #FFFFFF;
            background-color: {color};
            border-radius: 3px;
            text-decoration: none;">
            {text}
        </div>
    </a>
    """,
        unsafe_allow_html=True,
    )


def is_active_customer(email: str) -> bool:
    product_id = st.secrets["stripe_product_id"]
    is_active = False
    customers = stripe.Customer.list(email=email)
    if len(customers.data) > 0:
        for customer in customers.auto_paging_iter():
            subscriptions = stripe.Subscription.list(customer=customer.id)
            for subscription in subscriptions.auto_paging_iter():
                if subscription['plan']['active'] and subscription['plan']['product'] == product_id:
                    is_active = True

    st.session_state.subscriptions = is_active
    return is_active
