import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import datetime, hashlib, json
from datetime import timedelta, date
from datetime import datetime as datetimedt
import bisect, pyautogui, time
import pygetwindow as gw

customerFilePath = "customerFile.txt"
staffFilePath = "staffFile.txt"
membershipFilePath = "membershipFile.txt"
sessionFilePath = "sessionFile.txt"

# Initialising Globals
global currentStaffAccessArray
currentStaffAccessArray = {}

# Staff Information Menu Update
def staffChangesUpdate(changeText):
    try:
        # Loading data from file
        with open(staffFilePath, 'r') as dataFile:
            data = json.load(dataFile)
    except FileNotFoundError:
        messagebox.showerror("Error", "Problem Retrieving File")

    staffUsername = currentStaffAccessArray["staffUsername"]
    staffName = currentStaffAccessArray["name"]
    date = datetime.datetime.now().strftime("%d-%m-%Y")
    time = datetime.datetime.now().strftime("%H:%M")
    
    newStaffChanges = {"staffUsername": staffUsername, "name": staffName, "date": date, "time": time, "changeMade": changeText}

    data["staffChanges"].append(newStaffChanges)

    # Saving data to file
    with open(staffFilePath, 'w') as dataFile:
        json.dump(data, dataFile, indent=4)

## Entry base functions
def onEntryClick(event, entry, defaultEntry):
    if entry.get() == defaultEntry:
        entry.delete(0, tk.END)
        entry.config(fg="#FFFFFF")

def onEntryUnclick(event, entry, defaultEntry):
    if entry.get().strip() == "":
        entry.delete(0, tk.END)
        entry.insert(0, defaultEntry)
        entry.config(fg="#DEDEDE", show="")

def onPasswordEntryClick(event, entry, defaultEntry):
    if entry.get() == defaultEntry:
        entry.delete(0, tk.END)
        entry.config(fg="#FFFFFF", show="*")

def onCursorHoverHand2(event):
    event.widget.configure(cursor="hand2")

def onCursorLeave(event):
    event.widget.configure(cursor="")

def fillEntry(entry, newEntry, defaultBool=False):
    entry.delete(0, tk.END)
    entry.insert(0, str(newEntry))
    if defaultBool:
        entry.config(fg="#DEDEDE", show="")

