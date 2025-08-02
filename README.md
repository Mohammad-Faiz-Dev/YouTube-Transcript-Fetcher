# YouTube Transcript Fetcher
Automated tool to extract transcripts from YouTube videos using Selenium and save them in an Excel file. Ideal for researchers, content analysts, or anyone needing video transcripts in bulk.

🛠 Tech Stack
Python 3.7+

## Selenium – Browser automation for interacting with YouTube

## pandas – Data manipulation and Excel handling

## openpyxl – For writing .xlsx files

## Google Chrome + ChromeDriver

📁 Folder Structure

YouTube-Transcript-Fetcher/
│
├── main.py              # Core script that fetches YouTube transcripts
├── requirements.txt     # Python dependencies
└── Raw Data.xlsx        # Input/Output Excel file
📄 Raw Data.xlsx Format
The Excel file must include:

### YouTube URL	Transcript
https://www.youtube.com/watch?v=...	(Auto-filled)

### YouTube URL: Column of YouTube links (required).

### Transcript: Initially blank. The script fills this column.

### ⚙️ How It Works
- Loads Raw Data.xlsx containing YouTube video URLs.
- Opens each URL using Selenium in headless Chrome.
- Searches for the "Show transcript" button using multiple fallback strategies.
- Clicks it, waits for the panel, then scrapes and combines transcript text.
- Detects basic language presence (English/Hindi).
- Writes results back to Excel, saving after each processed video.

🚀 Getting Started
1. Clone the Repository
   
2. 
git clone https://github.com/yourusername/youtube-transcript-fetcher.git
cd youtube-transcript-fetcher)

4. Add Your YouTube URLs
Open Raw Data.xlsx and paste YouTube links under the YouTube URL column.

5. Run the Script
bash
Copy
Edit
python main.py
### ✅ Features
### Multi-method fallback for UI robustness

### Language check (basic Hindi/English detection)

### Headless mode for silent execution

### Writes output back to Excel in real time

### Handles partial failures gracefully

## 📦 Requirements

- selenium
- pandas
- openpyxl

### Install with:

pip install -r requirements.txt

## 🙏 Acknowledgements
### Claude AI – Helped with the core logic and fallback strategies used in main.py.

### ChatGPT (OpenAI) – Assisted in project structuring, debugging support, README writing, and overall refinement.

## 🔍 Troubleshooting
No transcript? The video may not have one.

Transcript panel not loading? YouTube UI may have changed; update XPath selectors.

ChromeDriver errors? Check compatibility with your browser version.

## 🧭 Roadmap
Add CLI options for input/output files

Multilingual transcript support

Retry queue for failed URLs

YouTube Data API integration for richer metadata

📄 License
MIT License — free to use, modify, and distribute.
