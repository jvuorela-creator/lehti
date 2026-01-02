import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import re
import os
import io

# --- ASETUKSET ---
# Nämä tiedostot pitää olla samassa kansiossa GitHub-repositoriossa!
FONT_REGULAR = "MinionPro-Regular.otf"
FONT_BOLD = "MinionPro-Bold.otf"

# Värit
BG_COLOR = "#F9F7F1"
TEXT_COLOR = "#2A2A2A"
ACCENT_COLOR = "#800000"
BORDER_COLOR = "#555555"

def load_font(path, size):
    """Lataa fontin tai palauttaa oletuksen, jos tiedostoa ei ole pilvessä."""
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    else:
        return ImageFont.load_default()

def parse_data(text):
    lines = text.strip().split('\n')
    parsed = []
    for line in lines:
        line = line.strip()
        if not line: continue
        match = re.match(r'^(\d+(\.\d+)?)', line)
        if match:
            number = match.group(1)
            content = line[len(number):].strip()
            is_sub = '.' in number
            parsed.append({'num': number, 'text': content, 'is_sub': is_sub})
    return parsed

def create_infobox(data, width=800):
    padding = 60
    
    # Fonttien lataus (tarkistaa löytyykö tiedostot)
    # Otsikko isompi, leipäteksti pienempi
    title_font = load_font(FONT_BOLD, 42)
    main_font = load_font(FONT_BOLD, 28)
    sub_font = load_font(FONT_REGULAR, 26)

    # Jos fontit puuttuu, varoitetaan käyttäjää (vain visuaalinen indikaattori fontin koossa)
    if not os.path.exists(FONT_BOLD):
        st.warning(f"Huom: Fonttitiedostoa '{FONT_BOLD}' ei löytynyt kansiosta. Käytetään oletusfonttia.")

    # Lasketaan korkeus
    current_y = padding + 60
    for item in data:
        current_y += 35 if item['is_sub'] else 50
    total_height = current_y + padding
    
    # Luodaan kuva
    img = Image.new('RGB', (width, total_height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Reunukset
    draw.rectangle([15, 15, width - 15, total_height - 15], outline=BORDER_COLOR, width=2)
    draw.rectangle([19, 19, width - 19, total_height - 19], outline=BORDER_COLOR, width=1)

    # Otsikko
    title_text = "Verokarhut"
    # Keskitetään otsikko (yhteensopiva tapa)
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) / 2, padding), title_text, font=title_font, fill=ACCENT_COLOR)

    # Lista
    y = padding + 80
    for item in data:
        num = item['num']
        text = item['text']
        
        if not item['is_sub']:
            y += 15
            draw.text((padding + 20, y), num, font=main_font, fill=ACCENT_COLOR)
            draw.text((padding + 70, y), text, font=main_font, fill=TEXT_COLOR)
            y += 40
            # Viiva
            draw.line([padding + 20, y - 5, width - padding - 20, y - 5], fill="#DDDDDD", width=1)
        else:
            indent = 90
            draw.text((padding + indent, y), num, font=sub_font, fill="#666666")
            draw.text((padding + indent + 60, y), text, font=sub_font, fill=TEXT_COLOR)
            y += 35

    return img

# --- STREAMLIT UI ---
st.title("Aikakauslehti-generaattori")
st.write("Luo tyylikäs infolaatikko sukututkimusartikkeliin.")

# Oletusteksti
default_text = """1 Pakkotyöverokarhut
2 Henkiverokarhut
3 Tuottoverokarhut
3.1 Pelto-, metsä- ja karjaverokarhut
3.2 Rakennus- ja tonttiverokarhut
3.3 Elinkeinoverokarhut
4 Tulo- ja varainverokarhut
4.1 Tuloverokarhu
4.2 Varallisuusverokarhu
4.3 Perintöverokarhu
4.4 Siirtoverokarhut
5 Pahe- ja ylellisyysverokarhut
5.1 Alkoholi- ja tupakkaverokarhut
5.2 Makeis- ja virvoitusjuomaverokarhut
5.3 Koiraverokarhu
5.4 Huviverokarhu
5.5 Peliverokarhu
6 Ympäristöverokarhut
6.1 Autoverokarhut
6.2 Juna-, laiva- ja lentoverokarhut
6.3 Energiaverokarhut
7 Tulliverokarhu ja Alvi-karhu
7.1 Tulliverokarhu
7.2 Liikevaihtoverokarhu ja Alvi-karhu"""

# Tekstikenttä muokkausta varten
input_text = st.text_area("Syötä lista (numero ja teksti)", value=default_text, height=300)

if st.button("Luo kuva"):
    parsed = parse_data(input_text)
    
    # Luodaan kuva
    final_img = create_infobox(parsed)
    
    # Näytetään kuva selaimessa (TÄMÄ KORJAA ONGELMAN)
    st.image(final_img, caption="Esikatselu", use_container_width=True)
    
    # Muutetaan kuva ladattavaan muotoon
    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    # Latauspainike
    st.download_button(
        label="Lataa kuva (PNG)",
        data=byte_im,
        file_name="verokarhut_infolaatikko.png",
        mime="image/png"
    )
