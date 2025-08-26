# src/ui/app.py
import streamlit as st
import json

st.title("Validador de Plànols Tècnics")

# Carregar dades
with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\structured\\structured_output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

st.subheader("Cotes detectades")
for i, dim in enumerate(data["dimensions"]):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text(f"🔍 {dim['text']} (conf: {dim['confidence']:.1f})")
    with col2:
        is_ok = st.checkbox("Correcte?", value=True, key=f"dim_{i}")

st.subheader("Anotacions")
for note in data["notes"]:
    st.text(f"📝 {note['text']}")

if st.button("✅ Finalitzar Validació"):
    st.success("✅ Validació completada. Dades preparades per a exportar.")