import pandas as pd
import os
from app.data.db import connect_database, DB_PATH
from app.data.security import reset_lockout
from app.services.user_service import (
    register_user, 
    login_user,
    validate_user,
    validate_pass,
    check_password_strength
)
from app.data.incidents import (
    insert_incident, 
    update_incident_status, 
    delete_incident,
    get_incidents_by_type_count,
    get_high_severity_by_status
)
from app.data.datasets import (
    insert_dataset,
    get_all_datasets,
    update_dataset_record_count,
    delete_dataset
)
from app.data.tickets import (
    insert_ticket,
    get_all_tickets,
    update_ticket_status,
    delete_ticket
)
from main import setup_database 

def run_comprehensive_tests():
    print("\n" + "="*60)
    print("Comprehensive test for setup")
    print("="*60)
    
    #Main setup of databases
    print("\n[--- Running Database Setup ---]")
    setup_database()
    print("[--- Database Setup Complete ---]")
    
    conn = connect_database()
    
    #Test of validation and strength function
    print("\nValidation & Strength Functions")
    
    #Validate for username
    valid, msg = validate_user("ok")
    print(f"Test to validate user (Short): {'✅' if not valid else '❌'}")
    valid, msg = validate_user("wrong user") 
    print(f"Test to validate user (Space): {'✅' if not valid else '❌'}")
    valid, msg = validate_user("validuser") 
    print(f"Test to validate user (Valid): {'✅' if valid else '❌'}")
    
    #Validation for password
    valid, msg = validate_pass("short") 
    print(f"Test to validate password (Short): {'✅' if not valid else '❌'}")
    long_pass = "a" * 51
    valid, msg = validate_pass(long_pass)
    print(f"Test to validate password (Long):  {'✅' if not valid else '❌'}")
    valid, msg = validate_pass("ValidPass")
    print(f"Test to validate password (Valid): {'✅' if valid else '❌'}")
    
    #Strength check for password
    strength = check_password_strength("weak")
    print(f"Test to check password strength (Weak): {'✅' if strength == 'Weak' else '❌'}")
    strength = check_password_strength("MediumPass123")
    print(f"Test to check password strength (Medium): {'✅' if strength == 'Medium' else '❌'}")
    strength = check_password_strength("StrongP@ss123!")
    print(f"Test to check password strength (Strong): {'✅' if strength == 'Strong' else '❌'}")

    #Authentication
    print("\nAuthentication functions")
    
    success, msg = register_user("test_user", "TestP@ss123!", 1)
    print(f"  Register New: {'✅' if success else '❌'} {msg}")
    
    success, msg = register_user("nova", "TestPass123!", 1)
    print(f"  Register Dup: {'✅' if not success else '❌'} {msg}")

    success, msg = login_user("test_user", "TestP@ss123!")
    print(f"  Login New:    {'✅' if success else '❌'} {msg}")
    
    success, msg = login_user("nova", "wrongpass")
    print(f"  Login Migrated (Wrong Pass): {'✅' if not success else '❌'} {msg}")
    
    success, msg = login_user("bob", "wrongpass")
    print(f"  Login Non-exist: {'✅' if not success else '❌'} {msg}")

    #Lockout functions
    print("\nLockout functions")
    register_user("lockout_user", "CorrectP@ss123!", 1)
    print("  Registered 'lockout_user'")
    success, msg = login_user("lockout_user", "wrong1")
    print(f"  Failed attempt 1: {'✅' if not success else '❌'} {msg}")
    success, msg = login_user("lockout_user", "wrong2")
    print(f"  Failed attempt 2: {'✅' if not success else '❌'} {msg}")
    success, msg = login_user("lockout_user", "wrong3")
    print(f"  Failed attempt 3: {'✅' if 'locked out' in msg else '❌'} {msg}")
    
    #Lockout reset function 
    reset_lockout('lockout_user')
    print("Lockout reset")
    success, msg = login_user("lockout_user", "CorrectP@ss123!")
    print(f"  Login after reset (Correct Pass): {'✅' if success else '❌'} {msg}")
    
    #CRUD operations for incidents
    print("\nCRUD (Incidents)")
    #Creation
    test_id = insert_incident(
        "2024-11-05", "Test Incident", "Low", "Open", "This is a test incident", "test_user"
    )
    print(f"  Create: {'✅' if test_id else '❌'} Incident #{test_id} created")
    
    #Update
    rows_updated = update_incident_status(test_id, "Resolved")
    print(f"  Update:  {'✅' if rows_updated == 1 else '❌'} Status updated")
    
    #Reading
    df = pd.read_sql_query(f"SELECT status FROM cyber_incidents WHERE id = {test_id}", conn)
    print(f"  Verify Update: {'✅' if df.iloc[0]['status'] == 'Resolved' else '❌'} Status is 'Resolved'")

    #Deletion
    rows_deleted = delete_incident(test_id)
    print(f"  Delete:  {'✅' if rows_deleted == 1 else '❌'} Incident deleted")
    df = pd.read_sql_query(f"SELECT * FROM cyber_incidents WHERE id = {test_id}", conn)
    print(f"  Verify Delete: {'✅' if len(df) == 0 else '❌'} Incident removed from DB")

    #CRUD operations for datasets
    print("\nCRUD (Datasets)")
    
    #Creation
    dataset_id = insert_dataset("Test Dataset", "Test", "Test Source", "2024-01-01", 100, 10.5)
    print(f"  Create: {'✅' if dataset_id else '❌'} Dataset #{dataset_id} created")

    #Update
    rows_updated = update_dataset_record_count(dataset_id, 9999)
    print(f"  Update:  {'✅' if rows_updated == 1 else '❌'} Record count updated")
    
    #Reading
    df = pd.read_sql_query(f"SELECT record_count FROM datasets_metadata WHERE id = {dataset_id}", conn)
    print(f"  Verify Update: {'✅' if df.iloc[0]['record_count'] == 9999 else '❌'} Count is 9999")

    #Deletion
    rows_deleted = delete_dataset(dataset_id)
    print(f"  Delete:  {'✅' if rows_deleted == 1 else '❌'} Dataset deleted")
    df = pd.read_sql_query(f"SELECT * FROM datasets_metadata WHERE id = {dataset_id}", conn)
    print(f"  Verify Delete: {'✅' if len(df) == 0 else '❌'} Dataset removed from DB")

    #CRUD operations for tickets
    print("\nCRUD (Tickets)")
    #Creation
    ticket_sql_id = insert_ticket("T-999", "High", "Open", "Test", "Test Ticket", "Test Desc")
    print(f"  Create: {'✅' if ticket_sql_id else '❌'} Ticket T-999 created")

    #Update
    rows_updated = update_ticket_status("T-999", "Resolved", is_resolved=True)
    print(f"  Update:  {'✅' if rows_updated == 1 else '❌'} Status updated")
    
    #Reading
    df = pd.read_sql_query("SELECT status, resolved_date FROM it_tickets WHERE ticket_id = 'T-999'", conn)
    print(f"  Verify Update: {'✅' if df.iloc[0]['status'] == 'Resolved' and df.iloc[0]['resolved_date'] else '❌'} Status is 'Resolved' and date set")

    #Deletion
    rows_deleted = delete_ticket("T-999")
    print(f"  Delete:  {'✅' if rows_deleted == 1 else '❌'} Ticket deleted")
    df = pd.read_sql_query("SELECT * FROM it_tickets WHERE ticket_id = 'T-999'", conn)
    print(f"  Verify Delete: {'✅' if len(df) == 0 else '❌'} Ticket removed from DB")
    
    #Query check 
    print("\nAnalytical Queries")
    df_by_type = get_incidents_by_type_count()
    print(f"  By Type:     {'✅' if len(df_by_type) > 0 else '❌'} Found {len(df_by_type)} incident types")
    print(df_by_type.to_string())
    
    df_high = get_high_severity_by_status()
    print(f"  High Severity: {'✅' if len(df_high) > 0 else '❌'} Found {len(df_high)} status categories")
    print(df_high.to_string())
    
    print("\nPlease delete the database manually to make sure it functions properly in the main file.")
    conn.close()   
    
    print("\n" + "="*60)
    print("All tests concluded!")
    print("="*60)

if __name__ == "__main__":
    run_comprehensive_tests()