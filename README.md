               .__.__      _________                                        
  _____ _____  |__|  |    /   _____/ ________________  ______   ___________ 
 /     \\__  \ |  |  |    \_____  \_/ ___\_  __ \__  \ \____ \_/ __ \_  __ \
|  Y Y  \/ __ \|  |  |__  /        \  \___|  | \// __ \|  |_> >  ___/|  | \/
|__|_|  (____  /__|____/ /_______  /\___  >__|  (____  /   __/ \___  >__|   
      \/     \/                  \/     \/           \/|__|        \/       

# email Scraper (Python)

> **DuckDuckGo search + Smart filtering + Email extraction from "Contact" pages.**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

---

**FOR EDUCATIONAL PURPOSE ONLY**

**WIP**

## Features

- Targeted search on **DuckDuckGo (HTML version)** with pagination
- Smart website filtering:
  - Exclude social media, directories, Wikipedia, etc.
  - Activity-specific exclusion rules (restaurant, hairdresser, lawyer…)
  - Keyword detection in domain and path
- Email extraction:
  - Via regex in page text
  - From `mailto:` links
  - Automatic follow-up of **"Contact"**, **"Legal notice"**, **"Privacy"** pages
- Random delays & **rotating User-Agents** → human-like behavior
- Structured CSV export: `City | Activity | URL | Email`

---

## Installation

### Requirements

- Python 3.8+
- `pip`

### Dependencies

bash
```pip install requests beautifulsoup4 lxml```

# Usage 

python scraper.py "Paris" --activite restaurant --pages 3 --output paris_restaurants.csv

# Ethics and legality

For legitimate and GDPR-compliant use only.
- Respecting robots.txt is recommended (not enforced here for simplicity)
- Request delays → no server overload
- Only extracts publicly available emails
- *Do not use for spam*


