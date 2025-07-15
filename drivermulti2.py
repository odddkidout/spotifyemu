import os
import sys
import threading
import traceback
import random
import string
import time
import subprocess

from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

import cap # Assuming 'cap' module handles captcha solving
import socket

# Global lock for safely incrementing the system port
system_port_lock = threading.Lock()
# Starting port for Appium's systemPort capability
# You can adjust this range if needed, just make sure it's not conflicting with other apps
STARTING_SYSTEM_PORT = 8200
current_system_port = STARTING_SYSTEM_PORT

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_next_system_port():
    """Safely gets the next available system port."""
    global current_system_port
    while True:
        with system_port_lock:
            port = current_system_port
            current_system_port += 1
            if not is_port_in_use(port):
                print(f"Port {port} is availavle, using it.")
                return port

    """check ig that port is not in use, if it is, increment and return the next available port
    This is a simple implementation, you might want to add more robust port checking logic. 
    For example, you could use socket to check if the port is available.
        """
    

"""
appium --allow-insecure chromedriver_autodownload
"""


class Streamer:
    def __init__(self, NewInstance=False, email=None, password=None, dev=None, system_port=None):
        self.email = email if email else None
        self.password = password if password else None
        options = AppiumOptions()
        self.dev = dev

        # Base capabilities common to both NewInstance scenarios
        base_capabilities = {
            "platformName": "Android",
            "appium:deviceName": "temp", # This might not be strictly needed if udid is provided
            "appium:udid": dev,
            "appium:automationName": "UiAutomator2",
            "appium:appPackage": "com.spotify.music", # Correct Spotify package name
            "appium:appActivity": "com.spotify.music.MainActivity",
            "appium:ensureWebviewsHavePages": True,
            "appium:nativeWebScreenshot": True,
            "appium:newCommandTimeout": 3600,
            "appium:noReset": False,
            "appium:fullReset": False,
            "goog:chromeOptions": {
                "androidPackage": "com.android.chrome", # Use the standard Chrome package
                "androidUseRunningApp": True
            }
        }

        if not NewInstance:
            # Capabilities for existing instances
            base_capabilities["appium:platformVersion"] = "9" # Or dynamically get from device
            options.load_capabilities(base_capabilities)
            if system_port:
                options.set_capability("appium:systemPort", system_port)
            else:
                print("Warning: systemPort not provided for an existing instance. This might lead to port conflicts.")
        else:
            # Capabilities for new instances (if you intend to use different settings)
            base_capabilities["appium:platformVersion"] = "12" # Example for a different version
            base_capabilities["appium:deviceName"] = "sdk_gphone64_arm64" # Example for a different device name
            base_capabilities["appium:noReset"] = True # Example of a different reset setting
            options.load_capabilities(base_capabilities)
            if system_port:
                options.set_capability("appium:systemPort", system_port)
            else:
                print("Warning: systemPort not provided for a new instance. This might lead to port conflicts.")


        try:
            self.driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
            print(f"Driver initialized for device {self.dev} on systemPort {system_port}")
        except Exception as e:
            print(f"Failed to initialize driver for device {self.dev} on systemPort {system_port}: {get_traceback(e)}")
            raise # Re-raise the exception to be caught by the calling thread


    def gen(self, length=10):
        """Generate a random string of fixed length."""
        self.email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length)) + '@nophear.in'
        self.password = self.email
        time.sleep(5)
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Sign up free\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Continue with email\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/email"))
        ).send_keys(self.email)

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/email_next_button"))
        ).click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "com.spotify.music:id/input_password"))
        ).send_keys(self.password)

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "com.spotify.music:id/password_next_button"))
        ).click()
        # year long pull
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"2014\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"2013\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"2012\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"2011\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"2010\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/age_next_button"))
        ).click()

        # gender selection
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/gender_button_male"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/name_next_button"))
        ).click()
        # recaptcha clicks
        time.sleep(3)
        contexts = self.driver.contexts
        print("Available contexts:", contexts)
        print("Current context:", self.driver.current_context)
        print("Switching to webview context...")
        if len(contexts) > 1:
            for _ in range(5):
                try:
                    # Switch to the last context, which is typically the WEBVIEW
                    self.driver.switch_to.context(contexts[-1])
                    break
                except Exception as e:
                    print(get_traceback(e))
                    time.sleep(1)
        time.sleep(5)
        captcha = cap.capsolver()
        if not captcha:
            print("Captcha solving failed, exiting...")
            return
        print("Captcha solved, token:", captcha)
        
        # Execute JavaScript for reCAPTCHA
        self.driver.execute_script("""const widget = document.querySelector('.g-recaptcha');if (widget) {const cbName = widget.getAttribute('data-callback');if (cbName && window[cbName]) {window[cbName]('""" + captcha + """');}}""")

        time.sleep(2)
        # Assuming this click is for the "Continue" button on the webview after captcha
        # It's better to use more specific selectors if possible.
        self.driver.execute_script('document.querySelector("#encore-web-main-content > div:nth-child(2) > div > div > div > div > div > button").click()')

        contexts = self.driver.contexts
        print("Available contexts:", contexts)
        print("Current context:", self.driver.current_context)
        print("Switching to native context...")
        if len(contexts) > 0: # Ensure there's a native context
            self.driver.switch_to.context(contexts[0])

        try:    
            WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Continue\")"))
            ).click()
        except Exception as e:
            print("Continue button not found, proceeding without it.")

        self.ACCOUNT_SAVER()

        time.sleep(5)

        #selection of genre page
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Hindi\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"International\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/actionButton"))
        ).click()

        # selection of artist page
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,
                                                             "new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(0)"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,
                                                             "new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(1)"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,
                                                             "new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(2)"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,
                                                             "new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(4)"))
        ).click()
        time.sleep(10)

    def play(self, track=None, album=None, playlist=None, playtime=60):
        time.sleep(5)
        if track is None and album is None and playlist is None:
            print("No track, album or playlist specified. Launching Spotify app.")
            return

        cmd = ["adb", "-s", self.dev, "shell", "am", "start", "-a", "android.intent.action.VIEW"]

        if track is not None:
            if album is not None:
                cmd.extend(["-d", f"spotify:track:{track}?context=spotify:album:{album}"])
            elif playlist is not None:
                cmd.extend(["-d", f"spotify:track:{track}?context=spotify:playlist:{playlist}"])
            else:
                cmd.extend(["-d", f"spotify:track:{track}"])
        elif album is not None:
            cmd.extend(["-d", f"spotify:album:{album}"])
        elif playlist is not None:
            cmd.extend(["-d", f"spotify:playlist:{playlist}"])

        cmd.extend(["-n", "com.spotify.music/.MainActivity"]) # Use correct package and activity here

        # Run the command, capture output for debugging
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Launched successfully on device {self.dev}:")
            print(result.stdout)
            time.sleep(playtime)
        else:
            print(f"Error launching on device {self.dev}:")
            print(result.stderr)

    def ACCOUNT_SAVER(self):
        with open("./ACCOUNTS_FILE/GEN_ACCOUNT.txt", "a") as file:
            file.write(f"{self.email}:{self.password}\n")


