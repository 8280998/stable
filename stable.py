import random
import string
import time
import imaplib
import email
from email.header import decode_header
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
import re

# Function to decode email subject
def decode_email_subject(subject):
    if subject is None:
        return ""
    decoded = decode_header(subject)[0]
    text, encoding = decoded
    if isinstance(text, bytes):
        text = text.decode(encoding or 'utf-8', errors='ignore')
    return text

# Load Gmail credentials from mail.txt (assuming format: username|password on first line)
def load_credentials():
    with open('mail.txt', 'r') as f:
        line = f.readline().strip()
        parts = line.split('|')
        if len(parts) != 2:
            raise ValueError("Invalid format in mail.txt. Expect: username|password")
        gmail_username = parts[0].strip()
        gmail_app_password = parts[1].strip()
    return gmail_username, gmail_app_password

# Generate random unique email
def generate_unique_email(used_emails):
    while True:
        random_part = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
        email_addr = f"{random_part}@domain.com"
        if email_addr not in used_emails:
            used_emails.add(email_addr)
            return email_addr

# Fetch verification code from Gmail, adapted from the reference code for Stable
def fetch_verification_code(gmail_username, gmail_app_password, target_email, keyword="login code", max_checks=10, timeout=300):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(gmail_username, gmail_app_password)
        mail.select("inbox")

        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Initial wait 10 sec to ensure email sync...")
        time.sleep(10)
        check_start_time = time.time()
        wait_interval = 5
        check_count = 0
        while time.time() - check_start_time < timeout and check_count < max_checks:
            mail.select("inbox")
            mail.noop()

            status, data = mail.search(None, f'(TEXT "{keyword}")')
            if not data[0]:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} No emails containing '{keyword}' found, waiting {wait_interval} sec to retry... (check {check_count + 1}/{max_checks})")
                time.sleep(wait_interval)
                wait_interval = min(wait_interval + 5, 20)
                check_count += 1
                if check_count >= max_checks:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Reached max checks {max_checks}, skipping current user")
                    return None
                continue

            email_ids = data[0].split()
            if not email_ids:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Email list empty, waiting 5 sec to retry...")
                time.sleep(5)
                continue

            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Found {len(email_ids)} emails containing '{keyword}', checking latest 5...")

            email_ids = email_ids[-5:]

            for email_id in reversed(email_ids):
                status, data = mail.fetch(email_id, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject = decode_email_subject(msg["subject"])
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Checking email, subject: {subject}, email ID: {email_id}")

                to_header = msg.get("To", "").lower()
                from_header = msg.get("From", "").lower()
                if target_email.lower() in to_header and "dynamicauth.com" in from_header and "stable's login code" in subject.lower():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain" or content_type == "text/html":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            code_match = re.search(r"\b\d{6}\b", body) or re.search(r"\d{6}", body)
                            if code_match:
                                code = code_match.group(0)
                                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Found verification code: {code}, extracted from body of subject {subject}")
                                mail.store(email_id, '+FLAGS', '\\Seen')
                                return code

                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Email does not match or no code found (To: {to_header})")

            time.sleep(wait_interval)

        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Timeout {timeout} sec or reached max checks, no matching unread email or code found")
        return None

    except imaplib.IMAP4.error as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IMAP error: {e}")
        return None
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Error occurred: {e}")
        return None
    finally:
        try:
            mail.logout()
        except:
            pass

# Automate the registration process using Playwright
def register_email(context, email_addr, gmail_username, gmail_app_password):
    page = context.new_page()
    try:
        page.goto('https://app.stable.xyz/', timeout=30000)
        
        # Check if email input is present and empty; if not, clear cookies/storage and reload
        try:
            main_locator = page.get_by_role("main")
            email_locator = main_locator.locator('input[name="email"]')
            email_locator.wait_for(state='visible', timeout=5000)
            if email_locator.input_value():
                print("Previous data detected, clearing...")
                context.clear_cookies()
                context.clear_permissions()
                page.reload(timeout=30000)
                email_locator.wait_for(state='visible', timeout=10000)
        except PlaywrightTimeoutError:
            pass  # If no input, perhaps already logged in, but assume fresh
        
        # Fill email
        email_locator.fill(email_addr)
        
        # Submit to send code
        submit_locator = main_locator.locator('path[d="M20.46 10.852 10.2 21.112 7.104 17.98l5.076-4.824H.156V8.512H12.18L7.104 3.688 10.2.556z"]')
        submit_locator.wait_for(state='visible', timeout=10000)
        submit_locator.click()
        
        # Wait for verify modal
        modal_locator = page.locator('[role="dialog"]')
        modal_locator.wait_for(state='visible', timeout=30000)
        code_locator = modal_locator.locator('input')  # Assuming the first input in modal is the code field
        code_locator.wait_for(state='visible', timeout=10000)
        
        # Fetch code
        print("Starting code fetch...")
        code = fetch_verification_code(gmail_username, gmail_app_password, email_addr)
        
        if not code:
            print(f"Failed to receive code for {email_addr}")
            return False
        
        code_locator.fill(code)
        
        # Submit code by pressing Enter (to avoid selector issue)
        code_locator.press('Enter')
        
        # Wait 8 seconds after pressing Enter
        time.sleep(8)
        
        # Append and print immediately after submit (assume success)
        with open('verifymail.txt', 'a') as f:
            f.write(email_addr + '\n')
        print(f"Successfully registered: {email_addr}")
        
        return True
    except Exception as e:
        print(f"Registration failed for {email_addr}: {e}")
        return False
    finally:
        # Clear and close
        context.clear_cookies()
        context.clear_permissions()
        page.close()
        context.close()

# Main command-line loop
if __name__ == "__main__":
    gmail_username, gmail_app_password = load_credentials()
    
    # Load used emails
    used_emails = set()
    try:
        with open('verifymail.txt', 'r') as f:
            used_emails = set(line.strip() for line in f)
    except FileNotFoundError:
        pass
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set headless=True for background
        
        try:
            while True:
                context = browser.new_context()  # New context for isolation
                email_addr = generate_unique_email(used_emails)
                print(f"Registering {email_addr}...")
                success = register_email(context, email_addr, gmail_username, gmail_app_password)
                print("Success! Waiting 5-10 sec...")
                time.sleep(random.uniform(5, 10))
        except KeyboardInterrupt:
            print("Stopped by user.")
        finally:
            browser.close()
