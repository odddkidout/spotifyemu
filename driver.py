from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
import random
import string
import time
# For W3C actions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import cap
import subprocess



class Streamer:
    def __init__(self, NewInstance=False, email=None, password=None):
        self.email = email if email else None
        self.password = password if password else None
        options = AppiumOptions()
        if not NewInstance:
            options.load_capabilities({
                "platformName": "android",
                "appium:platformVersion": "12",
                "appium:deviceName": "sdk_gphone64_arm64",
                "appium:automationName": "UiAutomator2",
                "appium:appPackage": "com.spotify.music",
                "appium:appActivity": "com.spotify.music.MainActivity",
                "appium:ensureWebviewsHavePages": True,
                "appium:nativeWebScreenshot": True,
                "appium:newCommandTimeout": 3600,
                "appium:connectHardwareKeyboard": True,
                "appium:noReset": True,
                "appium:fullReset": False
            })
        else:
            options.load_capabilities({
                "platformName": "android",
                "appium:platformVersion": "12",
                "appium:deviceName": "sdk_gphone64_arm64",
                "appium:automationName": "UiAutomator2",
                "appium:appPackage": "com.spotify.music",
                "appium:appActivity": "com.spotify.music.MainActivity",
                "appium:ensureWebviewsHavePages": True,
                "appium:nativeWebScreenshot": True,
                "appium:newCommandTimeout": 3600,
                "appium:connectHardwareKeyboard": True,
            })

        self.driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

    def gen(self, length=10):
        """Generate a random string of fixed length."""
        self.email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length)) + '@nophear.in'
        self.password = self.email
        time.sleep(5)
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Sign up free\")"))
            ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Continue with email\")"))
            ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/email"))
        ).send_keys(''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + '@nophear.in')

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/email_next_button"))
        ).click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "com.spotify.music:id/input_password"))
        ).send_keys("ababsjjh@sdjkfhds.com")

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "com.spotify.music:id/password_next_button"))
        ).click()
        #year long pull
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,"new UiSelector().text(\"2014\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,"new UiSelector().text(\"2013\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,"new UiSelector().text(\"2012\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,"new UiSelector().text(\"2011\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,"new UiSelector().text(\"2010\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID,"com.spotify.music:id/age_next_button"))
        ).click()
        
        #  gender selection
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
                self.driver.switch_to.context(contexts[1])
        time.sleep(5)
        captcha = cap.capsolver()
        if not captcha:
            print("Captcha solving failed, exiting...")
            return
        print("Captcha solved, token:", captcha)
        injection = """
        const widget = document.querySelector('.g-recaptcha');
        const cbName = widget.getAttribute('data-callback');  
        window[cbName]('"""+captcha+"""');  
        document.querySelector('button[name="solve"]').click();
        """
        self.driver.execute_script(injection)
        time.sleep(3)
        contexts = self.driver.contexts
        print("Available contexts:", contexts)
        print("Current context:", self.driver.current_context)
        print("Switching to native context...")
        if len(contexts) > 1:
                self.driver.switch_to.context(contexts[0])
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,"new UiSelector().text(\"Continue\")"))
        ).click()
        
        
        
        #WebDriverWait(self.driver, 10).until(
        #    expected_conditions.presence_of_element_located((AppiumBy.XPATH, "//main[@id='encore-web-main-content']/div[2]/div/div/div/div/div"))
        #).click()
        #self.driver.execute_script("document.querySelector('textarea[name=\"g-recaptcha-response\"]').value = 'jhgjhf';")
        #time.sleep(5)
        #print(WebDriverWait(self.driver, 10).until(
        #    expected_conditions.presence_of_element_located((AppiumBy.XPATH, "//textarea[@name=\"g-recaptcha-response\"]"))
        #)._execute("value"))
        #print(self.driver.execute_script("return document.querySelector('textarea[name=\"g-recaptcha-response\"]').value;"))
        time.sleep(5)

        """time.sleep(5)
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.CheckBox"))
        ).click()
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.Button"))
        ).click()
        time.sleep(5)
        #selection of genre page"""
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Hindi\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"International\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/actionButton"))
        ).click()

        # selection of artist page
        """el27 = driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(0)")
        el27.click()
        el28 = driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(1)")
        el28.click()
        el29 = driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(2)")
        el29.click()
        el30 = driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(10)")
        el30.click()"""

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(0)"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(1)"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(2)"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().resourceId(\"com.spotify.music:id/image\").instance(10)"))
        ).click()
        time.sleep(10)

    def play(self, track=None,album=None, playlist=None):
        time.sleep(5)
        if track is None and album is None and playlist is None:
            print("No track, album or playlist specified. Launching Spotify app.")
            return 

        cmd = [
            "adb", "shell", "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", f"spotify:track:{track}?context=spotify:playlist:{playlist}",
            "-n", "com.spotify.music/.MainActivity"
        ]
        # Run the command, capture output for debugging
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Launched successfully:")
            print(result.stdout)
        else:
            print("Error launching:")
            print(result.stderr)

        """WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().className(\"android.widget.Button\").instance(4)"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().className(\"android.widget.Button\").instance(6)"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Search for something to listen to"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"dismiss\")"))
        ).click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"dismiss\")"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/query"))
        ).send_keys("romeoo ghumshuda")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().resourceId(\"com.spotify.music:id/row_root\").instance(0)"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/subtitle"))
        ).click()
"""










Stream = Streamer( NewInstance=False)
#Stream.gen()
Stream.play(track="0FTmksd2dxiE5e3rWyJXs6",playlist="37i9dQZF1DXcBWIGoYBM5M")
