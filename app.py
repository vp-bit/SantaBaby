import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import validators

def validate_url(url):
    return validators.url(url)

# Google Sheets Authentication
def authenticate_google_sheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_file:
        st.error("Google Sheets credentials not found. Please set the GOOGLE_APPLICATION_CREDENTIALS environment variable.")
        return None
    creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
    client = gspread.authorize(creds)
    return client

# Load the Google Sheet
def load_sheet(client, sheet_name):
    sheet = client.open(sheet_name)
    return sheet

# Fetch Role of the User
def get_user_role():
    sheet = st.session_state["sheet"]
    name = st.session_state["name"]
    pin = st.session_state["pin"]
    users_sheet = sheet.worksheet("Users")
    users = users_sheet.get_all_records()
    i = 0
    while i < len(users):
        u = users[i]
        if u["Name"] == name and str(u["PIN"]) == pin:
            st.session_state["role"] = u["Role"]
            break
        i = i + 1



# Add a Wish (Child)
def add_wish():#name, wish):
    name = st.session_state["name"]
    wish = st.session_state["wish"]
    details = st.session_state["details"] 
    url = st.session_state["url"] 
    if "sheet" in st.session_state and st.session_state["sheet"]:
        try:
            wishes_sheet = st.session_state["sheet"].worksheet("Wishes")
            wishes_sheet.append_row([wish, details, url, name, "Pending"])
            st.session_state["wish"] = ""  # Clear the input after submission
            st.session_state["details"] = ""  # Clear the input after submission
            st.session_state["url"] = ""  # Clear the input after submission
            st.success("Your wish has been added!")
        except Exception as e:
            st.error(f"Error adding wish: {e}")
    else:
        st.error("Sheet is not initialized.")

# View Wishes (Santa)
def view_wishes(sheet):
    wishes_sheet = sheet.worksheet("Wishes")
    return wishes_sheet.get_all_records()

# Update Wish Status (Santa)
def update_wish_status():
    wish_no = st.session_state["wish_no"]
    name = st.session_state["name"]
    wishes_sheet = st.session_state["sheet"].worksheet("Wishes")
    wishes_sheet.update_cell(wish_no , 5, "Claimed")
    wishes_sheet.update_cell(wish_no , 7, name)

# Complete Wish (Santa)
def complete_wish():
    wish_no = st.session_state["wish_no"]
    name = st.session_state["name"]
    wishes_sheet = st.session_state["sheet"].worksheet("Wishes")
    wishes_sheet.update_cell(wish_no , 5, "Purchased")