def get_traceback(e):
    lines = traceback.format_exception(type(e), e, e.__traceback__)
    return ''.join(lines)


class thread_with_trace(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


def run(dev, initial_delay):
    # Each thread gets its own unique systemPort
    port = get_next_system_port()
    time.sleep(initial_delay)
    while True:
        Stream = None # Initialize Stream to None
        try:
            print(f"Attempting to initialize Streamer for device {dev} with systemPort {port}")
            Stream = Streamer(NewInstance=False, dev=dev, system_port=port)
            Stream.gen()
            # Example track, album, playlist IDs
            Stream.play(track="0IMIrQKzgGICPqhP384drD", playtime=100) # Example track
            # Stream.play(album="YOUR_ALBUM_ID", playtime=100) # Example album
            # Stream.play(playlist="YOUR_PLAYLIST_ID", playtime=100) # Example playlist
            # Stream.play(track="YOUR_TRACK_ID", playlist="YOUR_PLAYLIST_ID", playtime=100) # Example track in playlist
            Stream.driver.quit()
            print(f"Successfully completed session for device {dev} on systemPort {port}")

        except Exception as e:
            print(f"An error occurred for device {dev} on systemPort {port}: {get_traceback(e)}")
            if Stream and Stream.driver:
                try:
                    Stream.driver.quit()
                    print(f"Driver quit for device {dev} on systemPort {port} after error.")
                except Exception as quit_e:
                    print(f"Error quitting driver for device {dev} on systemPort {port}: {quit_e}")
        finally:
            # Ensure the driver is quit even if an error occurs mid-process
            if Stream and Stream.driver:
                try:
                    Stream.driver.quit()
                except Exception as finally_quit_e:
                    print(f"Error during final quit for device {dev} on systemPort {port}: {finally_quit_e}")
            print(f"Restarting session for device {dev} on systemPort {port} in 5 seconds...")
            time.sleep(5) # Wait before retrying


def get_devices():
    """Get connected Android devices."""
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, text=True, check=True)
    devices = [
        line.split()[0]
        for line in result.stdout.splitlines()[1:]
        if 'device' in line and line.split()[0] != "" # Ensure device ID is not empty
    ]
    return devices


os.makedirs("./ACCOUNTS_FILE", exist_ok=True)
if not os.path.isfile('./ACCOUNTS_FILE/GEN_ACCOUNT.txt'):
    open("./ACCOUNTS_FILE/GEN_ACCOUNT.txt", "w+").close()

while True:
    devlist = get_devices()
    if len(devlist) >= 1:
        print(f"Found devices: {devlist}")
        break
    else:
        print(f"No devices found, retrying in 5 seconds...")
        time.sleep(5)

# Ensure Appium server is running with --allow-insecure chromedriver_autodownload
# You might want to start Appium programmatically here if it's not already running
# Example:
# try:
#     subprocess.Popen(["appium", "--allow-insecure", "chromedriver_autodownload"])
#     time.sleep(10) # Give Appium time to start
# except Exception as e:
#     print(f"Could not start Appium server: {e}")
#     sys.exit(1)

thread_count = len(devlist)
active_threads = []

for i in range(thread_count):
    t1 = thread_with_trace(target=run, args=[devlist[i], i ]) # Stagger initial start times
    t1.start()
    active_threads.append(t1)
    time.sleep(1) # Small delay between thread starts

# Optionally, wait for all threads to complete (though your 'run' loop is infinite)
# for t in active_threads:
#     t.join()