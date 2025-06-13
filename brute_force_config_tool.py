# brute_force_config_tool.py

import tkinter as tk
from tkinter import messagebox
import json
import os

class BruteForceConfigTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Brute Force Configurator")
        self.root.geometry("400x300")
        self.config_file_path = "brute_force_config.json"

        # Instruction Label
        tk.Label(root, text="Configure Web Element Locators:", font=("Arial", 12, "bold")).pack(pady=10)

        # Username Field ID
        tk.Label(root, text="Username Field ID:").pack(pady=(5,0))
        self.username_entry = tk.Entry(root, width=50)
        self.username_entry.pack(pady=2)

        # Password Field ID
        tk.Label(root, text="Password Field ID:").pack(pady=(5,0))
        self.password_entry = tk.Entry(root, width=50)
        self.password_entry.pack(pady=2)

        # Login Button Locator (Optional) - Changed label and config key
        tk.Label(root, text="Login Button Locator (ID, XPath, or CSS Selector - Optional):").pack(pady=(5,0))
        self.login_button_entry = tk.Entry(root, width=50)
        self.login_button_entry.pack(pady=2)

        # Status Label
        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=5)

        # Load existing configuration on start
        self.load_config()

        # Save Button
        self.save_btn = tk.Button(root, text="Save Configuration", command=self.save_config)
        self.save_btn.pack(pady=20)


    def load_config(self):
        """Loads configuration from file and populates the fields."""
        if os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, 'r') as f:
                    config = json.load(f)
                self.username_entry.insert(0, config.get('username_field_id', ''))
                self.password_entry.insert(0, config.get('password_field_id', ''))
                # Changed from 'login_button_id' to 'login_button_locator'
                self.login_button_entry.insert(0, config.get('login_button_locator', ''))
                self.status_label.config(text="Configuration loaded.")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load configuration: {e}")
                self.status_label.config(text="Failed to load config.", fg="red")
        else:
            self.status_label.config(text="No existing configuration found.")
            # Set default placeholders for convenience if no config file exists
            # These are based on Netcam Studio HTML
            self.username_entry.insert(0, "mat-input-0") # Default for Netcam Studio Login Field
            self.password_entry.insert(0, "mat-input-1") # Default for Netcam Studio Password Field
            self.login_button_entry.insert(0, "//button//span[contains(text(), 'Sign In')]") # Default XPath for Netcam Studio Sign In button


    def save_config(self):
        """Saves current field values to a JSON configuration file."""
        config = {
            "username_field_id": self.username_entry.get().strip(),
            "password_field_id": self.password_entry.get().strip(),
            # Changed key name
            "login_button_locator": self.login_button_entry.get().strip()
        }
        
        try:
            with open(self.config_file_path, 'w') as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Success", f"Configuration saved to {self.config_file_path}")
            self.status_label.config(text="Configuration saved successfully!", fg="green")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration: {e}")
            self.status_label.config(text="Failed to save config.", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = BruteForceConfigTool(root)
    root.mainloop()