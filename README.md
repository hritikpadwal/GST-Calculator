# GST-Calculator

# 🇮🇳 Indian GST Calculator (Streamlit App)

This is a simple and clean GST Calculator that I built using **Python** and **Streamlit**.  
My goal was to create a fast, beginner-friendly tool that helps anyone calculate GST, reverse GST, CGST/SGST split, and maintain a small history of recent calculations — all inside a modern web UI.

---

## ⭐ Features

### ✔ Quick GST Calculation
You can calculate:
- Price **including** GST → Get Base Price  
- Price **excluding** GST → Get Total Price  
- **Reverse GST** → Enter GST amount to find base price  

### ✔ Automatic CGST & SGST Split
Whatever GST rate you choose, the app instantly splits it into:
- **CGST (50%)**
- **SGST (50%)**

### ✔ History (Last 10 Calculations)
The app keeps your latest 10 calculations so you can refer back anytime.

### ✔ Theme Support
You can switch between:
- **Light Mode**
- **Dark Mode**

### ✔ Quick GST Rate Buttons
Instant buttons for common rates:
`5%` · `12%` · `18%` · `28%`

### ✔ GST Category Information
Each GST rate automatically shows a small description  
(essential items, processed goods, electronics, luxury items, etc.)

---

## 🛠 Tech Stack

- **Python**
- **Streamlit**
- **Pandas**

No databases or external servers required — everything runs directly through Streamlit.

---

## 🚀 How to Run Locally

1. Clone the repo:
```bash
git clone https://github.com/hritikpadwal/gst-calculator



2.# Install dependencies:
pip install -r requirements.txt


3.# Run the Streamlit app:
streamlit run gst_app.py



🌐 Live Demo

You can use the live hosted version here:
https://gst-calculator-india.streamlit.app

📌 Why I Built This

I wanted a GST tool that’s:

clean

fast

easy to understand

has both normal GST and reverse GST

and works well on both mobile and desktop

Most calculators online are cluttered or full of ads, so I decided to build my own streamlined version.

📬 Feedback / Suggestions?

If you have ideas or want extra features, feel free to open an issue or reach out.
I’ll keep improving the app as I learn more.

❤️ Thanks for checking out my project!



