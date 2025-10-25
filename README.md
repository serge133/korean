
# Korean Mnemonics Manager: Complete Guide

---

## **Table of Contents**
1. [Introduction](#introduction)
2. [Generating Mnemonics with the Agent](#generating-mnemonics-with-the-agent)
3. [Managing Mnemonics with the Python Script](#managing-mnemonics-with-the-python-script)
   - [Installation](#installation)
   - [Adding Mnemonics](#adding-mnemonics)
   - [Recalling Mnemonics](#recalling-mnemonics)
   - [Exporting to Anki CSV](#exporting-to-anki-csv)
4. [Importing into Anki](#importing-into-anki)
5. [Example Workflow](#example-workflow)
6. [Troubleshooting](#troubleshooting)
7. [Customization](#customization)
8. [File Structure](#file-structure)
9. [Tips](#tips)

---

## **Introduction**
This guide provides a complete workflow for generating, managing, and studying Korean mnemonics using an AI agent and a Python script. You'll learn how to:
- Generate mnemonics with an AI agent.
- Manage and export mnemonics using a Python script.
- Import mnemonics into Anki for flashcard study.

---

## **Generating Mnemonics with the Agent**

### **How to Prompt the Agent**
- **For a single mnemonic:**
  Type a Korean word (e.g., "영화").
  The agent will respond with a formatted mnemonic, including:
  - Romanization
  - English meaning
  - Mnemonic phrase
  - Visual association
  - Notes

- **Example Output:**
  ```
  For **"영화" (yeonghwa)**, the Korean word for **"movie"**, here’s a mnemonic:

  **"Young-Wah!"**

  - **"영" (yeong)** sounds like **"young"**
  - **"화" (hwa)** sounds like **"wah!"**

  **Visual:** Imagine a group of young people watching a movie and shouting "Wah!" at an exciting scene.

  This ties the sound to the experience of watching a **movie**!
  ```

- **To export all generated mnemonics:**
  Say **"export"**.
  The agent will provide a JSON file with all mnemonics from the session.

- **Example JSON Output:**
  ```json
  [
    {
      "Korean Word": "영화",
      "Romanization": "yeonghwa",
      "Meaning": "movie",
      "Mnemonic": "Young-Wah!",
      "Visual": "Imagine a group of young people watching a movie and shouting 'Wah!' at an exciting scene.",
      "Notes": "This ties the sound to the experience of watching a movie!"
    }
  ]
  ```

---

## **Managing Mnemonics with the Python Script**

### **Features**
- Add mnemonics (single or bulk)
- Recall mnemonics by Korean or English word
- Export to Anki-importable CSV (Korean-first or English-first order)
- Import from JSON/CSV

---

### **Installation**
1. Save the script as `korean_mnemonics_manager.py`.
2. Install dependencies:
   ```bash
   pip install pandas
   ```

---

### **Adding Mnemonics**
- **Add a single mnemonic:**
  ```python
  manager.add_mnemonic("영화", "yeonghwa", "movie", "Young-Wah!", "Imagine a group of young people watching a movie and shouting 'Wah!' at an exciting scene.", "This ties the sound to the experience of watching a movie!")
  ```

- **Bulk import from JSON:**
  ```bash
  python korean_mnemonics_manager.py --import_json mnemonics.json
  ```

- **Bulk import from CSV:**
  ```bash
  python korean_mnemonics_manager.py --import_csv mnemonics.csv
  ```

---

### **Recalling Mnemonics**
- Recall by Korean word:
  ```bash
  python korean_mnemonics_manager.py --recall 영화
  ```

- Recall by English meaning:
  ```bash
  python korean_mnemonics_manager.py --recall movie
  ```

---

### **Exporting to Anki CSV**
- Export in Korean-first order:
  ```bash
  python korean_mnemonics_manager.py --export
  ```

- Export in English-first order:
  ```bash
  python korean_mnemonics_manager.py --export --english_first
  ```

---

## **Importing into Anki**

### **Steps**
1. Open Anki.
2. Click **File > Import**. 
3. Select the exported CSV file.
4. Map the fields:
   - **Front** → Front
   - **Back** → Back
5. Click **Import**. 

### **Anki CSV Format**
The script exports a CSV with two columns:
- **Front:** Korean word (and romanization) or English meaning (depending on order)
- **Back:** Meaning, mnemonic, visual, and notes (or Korean word and details for English-first)

---

## **Example Workflow**

### **Step 1: Generate Mnemonics**
- Ask the agent for mnemonics:
  ```
  User: 영화
  Agent: [Generates mnemonic]
  User: export
  Agent: [Provides JSON file]
  ```

### **Step 2: Import JSON into the Manager**
```bash
python korean_mnemonics_manager.py --import_json mnemonics.json
```

### **Step 3: Export to Anki CSV**
```bash
python korean_mnemonics_manager.py --export
```

or for English-first cards:
```bash
python korean_mnemonics_manager.py --export --english_first
```

### **Step 4: Import into Anki**
- Follow the Anki import steps above.

---

## **Troubleshooting**
- **Missing data in CSV?**
  Ensure all fields (`Korean Word`, `Romanization`, `Meaning`, `Mnemonic`, `Visual`, `Notes`) are filled in the JSON/CSV.

- **Encoding issues?**
  Use `encoding='utf-8-sig'` in the script for special characters.

---

## **Customization**
- Edit the script to change the CSV format or add more fields.
- Modify the agent prompt to adjust mnemonic style.

---

## **File Structure**
- `korean_mnemonics_manager.py`: Main script
- `mnemonics.json`: Exported mnemonics from the agent
- `korean_mnemonics_for_anki.csv`: Anki-importable CSV

---

## **Tips**
- Use `--english_first` to create English → Korean flashcards.
- Regularly export and back up your mnemonics.
- Customize the script to fit your study needs.
