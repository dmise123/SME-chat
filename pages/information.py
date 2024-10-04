import streamlit as st
import pandas as pd
import os

# Path to the CSV file
csv_file_path = "docs/data.csv"

# Hide sidebar navigation items
st.markdown(
    """
    <style>
        [data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True
)

# Sidebar navigation
with st.sidebar:
    st.page_link("rag_app.py", label="Home")  # Adjust this to your main app file
    st.page_link("pages/information.py", label="Bakery Information")
    st.page_link("pages/profile.py", label="Profile")

# Load bakery data from CSV if it exists
def load_bakery_data():
    if os.path.exists(csv_file_path):
        try:
            bakery_data = pd.read_csv(csv_file_path)
            bakery_info = {
                'items': bakery_data['Item'].tolist(),
                'prices': bakery_data['Price'].tolist(),
                'working_hours': bakery_data['Working Hours'][0],
                'contact_info': bakery_data['Contact Info'][0],
                'location': bakery_data['Location'][0]
            }
        except pd.errors.ParserError as e:
            st.error(f"Error reading CSV file: {e}")
            # Default data if CSV is not readable
            bakery_info = {
                'items': ['Bread', 'Cake', 'Pastry'],
                'prices': [5.0, 20.0, 3.0],
                'working_hours': '8 AM - 6 PM',
                'contact_info': '123-456-7890',
                'location': '123 Bakery Street'
            }
    else:
        # Default bakery data if CSV does not exist
        bakery_info = {
            'items': ['Bread', 'Cake', 'Pastry'],
            'prices': [5.0, 20.0, 3.0],
            'working_hours': '8 AM - 6 PM',
            'contact_info': '123-456-7890',
            'location': '123 Bakery Street'
        }
    return bakery_info

# Function to save bakery information to CSV
def save_to_csv(bakery_info):
    num_items = len(bakery_info['items'])  # Number of items

    # Repeat the single values for "Working Hours," "Contact Info," and "Location"
    df = pd.DataFrame({
        'Item': bakery_info['items'],
        'Price': bakery_info['prices'],
        'Working Hours': [bakery_info['working_hours']] * num_items,
        'Contact Info': [bakery_info['contact_info']] * num_items,
        'Location': [bakery_info['location']] * num_items
    })
    df.to_csv(csv_file_path, index=False)
    st.success("Bakery information saved to CSV.")

# Function to edit bakery information
def edit_bakery_info():
    if 'bakery_info' not in st.session_state:
        st.session_state.bakery_info = load_bakery_data()

    bakery_info = st.session_state.bakery_info

    st.title("Manage Bakery Information")

    # CRUD for items and prices
    st.header("Items and Prices")
    
    # Display current items and prices
    for idx, (item, price) in enumerate(zip(bakery_info['items'], bakery_info['prices'])):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            new_item = st.text_input(f"Edit Item {idx+1}", value=item, key=f"edit_item_{idx}")
        with col2:
            new_price = st.number_input(f"Edit Price {idx+1}", value=price, key=f"edit_price_{idx}")
        with col3:
            if st.button(f"Delete {item}", key=f"delete_item_{idx}"):
                del bakery_info['items'][idx]
                del bakery_info['prices'][idx]  # Ensure the price is also deleted
                st.success(f"Deleted {item}")
                st.experimental_rerun()

        # Update item and price in session state
        bakery_info['items'][idx] = new_item
        bakery_info['prices'][idx] = new_price

    # Add new item and price
    st.subheader("Add New Item")
    new_item_name = st.text_input("New Item Name")
    new_item_price = st.number_input("New Item Price", min_value=0.0, value=0.0)
    if st.button("Add Item"):
        if new_item_name:
            bakery_info['items'].append(new_item_name)
            bakery_info['prices'].append(new_item_price)
            st.success(f"Added {new_item_name} at ${new_item_price:.2f}")
        else:
            st.warning("Please enter a valid item name.")

    st.header("General Information")
    bakery_info['working_hours'] = st.text_input("Working Hours:", bakery_info['working_hours'])
    bakery_info['contact_info'] = st.text_input("Contact Information:", bakery_info['contact_info'])
    bakery_info['location'] = st.text_input("Location:", bakery_info['location'])

    if st.button("Update General Information"):
        st.success("General information updated!")

    # Save changes to CSV
    if st.button("Save Changes"):
        save_to_csv(bakery_info)

# Call the function to edit bakery information
edit_bakery_info()
