# gst_app.py
import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Indian GST Calculator", layout="centered")

# -----------------------
# Helper functions
# -----------------------
def calc_from_included(total_price: float, rate: float, rounding: float):
    """
    Given total price (including GST) and rate (e.g. 0.18), return:
    base_price, gst_amount, cgst, sgst, total_price
    """
    if rate < 0:
        rate = 0
    base = total_price / (1 + rate)
    gst = total_price - base
    if rounding:
        base = round(base / rounding) * rounding
        gst = round(gst / rounding) * rounding
    cgst = gst / 2
    sgst = gst / 2
    return base, gst, cgst, sgst, total_price

def calc_from_excluded(base_price: float, rate: float, rounding: float):
    """
    Given base price (excluding GST) and rate (e.g. 0.18), return:
    total_price, gst_amount, cgst, sgst, base_price
    """
    gst = base_price * rate
    total = base_price + gst
    if rounding:
        gst = round(gst / rounding) * rounding
        total = round(total / rounding) * rounding
    cgst = gst / 2
    sgst = gst / 2
    return total, gst, cgst, sgst, base_price

def calc_from_gst_amount(gst_amount: float, rate: float, rounding: float):
    """
    Given GST amount and rate, compute base and total:
    base = gst_amount / rate
    """
    base = gst_amount / rate if rate != 0 else 0
    total = base + gst_amount
    if rounding:
        base = round(base / rounding) * rounding
        total = round(total / rounding) * rounding
    cgst = gst_amount / 2
    sgst = gst_amount / 2
    return base, total, cgst, sgst, gst_amount

def add_history(entry):
    """Add an entry (dict) to session history, keep max 10"""
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, entry)
    # keep only last 10
    st.session_state.history = st.session_state.history[:10]

def history_to_csv():
    if "history" not in st.session_state or not st.session_state.history:
        return None
    df = pd.DataFrame(st.session_state.history)
    return df.to_csv(index=False).encode("utf-8")

def history_to_txt():
    if "history" not in st.session_state or not st.session_state.history:
        return None
    lines = []
    for item in st.session_state.history:
        lines.append(f"{item['timestamp']} | {item['mode']} | Rate: {item['rate_pct']}% | Base: ₹{item['base']:.2f} | GST: ₹{item['gst']:.2f} | CGST: ₹{item['cgst']:.2f} | SGST: ₹{item['sgst']:.2f} | Total: ₹{item['total']:.2f}")
    return ("\n".join(lines)).encode("utf-8")

# -----------------------
# GST rate descriptions
# -----------------------
GST_DESCRIPTIONS = {
    5: "Essential items (some packaged foods, edible oils, etc.)",
    12: "Processed foods & household items (some processed foods, computers accessories, etc.)",
    18: "Electronics & most services (mobiles, many services, branded goods).",
    28: "Luxury goods (cars, cigarettes, high-end electronics, luxury items)."
}

# -----------------------
# UI: Theme styling
# -----------------------
def inject_theme_css(theme_choice: str):
    # Minimal CSS to mimic theme differences; change colors to taste
    base_css = """
    <style>
    .card {
        background: #d9edf7;
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .big-btn{
        display:inline-block;
        margin:4px 6px;
    }
    .title{
        font-weight:700;
        font-size:22px;
    }
    </style>
    """
    dark_css = """
    <style>
    .stApp { background-color: #0f1724; color: #e6eef8; }
    .card { background: #0b1220; color: #e6eef8; }
    .stButton>button { background-color:#1d293b; color:#e6eef8; }
    </style>
    """
    # Light theme: keep default, inject base
    if theme_choice == "Light":
        st.markdown(base_css, unsafe_allow_html=True)
    elif theme_choice == "Dark":
        st.markdown(base_css + dark_css, unsafe_allow_html=True)

# -----------------------
# App main layout
# -----------------------
st.markdown("<div class='title'>🇮🇳 Indian GST Calculator</div>", unsafe_allow_html=True)

col1, col2 = st.columns([2,1])

with col2:
    # History panel
    st.markdown("### History")
    if "history" in st.session_state and st.session_state.history:
        for idx, h in enumerate(st.session_state.history):
            st.markdown(f"- **{h['timestamp']}** — {h['mode']} — ₹{h['base']:.2f} → ₹{h['total']:.2f} (GST ₹{h['gst']:.2f})")
    else:
        st.info("No history yet — calculations will appear here.")
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear History"):
            st.session_state.history = []
            st.experimental_rerun()
    with c2:
        csv_data = history_to_csv()
        txt_data = history_to_txt()
        if csv_data:
            st.download_button("Download CSV", data=csv_data, file_name="gst_history.csv", mime="text/csv")
        else:
            st.button("Download CSV", disabled=True)
        if txt_data:
            st.download_button("Download TXT", data=txt_data, file_name="gst_history.txt", mime="text/plain")
        else:
            st.button("Download TXT", disabled=True)