# Initialize Session State Variables
if "name" not in st.session_state:
    st.session_state["name"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "sheet" not in st.session_state:
    st.session_state["sheet"] = None
if "wish" not in st.session_state:
    st.session_state["wish"] = ""
if "details" not in st.session_state:
    st.session_state["details"] = ""
if "url" not in st.session_state:
    st.session_state["url"] = ""
if "submit_wish_clicked" not in st.session_state:
    st.session_state["submit_wish_clicked"] = False

# Streamlit App
#st.title("Gift Registry - Real Rulers of Rough Hollow") #make group name dynamic

# Google Sheets setup
if "client" not in st.session_state:
    st.session_state["client"] = authenticate_google_sheets()

if st.session_state["client"] and st.session_state["sheet"] is None:
    st.session_state["sheet"] = load_sheet(st.session_state["client"], "Gift Registry") 

st.markdown(
"""
<style>
.stButton button {
    font-size: 12px;
    padding: 5px 10px;
    background-color: #007bff;
    color: white;
    border-radius: 5px;
    border: none;
}
.stButton button:hover {
    background-color: #0056b3;
}
</style>
""",
unsafe_allow_html=True
)

# Login section
st.sidebar.title("Gift Registry")
if st.session_state["role"]:
    st.sidebar.markdown(f"Logged in as: **{st.session_state['name']}**")
    st.sidebar.markdown(f"Role: **{st.session_state['role']}**")
    if st.sidebar.button("Logout"):
        st.session_state["name"] = None
        st.session_state["role"] = None
        st.rerun()
else:
    st.sidebar.write("Please log in.")

if st.session_state["role"] is None:
    if st.session_state["sheet"]:
        users_sheet = st.session_state["sheet"].worksheet("Users")
        users = users_sheet.col_values(1)[1:]  # Assuming "Name" is in the first column
        st.write("### Welcome to the Gift Registry")
        st.write("Please log in to view or manage your wishes.")

        st.session_state["name"] = st.selectbox("Select your name:", options=users)
        st.session_state["pin"] = st.text_input("Enter your PIN:", type="password")
        #st.session_state["role"] = "Admin"

        if st.button("Login"):
            get_user_role()
            if st.session_state["role"]:
                st.rerun()
            else:
                st.error("Invalid name or PIN. Please try again.")
            

# Role-specific actions
else:
    role = st.session_state["role"]
    name = st.session_state["name"]

    status_icon = {"Pending": "⏳", "Claimed": "🎁", "Purchased": "🛍️"}



    if role:
        #st.write(f"Welcome, {name}! Role: {role}")

        if role == "Wishmaker":
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image("images/wishlist.png", width=150)
            with col2:
                #st.markdown("# Santa's Dashboard 🎅")
                st.header(f"{name}'s wishes")

            # Input field for wish
            st.session_state["wish"] = st.text_input("Enter your wish:", value=st.session_state["wish"])
            st.session_state["details"] = st.text_area("Enter details about the wish:", value=st.session_state["details"])
            st.session_state["url"] = st.text_input("Enter a URL for the wish (optional):", value=st.session_state["url"])
            
            # Submit button
            if st.button("Submit Wish"):
                #if st.session_state["wish"]:
                    add_wish()#name, st.session_state["wish"])
                    st.rerun()
                    #st.session_state["wish"] = ""  # Clear the input after submission
                    #st.experimental_rerun()  # Force a rerun to refresh the state
                #else:
                #    st.error("Please enter a wish before submitting.")

            #st.header(f"My Wishes")
            wishes = view_wishes(st.session_state["sheet"])
            with st.expander("My Wishes", expanded=True):
                for idx, wish in enumerate(wishes, start=2):
                    if wish['User'] == name:
                        url = wish['Link']
                        details = ""
                        if wish['Details'] != "":
                            details = " - " +wish['Details'] + " "
                        if validate_url(url):
                            st.write(f"{idx-1}: {status_icon[wish['Status']]} [{wish['Name']}]({url}){details}")
                        else:
                            st.write(f"{idx-1}: {status_icon[wish['Status']]} {wish['Name']}{details}")

        elif role == "Santa":
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image("images/santa.png", width=150)
            with col2:
                #st.markdown("# Santa's Dashboard 🎅")
                st.header(f"{name}'s Santa Workshop")           

            wishes = view_wishes(st.session_state["sheet"])
            with st.expander("Unclaimed Wishes", expanded=True):
                for idx, wish in enumerate(wishes, start=2):
                    if wish['Mom'] != name and wish['Status'] == "Pending":
                        url = wish['Link']
                        details = ""
                        if wish['Details'] != "":
                            details = " - " +wish['Details'] + " "
                        if validate_url(url):
                            st.write(f"{idx-1}: {wish['User']} would like a/an [{wish['Name']}]({url}){details}")
                        else:
                            st.write(f"{idx-1}: {wish['User']} would like a/an {wish['Name']}{details}")

                        #new_status = st.selectbox(
                        #    f"Update status for {wish['Name']}:", ["Pending", "Claimed"], key=idx
                        #)
                        if st.button(f"Claim Wish #{idx-1}"):
                            st.session_state["wish_no"] = idx
                            update_wish_status()
                            st.rerun()

            #st.header(f"To Do")
            wishes = view_wishes(st.session_state["sheet"])
            with st.expander("To Do", expanded=True):
                for idx, wish in enumerate(wishes, start=2):
                    if wish['Santa'] == name and wish['Status'] == "Claimed":
                        url = wish['Link']
                        details = ""
                        if wish['Details'] != "":
                            details = " - " +wish['Details'] + " "

                            col1, col2 = st.columns([3, 1])
                            with col1:
                                if validate_url(url):
                                    st.markdown(f"{idx-1}: {wish['User']} would like a/an [{wish['Name']}]({url}){details}")
                                else:
                                    st.markdown(f"{idx-1}: {wish['User']} would like a/an {wish['Name']}{details}")

                            with col2:
                                #st.write("")  # Spacer

                                if st.button(f"Bought Gift #{idx-1}"):
                                    st.session_state["wish_no"] = idx
                                    complete_wish()
                                    st.rerun()

            #st.header(f"Compeleted List")
            wishes = view_wishes(st.session_state["sheet"])
            with st.expander("Completed List", expanded=True):
                for idx, wish in enumerate(wishes, start=2):
                    if wish['Santa'] == name and wish['Status'] == "Purchased":
                        url = wish['Link']
                        details = ""
                        if wish['Details'] != "":
                            details = " - " +wish['Details'] + " "
                        if validate_url(url):
                            st.write(f"{idx-1}: {wish['User']} would like a/an [{wish['Name']}]({url}){details}")
                        else:
                            st.write(f"{idx-1}: {wish['User']} would like a/an {wish['Name']}{details}")
              

        elif role == "Admin":
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image("images/admin.png", width=150)
            with col2:
                #st.markdown("# Santa's Dashboard 🎅")
                st.header("Admin Controls")
            st.write("Admins can view and manage all data.")
            wishes = view_wishes(st.session_state["sheet"])
            with st.expander("List", expanded=True):
                for idx, wish in enumerate(wishes, start=2):
                    url = wish['Link']
                    details = ""
                    if wish['Details'] != "":
                        details = " - " +wish['Details'] + " "
                    if validate_url(url):
                        st.write(f"{idx-1}: {status_icon[wish['Status']]} {wish['User']}: [{wish['Name']}]({url}){details} ({wish['Status']})")
                    else:
                        st.write(f"{idx-1}: {status_icon[wish['Status']]} {wish['User']}: [{wish['Name']}{details} ({wish['Status']})")









