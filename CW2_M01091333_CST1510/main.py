import os
from pathlib import Path
from app.data.db import DB_PATH, connect_database
from app.data.schema import create_all_tables
from app.services.user_service import (
    validate_user,
    validate_pass,
    check_password_strength,
    check_user_exists,
    register_user,
    login_user,
    check_lockout,
    migrate_users_from_file
)

def setup_database():
    conn = connect_database()
    print("--- Initializing Database Setup ---")

    create_all_tables(conn)
    
    users_txt_path = Path("DATA/users.txt")
    migrate_users_from_file(users_txt_path)
    print("--- Database Setup Complete ---")

#Input from user for menu task as a loop until either valid input is given or user exits.
def main_menu():
    print('\nWelcome to the Multi-Domain Intelligence Platform\n')
    while True:
        #Menu/Start-up display for registration/login
        print("Please select an option from the following:\n\t1. Register as a new user\n\t2. Login as an existing user")
        try:
            #Input for choice of task
            choice = int(input("Please enter 1 or 2 (enter 0 to exit): "))
            
            #If user wants to exit program
            if choice == 0: 
                print("Thank you for using the Multi-Domain Intelligence Platform. Goodbye!\nExitting...")
                break
            
            #If user wants to register a new account
            elif choice == 1:
                #Display of function
                print("-- Registration --")
                
                #.strip() is used to remove any leading or trailing spaces or new line characters
            
                #Username - prompts until Valid
                while True:
                    username = input("Please enter your username: ").strip()
                    
                    #Validation check for username using predefined function
                    valid_user, msg = validate_user(username)
                    #If username is invalid, restarts loop
                    if not valid_user:
                        print(msg)
                        continue
                    
                    #Check for already existing usernames
                    if check_user_exists(username):
                        print(f'User: {username} already exists, please choose a different username.')
                        continue
                    break # Exits username loop if valid and not a duplicate
                
                #Password - prompts until valid
                while True:
                    password = input("Please enter a password: ").strip() 
                    
                    #Validation check for password using predefined function
                    valid_pass, msg = validate_pass(password)
                    #If password is invalid, restarts loop
                    if not valid_pass:
                        print(msg)
                        continue
                    
                    #Password strength check using predefined function
                    strength = check_password_strength(password)
                    #If password strength is not strong, restarts loop 
                    if strength != "Strong":
                        print(f'''
                            Your password strength is: {strength}. Please choose a stronger password.
                            It should be a minimum of 12 characters and contain one of each of the following:
                            - Uppercase letter
                            - Lowercase letter
                            - A digit
                            - A special character like '!','@','#',etc...\n''')
                        continue
                    break # Exits password loop if valid and strong
                
                #Group - prompts until valid
                while True:
                    try:
                        #Group to be assigned to
                        group = int(input("1. Cybersecurity Analysts\n2. Data Scientists\n3. IT Administrators\nPlease enter what group you belong to: "))
                    except ValueError:
                         print("The input you have entered is not among the options. Please enter only 1, 2 or 3.")
                         continue
                         
                    #If user enters an invalid group number - restarts loop
                    if group < 1 or group > 3:
                        print("The input you have entered is not among the options. Please enter only 1, 2 or 3.")
                        continue
                    break # Exits group loop if valid
                        
                #If all validations are passed, registers user and prints confirmation
                result = register_user(username, password, group)
                print(result)
                print()
                    
            #If user wants to login to an existing account 
            elif choice == 2:
                print("-- Login --")
                
                #Username - prompts until Valid
                while True:
                    username = input("Please enter your registered username: ").strip()
                    
                    #Making sure username is valid / exists
                    if not check_user_exists(username):
                        print("Incorrect username or this user doesn't exist.")
                        continue 
                    
                    #Making sure user is not locked out currently'
                    is_locked, msg = check_lockout(username)
                    if is_locked:
                        print(msg)
                        # This 'break' exits the username loop and goes back to the main menu
                        break 
                    
                    #If username is correct and not locked out, continues onto password
                    break
                
                # If the user was found to be locked out in the loop above,
                # 'is_locked' will be True, and we 'continue' to the main menu
                if is_locked:
                    continue

                #Password - prompts until lockout or correct
                while True:
                    password = input("Please enter your password: ").strip()
                    
                    #Login user function called and checked using the inputs given above
                    success, result_msg = login_user(username, password)
                    print(result_msg)
    
                    #If login successful, breaks loop and returns to main menu
                    if success:
                        print(f"--- Welcome {username}, you are logged in. ---")
                        # TODO: Add post-login menu here (e.g., show incidents, report new one)
                        break
                    
                    #If unsuccessful continues loop until lockout
                    
                    #Making sure user is not locked out *now*
                    is_locked, lock_msg = check_lockout(username)
                    if is_locked:
                        break
                    continue
                
            #If user inputs invalid option, print statement and restarts loop 
            elif choice < 0 or choice > 2:
                print("The input you have entered is not valid. Please enter either 1 or 2, thank you.")
      
        #If non-integer value is given, restarts loop after printing statement 
        except ValueError:
            print("The input you have entered is not valid. Please enter either 1 or 2, thank you.")

if __name__ == "__main__":
    # Run the setup once when the script starts
    setup_database()
    # Start the interactive menu
    main_menu()