with col1:
    inject_theme_css(st.sidebar.selectbox("Choose Theme", ["Light", "Dark"], index=0))

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # Quick GST buttons
    quick_rates = [5, 12, 18, 28]
    st.markdown("**Quick GST rates:**")
    qcols = st.columns(len(quick_rates))
    selected_quick = None
    for i, r in enumerate(quick_rates):
        if qcols[i].button(f"{r}%"):
            selected_quick = r

    # GST Mode (normal or reverse)
    mode = st.radio("Calculation Mode", ["Price Excluding GST (enter base)", "Price Including GST (enter total)", "Reverse: I have GST amount"], index=0)

    # GST rate selector (dropdown)
    if selected_quick:
        default_rate = selected_quick
    else:
        default_rate = 18

    rate_pct = st.selectbox("GST Rate (%)", options=[5,12,18,28], index=[5,12,18,28].index(default_rate))
    rate = rate_pct / 100.0

    # Show description
    if rate_pct in GST_DESCRIPTIONS:
        st.caption(f"Rate info: {GST_DESCRIPTIONS[rate_pct]}")

    # Rounding options
    rounding_choice = st.selectbox("Rounding", ["No rounding", "Round to ₹1", "Round to ₹0.50"], index=0)
    rounding_map = {"No rounding": None, "Round to ₹1": 1.0, "Round to ₹0.50": 0.5}
    rounding = rounding_map[rounding_choice]

    # Input fields based on mode
    if mode == "Price Excluding GST (enter base)":
        base_input = st.number_input("Base Price (₹)", min_value=0.0, format="%.2f")
        if st.button("Calculate (Excl GST)"):
            total, gst_amount, cgst, sgst, base_price = calc_from_excluded(base_input, rate, rounding)
            st.success(f"Total (including GST): ₹{total:.2f}")
            st.write(f"GST amount ({rate_pct}%): ₹{gst_amount:.2f}")
            st.write(f"CGST ({rate_pct/2}%): ₹{cgst:.2f}  |  SGST ({rate_pct/2}%): ₹{sgst:.2f}")
            # add to history
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "mode": "Excl → Incl",
                "rate_pct": rate_pct,
                "base": base_price,
                "gst": gst_amount,
                "cgst": cgst,
                "sgst": sgst,
                "total": total
            }
            add_history(entry)

    elif mode == "Price Including GST (enter total)":
        total_input = st.number_input("Total Price (including GST) (₹)", min_value=0.0, format="%.2f")
        if st.button("Calculate (Incl GST)"):
            base, gst_amount, cgst, sgst, total_price = calc_from_included(total_input, rate, rounding)
            st.success(f"Base Price (excluding GST): ₹{base:.2f}")
            st.write(f"GST amount ({rate_pct}%): ₹{gst_amount:.2f}")
            st.write(f"CGST ({rate_pct/2}%): ₹{cgst:.2f}  |  SGST ({rate_pct/2}%): ₹{sgst:.2f}")
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "mode": "Incl → Excl",
                "rate_pct": rate_pct,
                "base": base,
                "gst": gst_amount,
                "cgst": cgst,
                "sgst": sgst,
                "total": total_price
            }
            add_history(entry)

    else:  # reverse: user has GST amount
        gst_input = st.number_input("GST Amount (₹)", min_value=0.0, format="%.2f")
        if st.button("Calculate from GST amount"):
            if rate == 0:
                st.error("GST rate must be > 0 for Reverse calculation.")
            else:
                base, total, cgst, sgst, gst_amount = calc_from_gst_amount(gst_input, rate, rounding)
                st.success(f"Base Price (excluding GST): ₹{base:.2f}")
                st.write(f"Total Price (including GST): ₹{total:.2f}")
                st.write(f"CGST ({rate_pct/2}%): ₹{cgst:.2f}  |  SGST ({rate_pct/2}%): ₹{sgst:.2f}")
                entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "mode": "Reverse (GST→Base)",
                    "rate_pct": rate_pct,
                    "base": base,
                    "gst": gst_amount,
                    "cgst": cgst,
                    "sgst": sgst,
                    "total": total
                }
                add_history(entry)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# Optional: show full history table and export buttons lower
# -----------------------
st.markdown("---")
st.markdown("### Full history table (last 10)")
if "history" in st.session_state and st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)
    st.dataframe(df_hist[["timestamp","mode","rate_pct","base","gst","cgst","sgst","total"]].rename(
        columns={"rate_pct":"Rate (%)","base":"Base (₹)","gst":"GST (₹)","cgst":"CGST (₹)","sgst":"SGST (₹)","total":"Total (₹)"}
    ), height=260)
    csv_data = history_to_csv()
    txt_data = history_to_txt()
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.download_button("Export CSV", data=csv_data, file_name="gst_history.csv", mime="text/csv")
    with c2:
        st.download_button("Export TXT", data=txt_data, file_name="gst_history.txt", mime="text/plain")
    with c3:
        # Export HTML that user can print to PDF
        html = df_hist.to_html(index=False)
        st.download_button("Export HTML", data=html.encode("utf-8"), file_name="gst_history.html", mime="text/html")
else:
    st.info("No records saved yet.")

# -----------------------
# Footer: tips
# -----------------------
st.markdown("---")
st.markdown("**Tips:**\n\n- CGST and SGST are automatically split 50/50.\n- Use quick-rate buttons for faster inputs.\n- Use 'Reverse' mode when you only know the GST amount.\n- Export history then open the HTML and choose 'Print → Save as PDF' to create a PDF invoice/report.")

