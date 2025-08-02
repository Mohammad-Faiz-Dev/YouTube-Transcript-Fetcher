from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def setup_driver():
    """Setup Chrome driver with options"""
    options = Options()
    options.add_argument("--headless")  # Uncomment to run in background
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    return driver


def get_transcript(driver, url):
    """Extract transcript from YouTube video"""
    try:
        # Navigate to the video
        driver.get(url)
        print(f"Loading video page...")
        time.sleep(5)  # Increased wait time for page to fully load

        # Scroll down a bit to ensure all elements are loaded
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)

        # Try multiple methods to find and click the transcript button (Because earlier ones didn't work, or did but only sometimes)
        transcript_button = None

        # Method 1: Look for transcript button in description area
        try:
            transcript_button = WebDriverWait(driver, 7).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//button[contains(@aria-label, 'Show transcript') or contains(@aria-label, 'transcript')]"))
            )
            print("Found transcript button (Method 1)")
        except TimeoutException:
            pass

        # Method 2: Look for the three-dot menu and transcript option
        if not transcript_button:
            try:
                # Click on the three-dot menu first
                menu_button = driver.find_element(By.XPATH, "//button[@aria-label='More actions']")
                driver.execute_script("arguments[0].scrollIntoView();", menu_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", menu_button)
                time.sleep(2)

                # Look for transcript option in the menu
                transcript_option = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "//yt-formatted-string[contains(text(), 'Show transcript') or contains(text(), 'Transcript')]"))
                )
                transcript_button = transcript_option
                print("Found transcript button (Method 2 - Menu)")
            except (TimeoutException, NoSuchElementException):
                pass

        # Method 3: Alternative selectors
        if not transcript_button:
            selectors = [
                "//button[@aria-label='Show transcript']",
                "//button[contains(text(), 'Show transcript')]",
                "//yt-button-renderer[contains(@aria-label, 'transcript')]",
                "//button[contains(@class, 'transcript')]"
            ]

            for selector in selectors: #using a for loop to make sure the loop loops over all the items in Raw Data.xlsx
                try:
                    transcript_button = driver.find_element(By.XPATH, selector)
                    print(f"Found transcript button (Method 3 - {selector})")
                    break
                except NoSuchElementException:
                    continue

        if not transcript_button: #even if not found after 3 tries
            return "Error: Transcript button not found"

        # Click the transcript button using JavaScript to avoid interactability issues
        try:
            driver.execute_script("arguments[0].scrollIntoView();", transcript_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", transcript_button)
            print("Clicked transcript button")
            time.sleep(3)
        except Exception as e:
            return f"Error clicking transcript button: {str(e)}"

        # Wait for transcript panel to load
        try:
            # Try multiple selectors for transcript container
            transcript_container = None
            selectors = [
                "//div[@id='segments-container']",
                "//ytd-transcript-renderer",
                "//div[contains(@class, 'transcript')]",
                "//div[@class='ytd-transcript-segment-renderer']"
            ]

            for selector in selectors:
                try:
                    transcript_container = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"Found transcript container: {selector}")
                    break
                except TimeoutException:
                    continue

            if not transcript_container:
                return "Error: Transcript panel failed to load"

        except Exception as e:
            return f"Error waiting for transcript panel: {str(e)}"

        # Extract transcript text
        try:
            time.sleep(2)  # Wait for transcript text to load

            # Try multiple selectors for transcript segments
            transcript_segments = []
            selectors = [
                "//div[@class='segment-text']",
                "//yt-formatted-string[@class='segment-text style-scope ytd-transcript-segment-renderer']",
                "//div[contains(@class, 'cue-group')]//div[contains(@class, 'cue')]",
                "//ytd-transcript-segment-renderer//yt-formatted-string",
                "//div[@class='segment-text style-scope ytd-transcript-segment-renderer']"
            ]

            for selector in selectors:
                transcript_segments = driver.find_elements(By.XPATH, selector)
                if transcript_segments:
                    print(f"Found {len(transcript_segments)} transcript segments using: {selector}")
                    break

            if not transcript_segments:
                return "Error: Could not extract transcript text"

            # Combine all segments
            transcript_text = ""
            for segment in transcript_segments:
                text = segment.text.strip()
                if text:
                    transcript_text += text + " "

            if not transcript_text.strip():
                return "Error: Transcript text is empty"

            # Check if transcript contains non-English characters (basic check for Hindi)
            has_hindi = any(ord(char) > 127 for char in transcript_text)
            has_english = any(char.isalpha() and ord(char) <= 127 for char in transcript_text)

            if not (has_english or has_hindi):
                return "Error: Neither English nor Hindi transcript available"

            print(f"Successfully extracted transcript ({len(transcript_text)} characters)")
            return transcript_text.strip()

        except Exception as e:
            return f"Error extracting transcript: {str(e)}"

    except Exception as e:
        return f"Error processing video: {str(e)}"


def main():
    # Setup driver
    driver = setup_driver()

    try:
        # ==== Load Excel File ====
        input_file = 'Raw Data.xlsx'
        df = pd.read_excel(input_file)

        # Making sure 'Transcript' column exists
        if "Transcript" not in df.columns:
            df['Transcript'] = ""

        print("Correct Excel File Selected, Processing...")

        # Process each URL
        for index, row in df.iterrows():
            url = row['YouTube URL']
            print(f"\nProcessing video {index + 1}/{len(df)}: {url}")

            # Get transcript
            transcript = get_transcript(driver, url)

            # Check if there was an error
            if transcript.startswith("Error:"):
                print(f"Failed to get transcript: {transcript}")
                df.at[index, 'Transcript'] = transcript
                continue

            # Save transcript to dataframe
            df.at[index, 'Transcript'] = transcript
            print(f"Successfully extracted transcript ({len(transcript)} characters)")

            # Save progress after each video (in case of interruption)
            df.to_excel(input_file, index=False)

            # Small delay between requests to be respectful
            time.sleep(2)

        # Final save
        df.to_excel(input_file, index=False)
        print(f"\nCompleted processing all videos. Results saved to {input_file}")

    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        # Close the driver
        driver.quit()


if __name__ == "__main__":
    main()