# Defining Updating of Scrollable Label
def scrollAreaUpdate(event, canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

## Validation
def isAlphaNumericHyphen(data):
    string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
    for i in range(len(data)):
        if data[i] not in string:
            return False
    
    return True

def valLengthRange(checkVar, lengthBegin, lengthEnd):
    if (lengthBegin <= len(checkVar.strip()) <= lengthEnd):
        return True
    else:
        return False

def valPostcode(post):
    post = post.strip()
    if len(post) == 8:
        if post[:2].isalpha() and post[2:4].isnumeric() and post[5].isnumeric() and post[6:].isalpha():
            return True
        else:
            return False
    else:
        return False

def valEmail(email):
    email = email.strip()
    ATcount = 0
    if (len(email) >= 5) and ("@" in email) and ("." in email):
        
        for i in range(len(email)):
            if email[i] == "@":
                ATIndex = i
                ATcount += 1
            if email[i] == ".":
                dotIndex = i
                
        if (dotIndex > ATIndex) and (ATcount == 1):
            if (ATIndex != 0) and (ATIndex != (len(email)-1)) and (dotIndex != 0) and (dotIndex != (len(email)-1)):
                if isAlphaNumericHyphen(email[ATIndex + 1]) and isAlphaNumericHyphen(email[ATIndex - 1]) and isAlphaNumericHyphen(email[dotIndex + 1]) and isAlphaNumericHyphen(email[dotIndex - 1]):
                    return True
                
        else:
            return False

    else:
        return False

def valPrice(price):
    price = price.strip()
    decimalCounter = 0
    if len(price) > 0:
        for i in range(len(price)):
            if (price[i] == "."):
                decimalCounter += 1
                decimalLocation = i

        if (decimalCounter <= 1):
            if (decimalCounter == 1) and (price[:decimalLocation].isdigit() and price[(decimalLocation + 1):].isdigit()) and (len(price[(decimalLocation + 1):].rstrip("0")) <= 2):
                return True
            if (decimalCounter == 0) and price.isdigit():
                return True

    return False

# Hash validation
def hashValidation(password, storedHash):
    return hashlib.sha256(password.encode()).hexdigest() == storedHash

## Validation grouping
# Grouping necessary validation for customers
def customerValidation(name, phone, email, post):
    errorMessage = ""
    if not valLengthRange(name, 2, 25) and name.isalpha():
        errorMessage += "Name must be between 2 and 25 characters long\n"
    name = name.replace(" ", "a")
    if not name.isalpha():
        errorMessage += "Name must contain only letters\n"
    if not ((len(phone) == 11) and (phone.isnumeric())):
        errorMessage += "Phone number must be 11 characters long and only contain digits\n"
    if not (valEmail(email)):
        errorMessage += "Email must contain an '@', followed by a '.', and be atleast 5 characters long\n"
    if not (valPostcode(post)):
        errorMessage += "Postcode must be in format 'AA99 9AA'\n"

    if errorMessage == "":
        return [True]
    else:
        return [False, errorMessage]

# Grouping necessary validation for memberships
def membershipValidation(time, name, price):
    errorMessage = ""
    if not (time.strip()).isdigit():
        errorMessage += "Time must be an integer\n"
    if not valLengthRange(name, 2, 25) and name.isalpha():
        errorMessage += "Name must be between 2 and 25 characters long, and contain only letters\n"
    if not valPrice(price):
        errorMessage += "Price must be in format 99.99\n"
        
    if errorMessage == "":
        return [True]
    else:
        return [False, errorMessage]
        
# Grouping necessary validation for passwords
def passwordValidation(password):
    password = password.strip()
    errorMessage = ""
    if not (len(password) > 5):
        errorMessage += "Password is too short\n"
    if password.isalnum():
        errorMessage += "Password must contain a special character\n"
    if password.isalpha():
        errorMessage += "Password must contain a number\n"
    if password.isdigit():
        errorMessage += "Password must contain a letter\n"
    
    if errorMessage == "":
        return [True]
    else:
        return [False, errorMessage]
        
# Grouping necessary validation for staff
def staffValidation(username, name):
    username = username.strip()
    name = name.strip()
    errorMessage = ""

    usernameInUse = False
    with open(staffFilePath, 'r') as dataFile:
        data = json.load(dataFile)
        for i in range(len(data["staff"])):
            if username == data["staff"][i]["staffUsername"].strip():
                errorMessage += "Username is already in use\n"
                usernameInUse = True
                break
    
    if not valLengthRange(username, 2, 25) and username.isalpha() and not usernameInUse:
        errorMessage += "Username must be between 2 and 25 characters long, and contain only letters\n"
    if not valLengthRange(name, 2, 25) and name.isalpha():
        errorMessage += "Name must be between 2 and 25 characters long, and contain only letters\n"
    
    if errorMessage == "":
        return [True]
    else:
        return [False, errorMessage]

## UI Creation
# Entry function
def createEntryFunction(parent, defaultText, x, y, width, height, passwordBool=False):
    entry = tk.Entry(parent, bg="#0F1C26", fg="#DEDEDE", font=("Helvetica", 10), highlightbackground="#FFFFFF", highlightcolor="#1988BD", highlightthickness=1, selectbackground="#007ACC", relief="solid", insertbackground="#FFFFFF", insertwidth=1)
    
    if passwordBool:
        entry.bind("<FocusIn>", lambda event: onPasswordEntryClick(event, entry, defaultText))
    else:
        entry.bind("<FocusIn>", lambda event: onEntryClick(event, entry, defaultText))

    entry.bind("<FocusOut>", lambda event: onEntryUnclick(event, entry, defaultText))
    entry.insert(0, defaultText)
    entry.place(x=x, y=y, width=width, height=height)
    return entry

# Label function
def createLabelFunction(parent, text, x, y, width, height, fontSize=13):
    label = tk.Label(parent, text=text)
    label.configure(bg = "#182E3E", fg = "#FFFFFF", font=("Helvetica", fontSize), highlightbackground="#FFFFFF", highlightthickness=2)
    label.place(x=x, y=y, width=width, height=height)
    return label

# Scrolling label function
def createScrollingLabelFunction(parent, defaultText, x, y, width, height):
    def scrollingFunction(event, canvas):
        bbox = canvas.bbox("all")
        contentHeight = bbox[3] - bbox[1]
        if contentHeight > canvas.winfo_height():
            canvas.yview_scroll(int(-1* (event.delta / 60)), "units")

    frame = tk.Frame(parent, highlightbackground="#FFFFFF", highlightcolor="#FFFFFF", highlightthickness=2)
    canvas = tk.Canvas(frame, bg="#182E3E", highlightthickness=0)
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    stringVar = tk.StringVar(value=defaultText)
    label = tk.Label(canvas, textvariable=stringVar, wraplength=width-40, justify="left", anchor="nw", bg="#182E3E", fg = "#FFFFFF", font=("Helvetica", 12))
    labelID = canvas.create_window(0, 0, window=label, anchor="nw")
    label.bind("<Configure>", lambda event: scrollAreaUpdate(event, canvas))
    canvas.bind("<MouseWheel>", lambda event: scrollingFunction(event, canvas))
    label.bind("<MouseWheel>", lambda event: scrollingFunction(event, canvas))

    frame.place(x=x, y=y, width=width, height=height)
    canvas.place(x=0, y=0, width=width-20, height=height-4)
    scrollbar.place(x=width-20, y=0, width=20, height=height-4)

    return stringVar

# Drop down function
def createDropdownFunction(parent, options, x, y, width, height):
    # Add the functionality to delay the screenshot while dropdown is open
    def on_dropdown_select(event):#~
        print("test")
        parent.after(500, lambda: capture_menu(event))  # Delay the capture by 500ms
    
    var = tk.StringVar()
    var.set(options[0])
    dropdown = tk.OptionMenu(parent, var, *options)
    dropdown.configure(bg="#0F1C26", fg="#DEDEDE", font=("Helvetica", 9), activebackground="#FFFFFF", activeforeground="#105B80")
    dropdown["menu"].configure(bg="#0F1C26", fg="#DEDEDE", font=("Helvetica", 9), activebackground="#FFFFFF", activeforeground="#105B80")
    dropdown.place(x=x, y=y, width=width, height=height)

    dropdown.bind("<Button>", on_dropdown_select)#~

    return var, dropdown

# Button function
def createButtonFunction(parent, text, command, x, y, width, height, fontSize=14):
    buttonFrame = tk.Frame(parent, highlightbackground="#469BD4", highlightthickness=1)
    button = tk.Button(buttonFrame, text=text, command=command, bg="#105B80", fg="#FFFFFF", activebackground="#FFFFFF", activeforeground="#105B80", font=("Helvetica", fontSize, "bold"), borderwidth=0)
    button.bind("<Enter>", onCursorHoverHand2)
    button.bind("<Leave>", onCursorLeave)
    buttonFrame.place(x=x, y=y, width=width, height=height)
    button.place(x=0, y=0, width=width-2, height=height-2)
    return button

# Function to capture the window's screenshot
def capture_menu(event): #~~
    # Wait a bit to ensure the dropdown is fully open
    time.sleep(0.5)  # Adjust the time if needed

    # Get the window's position and size using pygetwindow
    window = gw.getActiveWindow()
    window_rect = window._rect

    # Capture the screenshot of the window using pyautogui
    screenshot = pyautogui.screenshot(region=(window_rect.left, window_rect.top, window_rect.width, window_rect.height))
    screenshot.save("testing_Screenshot.png")
    print("Window screenshot saved!")

# Main window function
def createMainWindowFunction(title, width, height):
    window = tk.Tk()
    window.title(title)
    window.configure(bg="#182E3E")
    screenWidth = window.winfo_screenwidth()
    screenHeight = window.winfo_screenheight()
    window.geometry(f"{width}x{height}+{round((screenWidth-width)/2)}+{round((screenHeight-height)/2)}")
    window.resizable(False, False)
    window.bind("<F12>", lambda event: capture_menu(event))#~

    headingFrame = tk.Frame(window, bg="#213E54", highlightbackground="#FFFFFF", highlightthickness=1)
    headingLabel = tk.Label(headingFrame, text=title, font=("Helvetica", 20, "bold"), bg="#213E54", fg="#FFFFFF")

    headingFrame.place(x=0, y=0, width=width, height=70)
    headingLabel.place(relx=0.5, rely=0.5, anchor="center")

    return window

## Main Code
# Login Menu Function
def loadLoginMenu():
    # Defining Functions
    def loginVerification():
        currentUsername = usernameEntry.get()
        currentPassword = passwordEntry.get()
        valid = False

        # Attempting to find username and password in staff file
        try:
            with open(staffFilePath, 'r') as dataFile:
                data = json.load(dataFile)
                for i in range(len(data["staff"])):
                    if currentUsername.strip() == data["staff"][i]["staffUsername"].strip():
                        if hashValidation(currentPassword.strip(), data["staff"][i]["password"].strip()):
                            global currentStaffAccessArray
                            currentStaffAccessArray = data["staff"][i]
                            valid = True
                        break
        
        # Accounting for exceptions
        except Exception as error:
            print(error)
            messagebox.showerror("Error", "Problem Retrieving File")

        # Checking to see if username and password matches                
        if valid:
            print(currentStaffAccessArray)
            loginMenu.destroy()
            loadNavigationMenu()
        else:
            # Resetting entries if they dont match
            fillEntry(usernameEntry, defaultUsernameEntry, True)
            fillEntry(passwordEntry, defaultPasswordEntry, True)
            messagebox.showerror("Error", "Username or Password is incorrect")
            loginButton.focus_set()
    
    # Creating Window
    loginMenu = createMainWindowFunction("Login Menu", 560, 360)

    # Creating Labels
    usernameLabel = createLabelFunction(loginMenu, "Username:", 50, 100, 100, 40)
    passwordLabel = createLabelFunction(loginMenu, "Password:", 50, 160, 100, 40)

    # Creating Entries
    defaultUsernameEntry = "Type Username here..."
    usernameEntry = createEntryFunction(loginMenu, defaultUsernameEntry, 180, 100, 330, 40)
    usernameEntry.bind("<Return>", lambda event: passwordEntry.focus_set())
    
    defaultPasswordEntry = "Type Password here..."
    passwordEntry = createEntryFunction(loginMenu, defaultPasswordEntry, 180, 160, 330, 40, True)
    passwordEntry.bind("<Return>", lambda event: loginVerification())

    # Creating Buttons
    loginButton = createButtonFunction(loginMenu, "Login", lambda: loginVerification(), 220, 240, 120, 60)

    # Setting up the menu
    loginMenu.lift()
    loginMenu.attributes('-topmost', True)
    loginMenu.after_idle(loginMenu.attributes, '-topmost', False)

    loginMenu.mainloop()

# Navigation Menu Function
def loadNavigationMenu():
    # Filling information labels
    def labelDataUpdate():
        currentUsernameLabel.configure(text=f'{currentStaffAccessArray["staffUsername"]}')
        currentNameLabel.configure(text=f'{currentStaffAccessArray["name"]}')
    
    # Updating time label every second
    def currentTimeUpdate():
        if not timeRunning:
            return
        currentTime = datetime.datetime.now().strftime("%H:%M")
        currentTimeLabel.configure(text=currentTime)
        navigationMenu.after(1000, currentTimeUpdate)
    
    # Stopping variables on close
    def onWindowClose():
        nonlocal timeRunning
        timeRunning = False
        navigationMenu.destroy()

    # Signing the staff member out
    def signOut():
        if messagebox.askokcancel("Sign Out", "Are you sure you want to sign out?"):
            currentStaffAccessArray = {}
            navigationMenu.destroy()
            loadLoginMenu()

    # Defining Menu Loading Functions
    def staffInformationMenuLoad():
        global currentStaffAccessArray
        if (currentStaffAccessArray["accessLevel"] != "Manager") and (currentStaffAccessArray["accessLevel"] != "Admin"):
            messagebox.showerror("Invalid Access", "You do not have the access required to use this")
            return
        else:
            navigationMenu.destroy()
            loadStaffInformationMenu()

    def membershipMenuLoad():
        global currentStaffAccessArray
        if (currentStaffAccessArray["accessLevel"] == "Trainer"):
            messagebox.showerror("Invalid Access", "You do not have the access required to use this")
            return
        else:
            navigationMenu.destroy()
            loadMembershipMenu()
            
    # Creating Window
    navigationMenu = createMainWindowFunction("Navigation Menu", 560, 360)
    navigationMenu.protocol("WM_DELETE_WINDOW", onWindowClose)

    # Creating Labels
    currentUsernameLabel = createLabelFunction(navigationMenu, "Current Username", 40, 100, 160, 40)
    currentNameLabel = createLabelFunction(navigationMenu, "Current Name", 230, 100, 160, 40)
    currentTimeLabel = createLabelFunction(navigationMenu, "Current Time", 420, 100, 100, 40)
    timeRunning = True
    currentTimeUpdate()

    # Creating Buttons
    searchInterfaceButton = createButtonFunction(navigationMenu, "Search Interface", lambda: [navigationMenu.destroy(), loadSearchInterface()], 40, 160, 230, 40)
    staffInformationMenuButton = createButtonFunction(navigationMenu, "Staff Information Menu", lambda: staffInformationMenuLoad(), 290, 160, 230, 40)
    customerDataInterfaceButton = createButtonFunction(navigationMenu, "Customer Data Interface", lambda: [navigationMenu.destroy(), loadCustomerDataInterface(None, None, False)], 40, 220, 230, 40, 12)
    membershipMenuButton = createButtonFunction(navigationMenu, "Membership Menu", lambda: membershipMenuLoad(), 290, 220, 230, 40)
    scheduleButton = createButtonFunction(navigationMenu, "Schedule", lambda: [navigationMenu.destroy(), loadScheduleMenu()], 40, 280, 230, 40)
    signOutButton = createButtonFunction(navigationMenu, "Sign Out", lambda: signOut(), 290, 280, 230, 40)

    labelDataUpdate()

    # Setting up the menu
    navigationMenu.lift()
    navigationMenu.attributes('-topmost', True)
    navigationMenu.after_idle(navigationMenu.attributes, '-topmost', False)

    navigationMenu.mainloop()

# Search Interface Function
def loadSearchInterface():
    
    # Creating Window
    searchInterface = createMainWindowFunction("Search Interface", 560, 280)

    # Binding Open Navigation On Window Close
    searchInterface.protocol("WM_DELETE_WINDOW", lambda: [searchInterface.destroy(), loadNavigationMenu()])

    # Creating Entries
    defaultSearchTermEntry = "Type Search Term here..."
    searchTermEntry = createEntryFunction(searchInterface, defaultSearchTermEntry, 220, 100, 290, 40)

    # Creating Drop Downs
    searchFieldOptions = ["Pick A Search Field", "CustomerID", "Name", "Phone Number", "Email Address", "Postcode", "Membership"]
    searchFieldText, searchFieldDropDown = createDropdownFunction(searchInterface, searchFieldOptions, 50, 100, 140, 40)

    # Creating Buttons
    searchButton = createButtonFunction(searchInterface, "Search", lambda: loadCustomerDataInterface(searchFieldText.get(), searchTermEntry.get(), True, searchInterface), 220, 170, 120, 60)

    # Setting up the menu
    searchInterface.lift()
    searchInterface.attributes('-topmost', True)
    searchInterface.after_idle(searchInterface.attributes, '-topmost', False)

    searchInterface.mainloop()

# Function for the customer data interface
def loadCustomerDataInterface(searchField, searchTerm, searchBool, searchInterface=None):
    # Checking if menu is loaded from searh interface
    if searchBool:
        searchInterface.destroy()
    
    # Defining Functions
    def customerSearch():
        try:
            with open(customerFilePath, 'r') as dataFile:
                data = json.load(dataFile)
                
                customerIDList = []

                # Returning all customers if no search term given, or loaded from navigation menu
                if not(searchBool) or searchField == "Pick A Search Field":
                    for i in range(len(data["customers"])):
                        customerIDList.append(data["customers"][i])

                    return customerIDList
                
                searchTermStrip = searchTerm.strip()

                # Checking what the user was searching for
                if searchField == "CustomerID":
                    if searchTermStrip.isnumeric():
                        binarySearchOutput = binarySearchCustomerID(data["customers"], int(searchTermStrip))
                    else:
                        # Destroying Window If Incorrect Search Term
                        customerDataInterface.destroy()
                        loadSearchInterface()
                        messagebox.showerror("Error", "Invalid Search Term, Use Only Numbers")
                        
                    if binarySearchOutput != -1:
                        customerIDList.append(data["customers"][binarySearchOutput])
                        return customerIDList
                    else:
                        # Destroying Window If ID Not In Customer Database
                        customerDataInterface.destroy()
                        messagebox.showerror("Error", "CustomerID Not In Customer Database")
                        loadSearchInterface()

                if searchField == "Name":
                    searchTermStrip = searchTermStrip.upper()
                    customerIDList = [customer for customer in data["customers"] if searchTermStrip in customer["name"].upper()]
                    if len(customerIDList) != 0:
                        return customerIDList
                    else:
                        # Destroying Window If Name Not In Customer Database
                        customerDataInterface.destroy()
                        messagebox.showerror("Error", f"No '{searchTermStrip}' In Database")
                        loadSearchInterface()
                        
                if searchField == "Phone Number":
                    customerIDList = [customer for customer in data["customers"] if customer["phone"] == searchTermStrip]
                    if len(customerIDList) != 0:
                        return customerIDList
                    else:
                        # Destroying Window If Phone Number Not In Customer Database
                        customerDataInterface.destroy()
                        messagebox.showerror("Error", f"No Customer With Phone Number '{searchTermStrip}' In Database")
                        loadSearchInterface()
                        
                if searchField == "Email Address":
                    customerIDList = [customer for customer in data["customers"] if customer["email"] == searchTermStrip]
                    if len(customerIDList) != 0:
                        return customerIDList
                    else:
                        # Destroying Window If Email Address Not In Customer Database
                        customerDataInterface.destroy()
                        messagebox.showerror("Error", f"No Customer With Email '{searchTermStrip}' In Database")
                        loadSearchInterface()
                        
                if searchField == "Postcode":
                    customerIDList = [customer for customer in data["customers"] if customer["postcode"] == searchTermStrip]
                    if len(customerIDList) != 0:
                        return customerIDList
                    else:
                        # Destroying Window If Postcode Not In Customer Database
                        customerDataInterface.destroy()
                        messagebox.showerror("Error", f"No Customer With Postcode '{searchTermStrip}' In Database")
                        loadSearchInterface()

                if searchField == "Membership":
                    customerIDList = [customer for customer in data["customers"] if customer["membershipType"] == searchTermStrip]
                    if len(customerIDList) != 0:
                        return customerIDList
                    else:
                        # Destroying Window If Postcode Not In Customer Database
                        customerDataInterface.destroy()
                        messagebox.showerror("Error", f"No Customer With Membership '{searchTermStrip}' In Database")
                        loadSearchInterface()
                        
        
        # Accounting for file errors
        except Exception as error:
            print(str(error) + "/nError appears in loadCustomerDataInterface customerSearch")
            return []
    
    # Defining Customer Adding
    def customerAddition(nameEntry, phoneNumberEntry, emailEntry, postcodeEntry, membershipText):
        if (currentStaffAccessArray["accessLevel"] != "Trainer"):
            # Retrieving data
            name = nameEntry.get()
            phoneNumber = phoneNumberEntry.get()
            email = emailEntry.get()
            postcode = postcodeEntry.get()
            membership = membershipText.get()

            # Validation
            customerValidationResult = customerValidation(name, phoneNumber, email, postcode)
            if not customerValidationResult[0]:
                messagebox.showerror("Error Creating Customer", str(customerValidationResult[1]))
                return
            if membership == "Select Membership":
                messagebox.showerror("Error Creating Customer", "Please Select A Membership")
                return

            # Resetting Entries
            fillEntry(nameEntry, "Name here...", True)
            fillEntry(phoneNumberEntry, "Phone Number here...", True)
            fillEntry(emailEntry, "Email here...", True)
            fillEntry(postcodeEntry, "Postcode here...", True)
            membershipText.set("Select Membership")

            # Loading data
            try:
                with open(customerFilePath, 'r') as dataFile:
                    data = json.load(dataFile)
            except FileNotFoundError:
                data = {"customers": []}

            # Creating a customer
            currentCustomerData = {"customerID": None, "name": name, "phone": phoneNumber, "email": email, "postcode": postcode, "membershipType": membership, "initialPaymentDate": None, "initialPaymentUpdate": False}
            currentCustomerData["customerID"] = max([i["customerID"] for i in data["customers"]], default=0) + 1
            currentCustomerData["initialPaymentDate"] = datetime.datetime.now().date().strftime("%d-%m-%Y")
            data["customers"].append(currentCustomerData)

            # Saving data to file
            with open(customerFilePath, 'w') as dataFile:
                json.dump(data, dataFile, indent=4)

            # Reloading Drop Down
            customerIDList = customerSearch()
            customerOptions = customerOptionsSearchUpdate(customerIDList)
            customerOptions.insert(0, "Select Customer")
            customerText.set(customerOptions[0])

            customerDropDown["menu"].delete(0, "end")
            for customer in customerOptions:
                customerDropDown["menu"].add_command(label=customer, command=lambda value=customer: customerText.set(value))

            # Resetting Focus
            creationButton.focus_set()

            # Updating staffChanges
            staffChangesUpdate(f'Added Customer: {currentCustomerData["customerID"]}')
            
        else:
            messagebox.showerror("Invalid Access", "You do not have the access required to use this")
            return

    # Defining Customer Editing
    def customerEditing(customerText, nameEntry, phoneNumberEntry, emailEntry, postcodeEntry, membershipText):
        if (currentStaffAccessArray["accessLevel"] != "Trainer"):
            if not (',' in customerText.get()):
                messagebox.showerror("Error Editing Customer", "Please select a customer")
                return

            # Retrieving data
            customerID = customerText.get().split(',')[0]
            name = nameEntry.get()
            phoneNumber = phoneNumberEntry.get()
            email = emailEntry.get()
            postcode = postcodeEntry.get()
            membership = membershipText.get()

            customerValidationResult = customerValidation(name, phoneNumber, email, postcode)
            if not customerValidationResult[0]:
                messagebox.showerror("Error Editing Customer", str(customerValidationResult[1]))
                return
            if membership == "Select Membership":
                messagebox.showerror("Error Editing Customer", "Please Select A Membership")
                return

            try:
                with open(customerFilePath, 'r') as dataFile:
                    data = json.load(dataFile)

                    index = binarySearchCustomerID(data["customers"], int(customerID))
                    initialPaymentUpdate = False
                    if (data["customers"][index]["membershipType"] == membership):
                        initialPaymentDate = data["customers"][index]["initialPaymentDate"]
                    else:
                        initialRetrieval = nextPaymentLabel['text'].split(":")
                        initialRetrieval = initialRetrieval[1][1:]
                        initialDateObject = datetimedt.strptime(initialRetrieval, "%d-%m-%Y")
                        initialPaymentDate = initialDateObject.strftime("%d-%m-%Y")
                        
                        if (lastPaymentLabel['text'][14:].strip() != "N/A"):
                            initialPaymentUpdate = lastPaymentLabel['text'].split(":")
                            initialPaymentUpdate = initialPaymentUpdate[1][1:]
                            initialUpdateObject = datetimedt.strptime(initialPaymentUpdate, "%d-%m-%Y")
                            initialPaymentUpdate = initialUpdateObject.strftime("%d-%m-%Y")
                            
                        else:
                            intialPayementUpdate = True
                        

                    print(initialPaymentUpdate)
                    data["customers"][index] = {"customerID": data["customers"][index]["customerID"], "name": name, "phone": phoneNumber, "email": email, "postcode": postcode, "membershipType": membership, "initialPaymentDate": initialPaymentDate, "initialPaymentUpdate": initialPaymentUpdate}

                # Saving data to file
                with open(customerFilePath, 'w') as dataFile:
                    json.dump(data, dataFile, indent=4)

                customerInformationLabelUpdate(customerText.get())

                # Resetting Focus
                editButton.focus_set()

                # Updating staffChanges
                staffChangesUpdate(f'Edited Customer: {customerID}')

            except Exception as error:
                print(error)
                
        else:
            messagebox.showerror("Invalid Access", "You do not have the access required to use this")
            return

    # Defining Customer Deletion
    def customerDeletion(customerID):
        if (currentStaffAccessArray["accessLevel"] != "Trainer"):
            if not (',' in customerID):
                messagebox.showerror("Error Deleting Customer", "Please select a customer")
                return
            
            customerID = customerID.split(',')[0]
            try:
                # Loading data from file
                with open(customerFilePath, 'r') as dataFile:
                    data = json.load(dataFile)
                    updatedCustomers = [customer for customer in data["customers"] if str(customer["customerID"]).strip() != str(customerID)]
                    data["customers"] = updatedCustomers

                # Saving data to file
                with open(customerFilePath, 'w') as dataFile:
                    json.dump(data, dataFile, indent=4)

                customerIDList = customerSearch()
                customerOptions = customerOptionsSearchUpdate(customerIDList)
                customerOptions.insert(0, "Select Customer")
                customerText.set(customerOptions[0])
                customerInformationLabelUpdate(customerText.get())

                # Reloading Drop Down
                customerDropDown["menu"].delete(0, "end")
                for customer in customerOptions:
                    customerDropDown["menu"].add_command(label=customer, command=lambda value=customer: customerText.set(value))
                
                # Resetting Focus
                deleteButton.focus_set()

                # Updating staffChanges
                staffChangesUpdate(f'Deleted Customer: {customerID}')

                # Pop-up
                messagebox.showinfo("Customer Deletion", f"Customer {customerID} has been deleted")
                
            except Exception as error:
                print("customerDeletion, " + str(error))
        else:
            messagebox.showerror("Invalid Access", "You do not have the access required to use this")
            return
            
    # Defining Binary Search
    def binarySearchCustomerID(dataCustomers, searchTerm):
        left, right = 0, len(dataCustomers)-1
        
        while left <= right:
                mid = (left + right) // 2
                
                if dataCustomers[mid]["customerID"] == searchTerm:
                        return mid
                elif dataCustomers[mid]["customerID"] < searchTerm:
                        left = mid + 1
                else:
                        right = mid - 1
        return -1

    # Updates the customerInformationLabel when customerDropDown is accessed/changed
    def customerInformationLabelUpdate(customerText): 
        
        # Checking if customer has been selected
        if customerText == "Select Customer":
            customerInformationStringVar.set("Select A Customer")

            fillEntry(nameEntry, defaultNameEntry)
            fillEntry(phoneNumberEntry, defaultPhoneNumberEntry)
            fillEntry(emailEntry, defaultEmailEntry)
            fillEntry(postcodeEntry, defaultPostcodeEntry)
            membershipText.set(membershipOptions[0])
            customerDropDown.focus_set()
            lastPaymentLabel.config(text = "Last Payment: ")
            nextPaymentLabel.config(text = "Next Payment: ")
            return
        
        # Filling scrolling label with customer information
        customerIDList = customerSearch()
        customerIDIndex = listLinearSearchIndex(customerIDList, customerText)

        fillEntry(nameEntry, customerIDList[customerIDIndex]["name"])
        fillEntry(phoneNumberEntry, customerIDList[customerIDIndex]["phone"])
        fillEntry(emailEntry, customerIDList[customerIDIndex]["email"])
        fillEntry(postcodeEntry, customerIDList[customerIDIndex]["postcode"])
        membershipText.set(customerIDList[customerIDIndex]["membershipType"])

        # Creates text in scrolling label
        customerInformationStringVar.set(f'CustomerID: {customerIDList[customerIDIndex]["customerID"]}\n'
                                         f'Name: {customerIDList[customerIDIndex]["name"]}\n'
                                         f'Phone: {customerIDList[customerIDIndex]["phone"]}\n'
                                         f'Email: {customerIDList[customerIDIndex]["email"]}\n'
                                         f'Postcode: {customerIDList[customerIDIndex]["postcode"]}\n'
                                         f'Membership Type: {customerIDList[customerIDIndex]["membershipType"]}\n'
                                         f'Joined Membership On: {customerIDList[customerIDIndex]["initialPaymentDate"]}')

        # Updating Payment Labels
        paymentLabelSearch(customerIDList[customerIDIndex]["membershipType"], customerIDList[customerIDIndex]["initialPaymentDate"], customerIDList[customerIDIndex]["initialPaymentUpdate"])

    # Populates an array with customer IDs and names
    def customerOptionsSearchUpdate(customerIDList):
        customerOptionsTemp = []
        try:
            for i in range(len(customerIDList)):
                customerOptionsTemp.append(f'{customerIDList[i]["customerID"]}, {customerIDList[i]["name"]}')
            return customerOptionsTemp
        except:
            return []

    # Searches for a customer with a specific ID
    def listLinearSearchIndex(listArray, listValue): # maybe add error checking ~
        listValue = listValue.split(',')[0]
        for i in range(len(listArray)):
            if str(listArray[i]["customerID"]).strip() == str(listValue).strip():
                return i

    # Searches membership file for every membership available
    def membershipSearch():
        try:
            # Loading data from file
            with open(membershipFilePath, 'r') as dataFile:
                data = json.load(dataFile)
                
                membershipList = []
        
                for i in range(len(data["memberships"])):
                    membershipList.append(data["memberships"][i])

                return membershipList

        except Exception as error:
            print("Membership membershipSearch: " + str(error))
            return []

    # Populates an array with names of memberships
    def membershipOptionsSearchUpdate(membershipList):
        membershipOptionsTemp = []
        for i in range(len(membershipList)):
            membershipOptionsTemp.append(f'{membershipList[i]["membershipName"]}')
        return membershipOptionsTemp

    # Defining Payment Date Label Searching
    def paymentLabelSearch(membershipType, initialDate, initialPaymentUpdate):
        # Loading data from file
        with open(membershipFilePath, 'r') as dataFile:
            data = json.load(dataFile)
            
            for i in range(len(data["memberships"])):
                if data["memberships"][i]["membershipName"] == membershipType:
                    interval = data["memberships"][i]["timeInterval"]
                    time = data["memberships"][i]["time"]
                    break

            if (interval == "Days"):
                intervalValue = 1
            elif (interval == "Weeks"):
                intervalValue = 7
            elif (interval == "Months"):
                intervalValue = 30
            else:
                intervalValue = 365

            dateIncrement = 0
            initialDate = datetimedt.strptime(initialDate, "%d-%m-%Y")
            currentDate = datetime.datetime.now().date()
            while True:
                comparisonDate = initialDate + timedelta(days=(intervalValue*int(time)*dateIncrement))
                comparisonDate = comparisonDate.date()
                if (comparisonDate >= currentDate):
                    break
                dateIncrement += 1

            lastPayment = initialDate + timedelta(days=(intervalValue*int(time)*(dateIncrement-1)))
            nextPayment = initialDate + timedelta(days=(intervalValue*int(time)*dateIncrement))

            # If Membership has not changed
            if (initialPaymentUpdate == False):
                # If previous payment is older than date of joining membership (customer just joined, no previous payments)
                if (lastPayment < initialDate):
                    lastPaymentLabel.config(text = "Last Payment: N/A")
                    
                # Customer has made previous payments, show previous payment
                else:
                    lastPaymentLabel.config(text = "Last Payment: " + str(lastPayment.strftime("%d-%m-%Y")))
                    
            # If Membership has changed
            else:
                lastPaymentLabel.config(text = "Last Payment: " + str(initialPaymentUpdate))

            nextPaymentLabel.config(text = "Next Payment: " + str(nextPayment.strftime("%d-%m-%Y")))

    # Creating Window
    customerDataInterface = createMainWindowFunction("Customer Data Interface", 720, 440)

    # Binding Open Navigation Or Search Interface On Window Close
    if searchBool:
        customerDataInterface.protocol("WM_DELETE_WINDOW", lambda: [customerDataInterface.destroy(), loadSearchInterface()])
    else:
        customerDataInterface.protocol("WM_DELETE_WINDOW", lambda: [customerDataInterface.destroy(), loadNavigationMenu()])

    # Creating Labels
    lastPaymentLabel = createLabelFunction(customerDataInterface, "Last Payment: ", 240, 300, 200, 40, 11)
    nextPaymentLabel = createLabelFunction(customerDataInterface, "Next Payment: ", 480, 300, 200, 40, 11)

    # Creating Scrolling Label
    customerInformationStringVar = createScrollingLabelFunction(customerDataInterface, "Select A Customer", 240, 100, 440, 120)

    # Creating Entries
    defaultNameEntry = "Name here..."
    nameEntry = createEntryFunction(customerDataInterface, defaultNameEntry, 40, 240, 160, 40)
    
    defaultPhoneNumberEntry = "Phone Number here..."
    phoneNumberEntry = createEntryFunction(customerDataInterface, defaultPhoneNumberEntry, 240, 240, 200, 40)
    
    defaultEmailEntry = "Email Address here..."
    emailEntry = createEntryFunction(customerDataInterface, defaultEmailEntry, 480, 240, 200, 40)
    
    defaultPostcodeEntry = "Postcode here..."
    postcodeEntry = createEntryFunction(customerDataInterface, defaultPostcodeEntry, 40, 300, 160, 40)

    # Creating Drop Downs
    customerIDList = customerSearch()
    customerOptions = customerOptionsSearchUpdate(customerIDList)
    customerOptions.insert(0, "Select Customer")
    customerText, customerDropDown = createDropdownFunction(customerDataInterface, customerOptions, 40, 110, 160, 40)
    customerText.trace_add("write", lambda name, index, operation: customerInformationLabelUpdate(customerText.get()))

    membershipList = membershipSearch()
    membershipOptions = membershipOptionsSearchUpdate(membershipList)
    membershipOptions.insert(0, "Select Membership")
    membershipText, membershipDropDown = createDropdownFunction(customerDataInterface, membershipOptions, 40, 170, 160, 40)

    # Creating Buttons
    creationButton = createButtonFunction(customerDataInterface, "Create", lambda: customerAddition(nameEntry, phoneNumberEntry, emailEntry, postcodeEntry, membershipText), 60, 360, 160, 40)
    editButton = createButtonFunction(customerDataInterface, "Edit", lambda: customerEditing(customerText, nameEntry, phoneNumberEntry, emailEntry, postcodeEntry, membershipText), 280, 360, 160, 40)
    deleteButton = createButtonFunction(customerDataInterface, "Delete", lambda: customerDeletion(customerText.get()), 500, 360, 160, 40)

    # Setting up the menu
    customerDataInterface.lift()
    customerDataInterface.attributes('-topmost', True)
    customerDataInterface.after_idle(customerDataInterface.attributes, '-topmost', False)

    customerDataInterface.mainloop()

# Function for the staff information menu
def loadStaffInformationMenu():

    # Defining Staff Changes Updating
    def staffChangesRefresh():
        try:
            # Loading data from file
            with open(staffFilePath, 'r') as dataFile:
                data = json.load(dataFile)

                oldDate = date.today() - timedelta(90)
                oldDate = oldDate.strftime("%Y%m%d")
                updatedStaffChanges = [changes for changes in data["staffChanges"] if changes["date"] >= oldDate]
                data["staffChanges"] = updatedStaffChanges

            # Saving data to file
            with open(staffFilePath, 'w') as dataFile:
                json.dump(data, dataFile, indent=4)

        except Exception as error:
            print(error)
    
    # Defining Staff Adding
    def staffAddition(usernameEntry, nameEntry, passwordEntry, accessLevelText, adminPasswordEntry): 
        
        username = usernameEntry.get()
        name = nameEntry.get()
        password = passwordEntry.get()
        accessLevel = accessLevelText.get()
        adminPassword = adminPasswordEntry.get()

        if (currentStaffAccessArray["accessLevel"] == "Manager") and (accessLevel == "Manager"):
            messagebox.showerror("Invalid Access", "You do not have the access required to create staff with this access level")
            return
        
        if (username == defaultUsernameEntry) or (name == defaultNameEntry) or (password == defaultPasswordEntry) or (adminPassword == defaultAdminPasswordEntry):
            messagebox.showerror("Staff Creation Error", "Please fill all fields")
            return
        
        if accessLevel == "Select Access Level":
            messagebox.showerror("Staff Creation Error", "Please fill all fields")
            return
        
        if (currentStaffAccessArray["password"] != hashlib.sha256(adminPassword.encode()).hexdigest()):
            messagebox.showerror("Invalid Password", "Admin password is incorrect")
            fillEntry(adminPasswordEntry, "Administrative Password here...", True)
            return

        staffValidationResult = staffValidation(username, name)
        if not staffValidationResult[0]:
            messagebox.showerror("Staff Creation Error", str(staffValidationResult[1]))
            return
        
        passwordValidationResult = passwordValidation(password)
        if not passwordValidationResult[0]:
            messagebox.showerror("Staff Creation Error", str(passwordValidationResult[1]))
            return

        # Resetting Entries
        fillEntry(usernameEntry, "Username here...", True)
        fillEntry(nameEntry, "Name here...", True)
        fillEntry(passwordEntry, "Password here...", True)
        fillEntry(adminPasswordEntry, "Administrative Password here...", True)
        accessLevelText.set("Select Access Level")

        try:
            # Loading data from file
            with open(staffFilePath, 'r') as dataFile:
                data = json.load(dataFile)
        except Exception as error:
            print("staffaddition" + str(error))

        currentStaffData = {"staffUsername": username, "name": name, "password": hashlib.sha256(password.encode()).hexdigest(), "accessLevel": accessLevel}
        data["staff"].append(currentStaffData)

        # Saving data to file
        with open(staffFilePath, 'w') as dataFile:
            json.dump(data, dataFile, indent=4)

        # Updating staffChanges
        staffChangesUpdate(f'Added Staff: {currentStaffData["staffUsername"]}')
        staffChangesLabelUpdate()
        createStaffButton.focus_set()

    # Defining Staff Deletion
    def staffDeletion(staffUsername, adminPassword):
        try:
            # Loading data from file
            with open(staffFilePath, 'r') as dataFile:
                data = json.load(dataFile)
                staffDetails = []
                updatedStaff = []
                for staff in data["staff"]:
                    if str(staff["staffUsername"]).strip() == str(staffUsername):
                        staffDetails = staff 
                    else:
                        updatedStaff.append(staff)

                data["staff"] = updatedStaff

                if (currentStaffAccessArray["accessLevel"] == "Receptionist") or (currentStaffAccessArray["accessLevel"] == "Trainer"):
                    messagebox.showerror("Invalid Access", "You do not have the access required to delete staff members")
                    return

                if staffDetails != []:
                    if (staffDetails["accessLevel"] == "Admin"):
                        messagebox.showerror("Invalid Access", "You do not have the access required to delete this staff member")
                        return
                        
                    if (staffDetails["accessLevel"] == "Manager") and (currentStaffAccessArray["accessLevel"] == "Manager"):
                        messagebox.showerror("Invalid Access", "You do not have the access required to delete this staff member")
                        return

                else:
                    messagebox.showerror("Staff Deletion Error", f'No Staff Member found with Username {staffUsername}')
                    return

            if not hashValidation(adminPassword.strip(), currentStaffAccessArray["password"]):
                messagebox.showerror("Error", "Admin Password does not match Current Account Password")
                return

            if staffDetails["accessLevel"] == "Trainer":
                runningSessionCount = 0
                sessionString = ""
                # Loading data from file
                with open(sessionFilePath, 'r') as dataFile:
                    sessionData = json.load(dataFile)
                    for i in range(len(sessionData["sessions"])):
                        for j in range(len(sessionData["sessions"][i]["lessons"])):
                            if sessionData["sessions"][i]["lessons"][j]["staffMember"] == staffUsername:
                                runningSessionCount += 1
                                beginTime = sessionData["sessions"][i]["lessons"][j]["beginTime"]
                                date = sessionData["sessions"][i]["date"]
                                sessionString = f'{beginTime[:2]}:{beginTime[2:]}, {date[6:]}/{date[4:6]}/{date[:4]}\n'
                
                if runningSessionCount > 0:
                    moreSessionInfoBool = messagebox.askokcancel("Staff Deletion Error", f"Staff is still hosting {runningSessionCount} sessions\nWould you like more information?")
                    if moreSessionInfoBool:
                        messagebox.showinfo(f"Sessions Hosted By {staffUsername}", sessionString)
                    return

            # Saving data to file
            with open(staffFilePath, 'w') as dataFile:
                json.dump(data, dataFile, indent=4)
            
            fillEntry(usernameEntry, defaultUsernameEntry, True)
            fillEntry(nameEntry, defaultNameEntry, True)
            fillEntry(passwordEntry, defaultPasswordEntry, True)
            fillEntry(adminPasswordEntry, defaultAdminPasswordEntry, True)
            accessLevelText.set(accessLevelOptions[0])
            
            # Updating staffChanges
            staffChangesUpdate(f'Deleted Staff: {staffUsername}')
            staffChangesLabelUpdate()
            messagebox.showinfo(f"Staff Deletion", f"Staff Member {staffUsername} Deleted")
            deleteButton.focus_set()
            
        except Exception as error:
            print("customerDeletion, " + str(error))
    
    # Defining Staff Password Editing
    def staffPasswordEdit(staffUsername, password, adminPassword):
        
        staffUsername = staffUsername.strip()
        password = password.strip()
        adminPassword = adminPassword.strip()
        
        if (currentStaffAccessArray["accessLevel"] != "Manager" and currentStaffAccessArray["accessLevel"] != "Admin"):
            messagebox.showerror("Invalid Access", "You do not have the access required to edit staff members")
            return

        if not hashValidation(adminPassword.strip(), currentStaffAccessArray["password"]):
            messagebox.showerror("Error", "Admin Password does not match Current Account Password")
            return

        passwordValidationResult = passwordValidation(password)
        if not passwordValidationResult[0]:
            messagebox.showerror("Error Creating Staff Member", str(passwordValidationResult[1]))
            return

        try:
            # Loading data from file
            with open(staffFilePath, 'r') as dataFile:
                data = json.load(dataFile)

                for i in range(len(data["staff"])):
                    if staffUsername == data["staff"]["staffUsername"]:
                        staffLocation = i
                        break
                
                if (data["staff"][staffLocation]["accessLevel"] == "Manager" and currentStaffAccessArray["accessLevel"] == "Manager") or data["staff"][staffLocation]["accessLevel"] == "Admin":
                    messagebox.showerror("Invalid Access", "You do not have the access required to edit this staff member")
                    return
                
                data["staff"][staffLocation]["password"] == password

            # Saving data to file
            with open(staffFilePath, 'w') as dataFile:
                json.dump(data, dataFile, indent=4)
            
            staffChangesUpdate(f'Changed Staff Password: {staffUsername}')
            staffChangesLabelUpdate()
            messagebox.showinfo("Changed Staff Password", f"Successfully changed the password of {staffUsername}")
            changePasswordButton.focus_set()

        except Exception as error:
            print("Staff password editing: " + str(error))

    # Defining Staff Access Editing
    def staffAccessEdit(staffUsername, accessLevel, adminPassword):
        staffUsername = staffUsername.strip()
        adminPassword = adminPassword.strip()
        
        if (currentStaffAccessArray["accessLevel"] != "Manager" and currentStaffAccessArray["accessLevel"] != "Admin"):
            messagebox.showerror("Invalid Access", "You do not have the access required to edit staff members")
            return

        if not hashValidation(adminPassword.strip(), currentStaffAccessArray["password"]):
            messagebox.showerror("Error", "Admin Password does not match Current Account Password")
            return

        if accessLevel == "Select Access Level":
            messagebox.showerror("Error", "Please select an access level")
            return

        try:
            # Loading data from file
            with open(staffFilePath, 'r') as dataFile:
                data = json.load(dataFile)

                for i in range(len(data["staff"])):
                    if staffUsername == data["staff"]["staffUsername"]:
                        staffLocation = i
                        break
                
                if (data["staff"][staffLocation]["accessLevel"] == "Manager" and currentStaffAccessArray["accessLevel"] == "Manager") or data["staff"][staffLocation]["accessLevel"] == "Admin":
                    messagebox.showerror("Invalid Access", "You do not have the access required to edit this staff member")
                    return
                
                data["staff"][staffLocation]["accessLevel"] == accessLevel

            # Saving data to file
            with open(staffFilePath, 'w') as dataFile:
                json.dump(data, dataFile, indent=4)
            
            staffChangesUpdate(f'Changed Staff Access: {staffUsername}')
            staffChangesLabelUpdate()
            messagebox.showinfo("Changed Staff Access", f"Successfully changed the access of {staffUsername}")
            changeAccessButton.focus_set()

        except Exception as error:
            print("Staff access editing: " + str(error))

    # Updating content inside scrolling label
    def staffChangesLabelUpdate():
        staffChangesStringVar.set("")
        try:
            # Loading data from file
            with open(staffFilePath, 'r') as dataFile:
                data = json.load(dataFile)
                staffChanges = [changes for changes in data["staffChanges"]]

                staffChangesText = ""
                for i in range(len(staffChanges) - 1, -1, -1):
                    staffChangesText += f'{staffChanges[i]["name"]} ({staffChanges[i]["staffUsername"]}), {staffChanges[i]["changeMade"]}, at {staffChanges[i]["time"]} on {staffChanges[i]["date"]} \n'

                if staffChangesText != "":
                    staffChangesStringVar.set(staffChangesText)
                else:
                    staffChangesStringVar.set("No Changes To Report")
                
        except Exception as error:
            staffChangesStringVar.set("No Changes To Report")
    
    # Creating Window
    staffInformationMenu = createMainWindowFunction("Staff Information Menu", 560, 560)

    # Binding Open Navigation On Window Close
    staffInformationMenu.protocol("WM_DELETE_WINDOW", lambda: [staffInformationMenu.destroy(), loadNavigationMenu()])

    # Creating Scrolling Label
    staffChangesStringVar = createScrollingLabelFunction(staffInformationMenu, "No Changes To Report", 40, 100, 480, 170)

    # Creating Entries
    defaultUsernameEntry = "Username here..."
    usernameEntry = createEntryFunction(staffInformationMenu, defaultUsernameEntry, 40, 280, 230, 40)
    
    defaultNameEntry = "Name here..."
    nameEntry = createEntryFunction(staffInformationMenu, defaultNameEntry, 40, 342, 230, 40)
    
    defaultPasswordEntry = "Password here..."
    passwordEntry = createEntryFunction(staffInformationMenu, defaultPasswordEntry, 290, 342, 230, 40, True)
    
    defaultAdminPasswordEntry = "Administrative Password here..."
    adminPasswordEntry = createEntryFunction(staffInformationMenu, defaultAdminPasswordEntry, 290, 280, 230, 40, True)

    # Creating Drop Downs
    # Access Levels are Receptionist, Trainer, Manager and Admin
    accessLevelOptions = ["Select Access Level", "Receptionist", "Trainer", "Manager"]
    accessLevelText, accessLevelDropDown = createDropdownFunction(staffInformationMenu, accessLevelOptions, 40, 392, 480, 40)

    # Creating Buttons
    createStaffButton = createButtonFunction(staffInformationMenu, "Create Staff", lambda: staffAddition(usernameEntry, nameEntry, passwordEntry, accessLevelText, adminPasswordEntry), 40, 450, 230, 40)
    changePasswordButton = createButtonFunction(staffInformationMenu, "Change Password", lambda: staffPasswordEdit(usernameEntry.get(), passwordEntry.get(), adminPasswordEntry.get()), 290, 450, 230, 40)
    changeAccessButton = createButtonFunction(staffInformationMenu, "Change Access", lambda: staffAccessEdit(usernameEntry.get(), accessLevelText.get(), adminPasswordEntry.get()), 290, 500, 230, 40)
    deleteButton = createButtonFunction(staffInformationMenu, "Delete Staff", lambda: staffDeletion(usernameEntry.get(), adminPasswordEntry.get()), 40, 500, 230, 40)

    staffChangesLabelUpdate()
    staffChangesRefresh()

    # Setting up the menu
    staffInformationMenu.lift()
    staffInformationMenu.attributes('-topmost', True)
    staffInformationMenu.after_idle(staffInformationMenu.attributes, '-topmost', False)

    staffInformationMenu.mainloop()

# Function for the membership menu
def loadMembershipMenu():
    
    # Defining Functions
    def membershipSearch():
        try:
            # Loading data from file
            with open(membershipFilePath, 'r') as dataFile:
                data = json.load(dataFile)
                
                membershipList = []
        
                for i in range(len(data["memberships"])):
                    membershipList.append(data["memberships"][i])

                return membershipList

        except Exception as error:
            print("Membership membershipSearch: " + str(error))
            return []
    
    # Defining Membership Adding
    def membershipAddition(timeEntry, nameEntry, priceEntry, timeIntervalText):
        if (currentStaffAccessArray["accessLevel"] != "Receptionist"):
            
            time = timeEntry.get()
            name = nameEntry.get()
            price = priceEntry.get()
            timeInterval = timeIntervalText.get()

            # Validation
            membershipValidationResult = membershipValidation(time, name, price)
            if not membershipValidationResult[0]:
                messagebox.showerror("Error Creating Membership", str(membershipValidationResult[1]))
                return
            if timeInterval == "Select Time Interval":
                messagebox.showerror("Error Creating Membership", "Please Select A Time Interval")
                return

            # Resetting Entries
            fillEntry(nameEntry, "Name here...", True)
            fillEntry(priceEntry, "Price here...", True)
            fillEntry(timeEntry, "Time here...", True)
            timeIntervalText.set("Select Time Interval")

            try:
                # Loading data from file
                with open(membershipFilePath, 'r') as dataFile:
                    data = json.load(dataFile)
            
            # Accounting for errors
            except FileNotFoundError:
                data = {"memberships": []}

            currentMembershipData = {"membershipName": name, "price": price, "timeInterval": timeInterval, "time": time} 
            data["memberships"].append(currentMembershipData)

            # Saving data to file
            with open(membershipFilePath, 'w') as dataFile:
                json.dump(data, dataFile, indent=4)

            # Reloading Drop Down
            membershipList = membershipSearch()
            membershipOptions = membershipOptionsSearchUpdate(membershipList)
            membershipOptions.insert(0, "Select Membership")
            membershipText.set(membershipOptions[0])

            membershipDropDown["menu"].delete(0, "end")
            for membership in membershipOptions:
                membershipDropDown["menu"].add_command(label=membership, command=lambda value=membership: membershipText.set(value))

            # Resetting Focus
            createMembershipButton.focus_set()

            # Updating staffChanges
            staffChangesUpdate(f'Added Membership: {currentMembershipData["membershipName"]}')
            messagebox.showinfo("Created Membership", f"Created membership {name}")
            
        else:
            messagebox.showerror("Invalid Access", "You do not have the access required to use this")
            return

    # Defining Membership Editing
    def membershipEditing(membershipText, timeEntry, nameEntry, priceEntry, timeIntervalText):
        if (currentStaffAccessArray["accessLevel"] != "Receptionist"):
            time = timeEntry.get().strip()
            name = nameEntry.get().strip()
            price = priceEntry.get().strip()
            timeInterval = timeIntervalText.get().strip()
            membershipName = membershipText.get()

            # Validation
            membershipValidationResult = membershipValidation(time, name, price)
            if not membershipValidationResult[0]:
                messagebox.showerror("Error Editing Membership", str(membershipValidationResult[1]))
                return
            if timeInterval == "Select Time Interval":
                messagebox.showerror("Error Editing Membership", "Please Select A Time Interval")
                return

            try:
                # Loading data from file
                with open(customerFilePath, 'r') as dataFile:
                    data = json.load(dataFile)

                    errorMessage = ""
                    for i in range(len(data["customers"])):
                        if (data["customers"][i]["membershipType"] == membershipName):
                            errorMessage += f'{data["customers"][i]["customerID"]}, {data["customers"][i]["name"]}\n'

                    if not (errorMessage == ""):
                        messagebox.showerror("Error", f'The membership exists in the following customers:\n{errorMessage}')

                        return

            # Accounting for errors
            except Exception as error:
                print("Editing membership error: " + str(error))

            try:
                # Loading data from file
                with open(membershipFilePath, 'r') as dataFile:
                    data = json.load(dataFile)

                    membershipIndex = listLinearSearchIndex(data["memberships"], membershipName)
                    data["memberships"][membershipIndex] = {"membershipName": name, "price": price, "timeInterval": timeInterval, "time": time}

                # Saving data to file
                with open(membershipFilePath, 'w') as dataFile:
                    json.dump(data, dataFile, indent=4)

                # Resetting Focus
                editButton.focus_set()

                # Updating staffChanges
                staffChangesUpdate(f'Edited Membership: {membershipName}')
                messagebox.showinfo("Edited Membership", f"Edited membership {name}")
                    
                    
            # Accounting for errors
            except Exception as error:
                print("Membership editing error " + str(error))

        else:
            messagebox.showerror("Invalid Access", "You do not have the access required to use this")
            return

    # Defining Membership Deletion
    def membershipDeletion(membershipText):
        if (currentStaffAccessArray["accessLevel"] != "Receptionist"):
            
            membershipName = membershipText.get()
            if membershipName == "Select Membership":
                messagebox.showerror("Error", "Please select a membership to delete")
                return
            
            try:
                # Loading data from file
                with open(customerFilePath, 'r') as dataFile:
                    data = json.load(dataFile)

                    errorMessage = ""
                    for i in range(len(data["customers"])):
                        if (data["customers"][i]["membershipType"] == membershipName):
                            errorMessage += f'{data["customers"][i]["customerID"]}, {data["customers"][i]["name"]}\n'

                    if not (errorMessage == ""):
                        messagebox.showerror("Error", f'The membership exists in the following customers:\n{errorMessage}')
                        return
                
                # Loading data from file
                with open(membershipFilePath, 'r') as dataFile:
                    data = json.load(dataFile)
                    updatedMemberships = [membership for membership in data["memberships"] if str(membership["membershipName"]).strip() != str(membershipName).strip()]
                    data["memberships"] = updatedMemberships

                # Saving data to file
                with open(membershipFilePath, 'w') as dataFile:
                    json.dump(data, dataFile, indent=4)


                membershipList = membershipSearch()
                membershipOptions = membershipOptionsSearchUpdate(membershipList)
                membershipOptions.insert(0, "Select Membership")
                membershipText.set(membershipOptions[0])
                membershipInformationLabelUpdate(membershipText.get())

                membershipDropDown["menu"].delete(0, "end")
                for membership in membershipOptions:
                    membershipDropDown["menu"].add_command(label=membership, command=lambda value=membership: membershipText.set(value))

                # Resetting entries~

                # Updating staffChanges
                staffChangesUpdate(f'Deleted Membership: {membershipName}')
                messagebox.showinfo("Deleted Membership", f"Deleted membership {membershipName}")
                
            # Accounting for errors
            except Exception as error:
                print("membershipDeletion, " + str(error))

        else:
            messagebox.showerror("Invalid Access", "You do not have the access required to use this")
            return

    # General Functions
    def membershipOptionsSearchUpdate(membershipList):
        membershipOptionsTemp = []
        for i in range(len(membershipList)):
            membershipOptionsTemp.append(f'{membershipList[i]["membershipName"]}')
        return membershipOptionsTemp

    def listLinearSearchIndex(listArray, listValue):
        for i in range(len(listArray)):
            if str(listArray[i]["membershipName"]).strip() == str(listValue).strip():
                return i

    def membershipInformationLabelUpdate(membershipText):
            
        if membershipText == "Select Membership":
            membershipInformationStringVar.set("Select A Membership")

            fillEntry(timeEntry, defaultTimeEntry)
            fillEntry(nameEntry, defaultNameEntry)
            fillEntry(priceEntry, defaultPriceEntry)
            timeIntervalText.set(timeIntervalOptions[0])
            membershipDropDown.focus_set()
        
        else:
            # Loading data from file
            with open(membershipFilePath, 'r') as dataFile:
                data = json.load(dataFile)
                membershipSearchArray = membershipSearch()
                membershipIndex = listLinearSearchIndex(membershipSearchArray, membershipText)

                fillEntry(nameEntry, data["memberships"][membershipIndex]["membershipName"])
                fillEntry(priceEntry, data["memberships"][membershipIndex]["price"])
                fillEntry(timeEntry, data["memberships"][membershipIndex]["time"])
                timeIntervalText.set(data["memberships"][membershipIndex]["timeInterval"])
                
                membershipInformationStringVar.set(f'Membership Name: {data["memberships"][membershipIndex]["membershipName"]}\n'
                                                   f'Price: {data["memberships"][membershipIndex]["price"]}\n'
                                                   f'Time Interval: {data["memberships"][membershipIndex]["timeInterval"]}\n'
                                                   f'Time Integer: {data["memberships"][membershipIndex]["time"]}')

    # Creating Window
    membershipMenu = createMainWindowFunction("Membership Menu", 720, 360)

    # Binding Open Navigation On Window Close
    membershipMenu.protocol("WM_DELETE_WINDOW", lambda: [membershipMenu.destroy(), loadNavigationMenu()])

    # Creating Scrolling Label
    membershipInformationStringVar = createScrollingLabelFunction(membershipMenu, "Select A Membership", 240, 100, 440, 120)

    # Creating Entries
    defaultTimeEntry = "Time here..."
    timeEntry = createEntryFunction(membershipMenu, defaultTimeEntry, 40, 240, 160, 40)
    
    defaultNameEntry = "Name here..."
    nameEntry = createEntryFunction(membershipMenu, defaultNameEntry, 240, 240, 200, 40)
    
    defaultPriceEntry = "Price here..."
    priceEntry = createEntryFunction(membershipMenu, defaultPriceEntry, 480, 240, 200, 40)

    # Creating Drop Downs
    membershipList = membershipSearch()
    membershipOptions = membershipOptionsSearchUpdate(membershipList)
    membershipOptions.insert(0, "Select Membership")
    membershipText, membershipDropDown = createDropdownFunction(membershipMenu, membershipOptions, 40, 110, 160, 40)
    membershipText.trace_add("write", lambda name, index, operation: membershipInformationLabelUpdate(membershipText.get()))

    timeIntervalOptions = ["Select Time Interval", "Days", "Weeks", "Months", "Years"]
    timeIntervalText, timeIntervalDropDown = createDropdownFunction(membershipMenu, timeIntervalOptions, 40, 170, 160, 40)
    
    # Creating Buttons
    createMembershipButton = createButtonFunction(membershipMenu, "Create", lambda: membershipAddition(timeEntry, nameEntry, priceEntry, timeIntervalText), 60, 300, 160, 40)
    editButton = createButtonFunction(membershipMenu, "Edit", lambda: membershipEditing(membershipText, timeEntry, nameEntry, priceEntry, timeIntervalText), 280, 300, 160, 40)
    deleteButton = createButtonFunction(membershipMenu, "Delete", lambda: membershipDeletion(membershipText), 500, 300, 160, 40)

    # Setting up the menu
    membershipMenu.lift()
    membershipMenu.attributes('-topmost', True)
    membershipMenu.after_idle(membershipMenu.attributes, '-topmost', False)

    membershipMenu.mainloop()

# Function for the schedule
def loadScheduleMenu():
    global currentSessionData
    currentSessionData = []

    # Search Function For Staff
    def staffSearch():
        try:
            # Loading data from file
            with open(staffFilePath, 'r') as dataFile:
                data = json.load(dataFile)
                
                if "staff" not in data:
                    return []

                staffList = []
                for i in range(len(data["staff"])):
                    if data["staff"][i]["accessLevel"] == "Trainer":
                        staffList.append(str(data["staff"][i]["staffUsername"]))

                return staffList

        # Accounting for errors
        except Exception as error:
            print("Schedule staffSearch: " + str(error))
            return []
    
    # Search Function For Sessions
    def sessionSearch(sessionValue):
        try:
            # Loading data from file
            with open(sessionFilePath, 'r') as dataFile:
                data = json.load(dataFile)
                
                if "sessions" not in data:
                    return -1

                sessionBinaryOutput = binarySearchSessions(data["sessions"], sessionValue)
                if sessionBinaryOutput == -1:
                    return -1
                else:
                    return data["sessions"][sessionBinaryOutput]
                
        # Accounting for errors
        except Exception as error:
            print("Session Search: " + str(error))
            return -1

    # Session Creation
    def sessionCreation(beginTimeEntry, endTimeEntry, staffText):

        beginTime = beginTimeEntry.get().replace(":", "")
        endTime = endTimeEntry.get().replace(":", "")
        staffMember = staffText.get().strip()

        # Validation
        if not (timeValidation(beginTime) and timeValidation(endTime)):
            messagebox.showerror("Error Editing Session", "Times have to be in the format HH:MM")
            return
        
        if endTime <= beginTime:
            messagebox.showerror("Error Creating Session", "End time cannot be before Begin time")
            return

        chosenDate = dateCalendar.get_date()
        sessionsOnDate = sessionSearch(chosenDate)

        if sessionsOnDate == -1:
            sessionsOnDate = {"date": chosenDate, "lessons": []}

        for i in range(len(sessionsOnDate["lessons"])):
            if (staffMember == sessionsOnDate["lessons"][i]["staffMember"]) and (
                (int(sessionsOnDate["lessons"][i]["beginTime"]) < int(beginTime) <= int(sessionsOnDate["lessons"][i]["endTime"])) or
                (int(sessionsOnDate["lessons"][i]["beginTime"]) <= int(endTime) < int(sessionsOnDate["lessons"][i]["endTime"]))
            ):
                messagebox.showerror("Staff Member Error", "Staff member is already in a different session at this time")
                staffDropDown.set("Select Staff")
                return

        try:
            # Loading data from file
            with open(sessionFilePath, 'r') as dataFile:
                data = json.load(dataFile)

                dates = [int(session["date"]) for session in data["sessions"]]
                indexToInsert = bisect.bisect_left(dates, int(chosenDate))

                if sessionsOnDate["lessons"] == []:
                    newDate = {"date": chosenDate, "lessons": [{"beginTime": beginTime, "endTime": endTime, "staffMember": staffMember, "customers": []}]}
                    data["sessions"].insert(indexToInsert, newDate)
                else:
                    print(f"indexToInsert: {indexToInsert}, len(data['sessions']): {len(data['sessions'])}")
                    print(f"sessionsOnDate: {sessionsOnDate}")

                    timeToInsert = bisect.bisect_left([int(lesson["beginTime"]) for lesson in data["sessions"][indexToInsert]["lessons"]], int(beginTime))
                    data["sessions"][indexToInsert]["lessons"].insert(timeToInsert, {"beginTime": beginTime, "endTime": endTime, "staffMember": staffMember, "customers": []})

            # Saving data to file
            with open(sessionFilePath, 'w') as dataFile:
                json.dump(data, dataFile, indent=4)

            # Resetting focus
            createSessionButton.focus_set()

            chosenDate = f'{chosenDate[6:]}/{chosenDate[4:6]}/{chosenDate[:4]}'
            staffChangesUpdate(f'Created Session on {chosenDate}, ran by {staffMember}')

        # Accounting for errors
        except Exception as error:
            print("Session creation error: " + str(error))

    # Session Creation
    def sessionEditing(sessionText, beginTimeEntry, endTimeEntry, staffText):
        sessionText = sessionText.get()
        sessionRealBeginTime, sessionRealStaffMember = sessionText.split(", ", 1)[0].replace(":", ""), sessionText.split(", ", 1)[1]
        beginTime = beginTimeEntry.get().replace(":", "")
        endTime = endTimeEntry.get().replace(":", "")
        staffMember = staffText.get().strip()

        customerList = []

        # Validation
        if not (timeValidation(beginTime) and timeValidation(endTime)):
            messagebox.showerror("Error Editing Session", "Times have to be in the format HH:MM")
            return

        if endTime <= beginTime:
            messagebox.showerror("Error Editing Session", "End time has to be after Begin Time")
            return

        chosenDate = dateCalendar.get_date()
        sessionsOnDate = sessionSearch(chosenDate)

        if sessionsOnDate == -1:
            sessionsOnDate = {"date": chosenDate, "lessons": []}

        # Ensuring staff member is not already in use
        for i in range(len(sessionsOnDate["lessons"])):
            if (int(sessionsOnDate["lessons"][i]["beginTime"]) == int(sessionRealBeginTime) and sessionsOnDate["lessons"][i]["staffMember"] == sessionRealStaffMember):
                sessionLessonIndex = i
                customerList = sessionsOnDate["lessons"][i]["customers"]
            elif(staffMember == sessionsOnDate["lessons"][i]["staffMember"]) and (
                (int(sessionsOnDate["lessons"][i]["beginTime"]) < int(beginTime) <= int(sessionsOnDate["lessons"][i]["endTime"])) or
                (int(sessionsOnDate["lessons"][i]["beginTime"]) <= int(endTime) < int(sessionsOnDate["lessons"][i]["endTime"]))
                ):
                messagebox.showerror("Staff Member Error", "Staff member is already in a different session at this time")
                staffDropDown.set("Select Staff")
                return

        try:
            # Loading data from file
            with open(sessionFilePath, 'r') as dataFile:
                data = json.load(dataFile)

                sessionIndex = binarySearchSessions(data["sessions"], chosenDate)
                data["sessions"][sessionIndex]["lessons"][sessionLessonIndex] = {"beginTime": beginTime, "endTime": endTime, "staffMember": staffMember, "customers": customerList}

            # Saving data to file
            with open(sessionFilePath, 'w') as dataFile:
                json.dump(data, dataFile, indent=4)

            chosenDate = f'{chosenDate[6:]}/{chosenDate[4:6]}/{chosenDate[:4]}'
            staffChangesUpdate(f'Edited Session on {chosenDate}, ran by {staffMember}')
            editSessionButton.focus_set()

            # Resetting global currentSessionData
            chosenDate = dateCalendar.get_date()
            availableSessions = sessionSearch(chosenDate)
            global currentSessionData
            currentSessionData = availableSessions
            dateInformationLabelUpdate(sessionText)

        # Accounting for errors
        except Exception as error:
            print("Session creation error: " + str(error))

    # Session Deletion
    def sessionDeletion(sessionText):
        sessionText = sessionText.get().strip()
        if not sessionText:
            return

        sessionTime, sessionStaff = sessionText.split(", ", 1)
        sessionTime = sessionTime.replace(":", "")

        sessionDate = currentSessionData["date"]

        # Find the session to delete
        sessionLocation = -1
        for i in range(len(currentSessionData["lessons"])):
            if (currentSessionData["lessons"][i]["beginTime"] == sessionTime and currentSessionData["lessons"][i]["staffMember"] == sessionStaff):
                sessionLocation = i
                break

        if sessionLocation == -1:
            messagebox.showerror("Error", "Session not found")
            return

        # Warn if there are customers attached to the session
        numberOfCustomers = len(currentSessionData["lessons"][sessionLocation]["customers"])
        if numberOfCustomers > 0:
            continueBool = messagebox.askyesno("Warning", f'{numberOfCustomers} customers are still attached to this session\nAre you sure you want to continue?')
            if not continueBool:
                return

        try:
            # Load the session data from the file
            with open(sessionFilePath, 'r') as dataFile:
                data = json.load(dataFile)

            # Iterate through sessions and locate the matching date
            updatedSessions = []
            for date in data["sessions"]:
                if date["date"] == sessionDate:
                    # Remove the target lesson
                    date["lessons"] = [lesson for lesson in date["lessons"] if not (lesson["beginTime"] == sessionTime and lesson["staffMember"] == sessionStaff)]

                    # If there are no lessons left on that day, skip adding this session
                    if not date["lessons"]:
                        continue

                # Add the updated session if it still has lessons
                updatedSessions.append(date)

            # Update the data with the modified sessions
            data["sessions"] = updatedSessions

            # Save the updated data back to the file
            with open(sessionFilePath, 'w') as dataFile:
                json.dump(data, dataFile, indent=4)

            # Update UI and log the change
            sessionOptionsDropDownUpdate(None)
            staffChangesUpdate(f"Deleted {sessionStaff}'s Session on {sessionDate}")
            deleteSessionButton.focus_set()

        # Accounting for errors
        except Exception as error:
            print("Session deletion error: " + str(error))

    # Session Customer Addition
    def sessionCustomerAddition(sessionText, customerID):
        customerID = customerID.strip()
        sessionText = sessionText.get()

        if (customerID != defaultCustomerIDEntry) and customerID.isdigit() and (sessionText != "Select A Session") and (sessionText != "Select A Date"):
            beginTime, staffMember = sessionText.split(", ", 1)[0].replace(":", ""), sessionText.split(", ", 1)[1]

            chosenDate = dateCalendar.get_date()
            sessionsOnDate = sessionSearch(chosenDate)

            try:
                # Loading data from file
                with open(customerFilePath, 'r') as dataFile:
                    data = json.load(dataFile)

                    customerPresentBool = False
                    for i in range(len(data["customers"])):
                        if str(data["customers"][i]["customerID"]) == customerID:
                            customerPresentBool = True
                            break

            # Accounting for errors
            except:
                messagebox.showerror("Error", "Problem retrieving file")
                return

            if not customerPresentBool:
                messagebox.showerror("Error", "Customer does not exist")
                return

            for i in range(len(sessionsOnDate["lessons"])):
                if (int(sessionsOnDate["lessons"][i]["beginTime"]) == int(beginTime) and sessionsOnDate["lessons"][i]["staffMember"] == staffMember):
                    sessionLessonIndex = i
                    break

            try:
                # Loading data from file
                with open(sessionFilePath, 'r') as dataFile:
                    data = json.load(dataFile)
                    
                    sessionIndex = binarySearchSessions(data["sessions"], chosenDate)
                    data["sessions"][sessionIndex]["lessons"][sessionLessonIndex]["customers"].append(customerID)

                # Saving data to file
                with open(sessionFilePath , 'w') as dataFile:
                    json.dump(data, dataFile, indent=4)
            
                chosenDate = f'{chosenDate[6:]}/{chosenDate[4:6]}/{chosenDate[:4]}'
                staffChangesUpdate(f'Added Customer {customerID} to Session on {chosenDate}, ran by {staffMember}')
                addCustomerButton.focus_set()

                # Resetting global currentSessionData
                chosenDate = dateCalendar.get_date()
                availableSessions = sessionSearch(chosenDate)
                global currentSessionData
                currentSessionData = availableSessions
                dateInformationLabelUpdate(sessionText)

            # Accounting for errors
            except Exception as error:
                print("Session customer addition " + str(error))

        else:
            messagebox.showerror("Error", "Please enter a valid customer ID, and have a date selected")

    # Session Customer Addition
    def sessionCustomerDeletion(sessionText, customerID):
        if (customerID != defaultCustomerIDEntry) and customerID.isdigit():
            sessionText = sessionText.get()
            beginTime, staffMember = sessionText.split(", ", 1)[0].replace(":", ""), sessionText.split(", ", 1)[1]

            chosenDate = dateCalendar.get_date()
            sessionsOnDate = sessionSearch(chosenDate)

            for i in range(len(sessionsOnDate["lessons"])):
                if (int(sessionsOnDate["lessons"][i]["beginTime"]) == int(beginTime) and sessionsOnDate["lessons"][i]["staffMember"] == staffMember):
                    sessionLessonIndex = i
                    break

            try:
                # Loading data from file
                with open(sessionFilePath, 'r') as dataFile:
                    data = json.load(dataFile)
                    
                    sessionIndex = binarySearchSessions(data["sessions"], chosenDate)
                    customerData = data["sessions"][sessionIndex]["lessons"][sessionLessonIndex]["customers"]
                    customerPresentBool = False
                    for i in range(len(customerData)):
                        if customerData[i] == customerID:
                            customerPresentBool = True
                            break
                    
                    if customerPresentBool:
                        data["sessions"][sessionIndex]["lessons"][sessionLessonIndex]["customers"] = [customer for customer in customerData if customer != customerID]
                    else:
                        messagebox.showerror("Error", "Customer not attending session")

                # Saving data to file
                with open(sessionFilePath , 'w') as dataFile:
                    json.dump(data, dataFile, indent=4)
            
                chosenDate = f'{chosenDate[6:]}/{chosenDate[4:6]}/{chosenDate[:4]}'
                staffChangesUpdate(f'Added Customer {customerID} to Session on {chosenDate}, ran by {staffMember}')
                deleteCustomerButton.focus_set()
                
                # Resetting global currentSessionData
                chosenDate = dateCalendar.get_date()
                availableSessions = sessionSearch(chosenDate)
                global currentSessionData
                currentSessionData = availableSessions
                dateInformationLabelUpdate(sessionText)


            # Accounting for errors
            except Exception as error:
                print("Session customer addition " + str(error))

        else:
            messagebox.showerror("Error", "Please enter a valid customer ID")

    # Updates sessionOptions Drop Down When Calendar Date Is Picked
    def sessionOptionsDropDownUpdate(event):

        dateInformationStringVar.set("Select A Session")
        
        # Searching for sessions on selected date
        chosenDate = dateCalendar.get_date()
        availableSessions = sessionSearch(chosenDate)
        global currentSessionData
        currentSessionData = availableSessions

        # Setting label to date
        chosenDateString = f'{chosenDate[6:]}/{chosenDate[4:6]}/{chosenDate[:4]}'
        dateSelectedLabel.configure(text=chosenDateString)

        # Checking if date is already in file
        if availableSessions != -1:

            # Creating array to be used for drop down
            sessionOptions = []
            if len(currentSessionData["lessons"]) > 0:
                for i in range(len(currentSessionData["lessons"])):
                    appendText = str(currentSessionData["lessons"][i]["beginTime"])
                    appendText = appendText[:2] + ":" + appendText[2:]
                    appendText += f', {currentSessionData["lessons"][i]["staffMember"]}'
                    sessionOptions.append(appendText)

            # Populating drop down
            sessionOptions.insert(0, "Select A Session")
            sessionDropDown["menu"].delete(0, "end")
            print(sessionOptions)
            for session in sessionOptions:
                sessionDropDown["menu"].add_command(label=session, command=lambda value=session: sessionText.set(value))
            sessionText.set("Select A Session")
            messagebox.showinfo("Session Results", f'{len(currentSessionData["lessons"])} Sessions Found')
        
        else:
            # Appending to drop down
            dateInformationStringVar.set("Select A Date")
            sessionDropDown["menu"].delete(0, "end")
            sessionDropDown['menu'].add_command(label="Select A Date", command=tk._setit(sessionText, "Select A Date"))
            sessionText.set("Select A Date")
            messagebox.showinfo("Session Results", f'No Sessions Found')
            

        # Resetting entries
        fillEntry(customerIDEntry, defaultCustomerIDEntry, True)
        fillEntry(beginTimeEntry, defaultBeginTimeEntry, True)
        fillEntry(endTimeEntry, defaultEndTimeEntry, True)
        staffText.set(staffOptions[0])

    # Deleting old entries
    def deleteOldSessions(sessionFilePath):
        try:
            # Load session data from the file
            with open(sessionFilePath, 'r') as dataFile:
                data = json.load(dataFile)

            # Get the current date and the cutoff date (7 days ago)
            current_date = datetimedt.today()
            cutoff_date = current_date - timedelta(days=14)

            # Filter out sessions older than a week
            data["sessions"] = [
                date for date in data["sessions"]
                if datetimedt.strptime(date["date"], "%Y%m%d") >= cutoff_date
            ]

            # Filter out days with no sessions on
            data["sessions"] = [
                date for date in data["sessions"]
                if len(date["lessons"]) > 0
            ]

            # Save the updated session data back to the file
            with open(sessionFilePath, 'w') as dataFile:
                json.dump(data, dataFile, indent=4)

        # Accounting for errors
        except Exception as error:
            print("Error deleting old sessions: " + str(error))

    # Updates the Scrolling Label
    def dateInformationLabelUpdate(sessionText):
        print(sessionText)
        def subtractTimes(time1, time2):
            # Convert HHMM strings to datetime objects
            fmt = "%H%M"
            t1 = datetimedt.strptime(time1, fmt)
            t2 = datetimedt.strptime(time2, fmt)

            # Calculate the difference
            diff = t1 - t2

            # Format the result back to HHMM
            hours, remainder = divmod(diff.seconds, 3600)
            minutes = remainder // 60

            return f"{hours:02}{minutes:02}"
        
        if sessionText != "Select A Session" and sessionText != "Select A Date":

            sessionTime, sessionStaff = sessionText.split(", ", 1)[0], sessionText.split(", ", 1)[1]
            
            global currentSessionData
            sessionTime = sessionTime.replace(":", "")
            sessionIndex = listLinearSearchIndex(currentSessionData, sessionTime, sessionStaff)
            if sessionIndex == -1:
                return

            beginTimeVar = currentSessionData["lessons"][sessionIndex]["beginTime"]
            endTimeVar = currentSessionData["lessons"][sessionIndex]["endTime"]
            customerListVar = currentSessionData["lessons"][sessionIndex]["customers"]
            staffMemberVar = currentSessionData["lessons"][sessionIndex]["staffMember"]
            dateVar = currentSessionData["date"]

            timeLengthVar = subtractTimes(endTimeVar, beginTimeVar)
            dateVar = f'{dateVar[6:]}/{dateVar[4:6]}/{dateVar[:4]}'
            beginTimeVar = f'{beginTimeVar[:2]}:{beginTimeVar[2:]}'
            endTimeVar = f'{endTimeVar[:2]}:{endTimeVar[2:]}'
            timeLengthVar = ("0" * (4 - len(timeLengthVar))) + timeLengthVar

            if len(timeLengthVar[:2].lstrip("0")) > 0:
                hrsText = " hours" if int(timeLengthVar[:2].lstrip("0")) > 1 else " hour"
            else:
                hrsText = ""

            if len(timeLengthVar[2:].lstrip("0")) > 0:
                minText = " minutes" if int(timeLengthVar[2:].lstrip("0")) > 1 else " minute"
            else:
                minText = ""

            conText = " and " if hrsText and minText else ""
            timeLengthVar = f'Lasts {timeLengthVar[:2].lstrip("0")}{hrsText}{conText}{timeLengthVar[2:].lstrip("0")}{minText}'

            customerResultString = ""
            for customer in customerListVar:
                customerResultString += f'\n - {customer}'
            
            # Loading information into scrolling label
            dateInformationStringVar.set(f'Session Date: {dateVar}\n'
                                        f'Session Time: {beginTimeVar} to {endTimeVar}\n'
                                        f'Length: {timeLengthVar}\n'
                                        f'Staff Member: {staffMemberVar}\n'
                                        f'Customers: {customerResultString}')
        
            # Filling entries
            fillEntry(customerIDEntry, defaultCustomerIDEntry)
            fillEntry(beginTimeEntry, beginTimeVar)
            fillEntry(endTimeEntry, endTimeVar)
            staffText.set(staffMemberVar)
            sessionDropDown.focus_set()
        
        else:
            # Resetting entries
            dateInformationStringVar.set("Select A Session")
            fillEntry(customerIDEntry, defaultCustomerIDEntry, True)
            fillEntry(beginTimeEntry, defaultBeginTimeEntry, True)
            fillEntry(endTimeEntry, defaultEndTimeEntry, True)
            staffText.set(staffOptions[0])
            sessionDropDown.focus_set()

    # Searching for a value in a list
    def listLinearSearchIndex(listArray, listTime, listStaff):
        for i in range(len(listArray["lessons"])):
            if (str(listArray["lessons"][i]["beginTime"]).strip() == str(listTime).strip()) and (str(listArray["lessons"][i]["staffMember"]).strip() == str(listStaff).strip()):
                return i
        return -1

    # Binary Search for Session Day
    def binarySearchSessions(dataSessions, searchTerm):
        left, right = 0, len(dataSessions) - 1
        while left <= right:
            mid = (left + right) // 2
            if int(dataSessions[mid]["date"]) == int(searchTerm):
                return mid
            elif int(dataSessions[mid]["date"]) < int(searchTerm):
                left = mid + 1
            else:
                right = mid - 1
        return -1

    # Date HH:MM validation
    def timeValidation(timeText):
        try:
            hours, minutes = timeText[:2], timeText[2:]
            return (0 <= int(hours) < 24) and (0 <= int(minutes) < 60)
        except:
            return False

    # Creating Window
    scheduleMenu = createMainWindowFunction("Schedule", 840, 640)

    # Binding Open Navigation On Window Close
    scheduleMenu.protocol("WM_DELETE_WINDOW", lambda: [scheduleMenu.destroy(), loadNavigationMenu()])

    # Creating Calendar
    dateCalendar = Calendar(scheduleMenu, selectmode="day", firstweekday="monday", date_pattern="yyyymmdd",
                            background="#0F1C26", foreground="#FFFFFF", headersbackground="#213E54", headersforeground="#FFFFFF",
                            selectbackground="#8ED0F1", selectforeground="#105B80",
                            normalbackground="#105B80", normalforeground="#FFFFFF",
                            weekendbackground="#105B80", weekendforeground="#FFFFFF",
                            othermonthbackground="#182E3E", othermonthforeground="#FFFFFF",
                            othermonthwebackground="#182E3E", othermonthweforeground="#FFFFFF")
    dateCalendar.bind("<<CalendarSelected>>", sessionOptionsDropDownUpdate)

    # Creating Scrolling Label
    dateInformationStringVar = createScrollingLabelFunction(scheduleMenu, "Select A Session", 40, 100, 240, 220)

    # Creating Labels
    dateSelectedLabel = createLabelFunction(scheduleMenu, "Select A Date", 40, 340, 220, 40, 10)

    # Creating Entries
    defaultCustomerIDEntry = "Customer ID here..."
    customerIDEntry = createEntryFunction(scheduleMenu, defaultCustomerIDEntry, 40, 420, 220, 40)
    
    defaultBeginTimeEntry = "Begin Time (HH:MM) here..."
    beginTimeEntry = createEntryFunction(scheduleMenu, defaultBeginTimeEntry, 40, 500, 200, 40)
    
    defaultEndTimeEntry = "End Time (HH:MM) here..."
    endTimeEntry = createEntryFunction(scheduleMenu, defaultEndTimeEntry, 260, 500, 200, 40)

    # Creating Drop Downs
    sessionOptions = ["Select A Date"]
    sessionText, sessionDropDown = createDropdownFunction(scheduleMenu, sessionOptions, 280, 340, 250, 40)
    sessionText.trace_add("write", lambda name, index, operation: dateInformationLabelUpdate(sessionText.get()))

    staffOptions = staffSearch()
    staffOptions.insert(0, "Select Staff")
    staffText, staffDropDown = createDropdownFunction(scheduleMenu, staffOptions, 40, 560, 420, 40)
    
    # Creating Buttons
    createSessionButton = createButtonFunction(scheduleMenu, "Create Session", lambda: sessionCreation(beginTimeEntry, endTimeEntry, staffText), 480, 560, 320, 40)
    editSessionButton = createButtonFunction(scheduleMenu, "Edit Session", lambda: sessionEditing(sessionText, beginTimeEntry, endTimeEntry, staffText), 480, 500, 320, 40)
    deleteSessionButton = createButtonFunction(scheduleMenu, "Delete Session", lambda: sessionDeletion(sessionText), 550, 340, 250, 40)
    addCustomerButton = createButtonFunction(scheduleMenu, "Add Customer", lambda: sessionCustomerAddition(sessionText, customerIDEntry.get()), 280, 420, 250, 40)
    deleteCustomerButton = createButtonFunction(scheduleMenu, "Delete Customer", lambda: sessionCustomerDeletion(sessionText, customerIDEntry.get()), 550, 420, 250, 40)

    # Positioning Calendar
    dateCalendar.place(x=320, y=100, width=480, height=220)

    # Additional Canvas Details
    lineCanvasOne = tk.Canvas(scheduleMenu, highlightthickness=0, bg="#FFFFFF")
    lineCanvasOne.place(x=40, y=398, width=760, height=2)
    
    lineCanvasTwo = tk.Canvas(scheduleMenu, highlightthickness=0, bg="#FFFFFF")
    lineCanvasTwo.place(x=40, y=478, width=760, height=2)

    # Calling function to delete old sessions
    deleteOldSessions(sessionFilePath)

    # Setting up the menu
    scheduleMenu.lift()
    scheduleMenu.attributes('-topmost', True)
    scheduleMenu.after_idle(scheduleMenu.attributes, '-topmost', False)
        
    scheduleMenu.mainloop()

loadLoginMenu()