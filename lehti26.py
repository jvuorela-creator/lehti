import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import re
import os
import io

# --- ASETUKSET ---
USER_FONT_REGULAR = "MinionPro-Regular.otf"
USER_FONT_BOLD = "MinionPro-Bold.otf"

# Värit
BG_COLOR = "#FDFBF7"
TEXT_COLOR = "#1A1A1A"
ACCENT_COLOR = "#8B0000"
LINE_COLOR = "#D3D3D3"
BORDER_COLOR = "#444444"

def get_font(font_path_user, font_name_system, size):
    size = int(size) # Varmistetaan että koko on kokonaisluku
    if os.path.exists(font_path_user):
        return ImageFont.truetype(font_path_user, size)
    
    system_fonts = [
        "DejaVuSerif.ttf", "LiberationSerif-Regular.ttf", "times.ttf", "arial.ttf"
    ]
    for font in system_fonts:
        try:
            return ImageFont.truetype(font, size)
        except IOError:
            continue
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

def create_infobox(data, width=600):
    # --- SKAALAUS JA MITOITUS ---
    scale_factor = width / 600.0 
    
    padding = int(40 * scale_factor)
    
    # Fonttikoot
    font_size_title = int(36 * scale_factor)
    font_size_main = int(24 * scale_factor)
    font_size_sub = int(20 * scale_factor)
    
    # Rivikorkeudet
    row_h_main = int(45 * scale_factor)
    row_h_sub = int(30 * scale_factor)
    extra_gap_after_main = int(10 * scale_factor)
    
    header_space = int(80 * scale_factor)

    # --- 1. LASKETAAN TARVITTAVA KORKEUS ---
    content_height = 0
    for item in data:
        if not item['is_sub']:
            content_height += row_h_main + extra_gap_after_main
        else:
            content_height += row_h_sub

    # Lisätään lopuksi reilusti tyhjää tilaa
    bottom_white_space = int(padding * 1.5)
    
    total_height = int(padding + header_space + content_height + bottom_white_space)
    width = int(width) # Varmistetaan int
    
    # --- 2. PIIRRETÄÄN ---
    img = Image.new('RGB', (width, total_height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Fontit
    title_font = get_font(USER_FONT_BOLD, "DejaVuSerif-Bold.ttf", font_size_title)
    main_font = get_font(USER_FONT_BOLD, "DejaVuSerif-Bold.ttf", font_size_main)
    sub_font = get_font(USER_FONT_REGULAR, "DejaVuSerif.ttf", font_size_sub)

    # Reunukset
    border_out = int(10 * scale_factor)
    border_in = int(14 * scale_factor)
    draw.rectangle([border_out, border_out, width - border_out, total_height - border_out], outline=BORDER_COLOR, width=2)
    draw.rectangle([border_in, border_in, width - border_in, total_height - border_in], outline=BORDER_COLOR, width=1)

    # Otsikko
    title_text = "Verokarhut"
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) / 2, padding), title_text, font=title_font, fill=ACCENT_COLOR)

    # Listan piirto
    y = int(padding + header_space)
    
    indent_main = int(25 * scale_factor)
    indent_text = int(70 * scale_factor)
    indent_sub = int(80 * scale_factor)
    indent_sub_text = int(140 * scale_factor)

    for item in data:
        num = item['num']
        text = item['text']
        
        if not item['is_sub']:
            # PÄÄKOHTA
            draw.text((padding + indent_main, y), num, font=main_font, fill=ACCENT_COLOR)
            draw.text((padding + indent_text, y), text, font=main_font, fill=TEXT_COLOR)
            
            line_y = int(y + row_h_main - (5 * scale_factor))
            draw.line(
                [padding + indent_main, line_y, width - padding - indent_main, line_y], 
                fill=LINE_COLOR, width=1
            )
            y += row_h_main + extra_gap_after_main
        else:
            # ALAKOHTA
            draw.text((padding + indent_sub, y), num, font=sub_font, fill="#555555")
            draw.text((padding + indent_sub_text, y), text, font=sub_font, fill=TEXT_COLOR)
            y += row_h_sub

    return img

# --- UI LOGIIKKA ---
st.set_page_config(page_title="Infolaatikko", layout="centered")
st.title("🗞️ Sukututkijan Infolaatikko")

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

# KÄYTETÄÄN LOMAKETTA (FORM) JOTTA SIVU EI VÄLKKYISI
with st.form("settings_form"):
    col1, col2 = st.columns([1, 1])
    with col1:
        width_slider = st.slider("Kuvan leveys (px)", 400, 1000, 500, 50)
    with col2:
        st.write("Säädä leveyttä sopivaksi.")
        
    text_input = st.text_area("Sisältö", value=default_text, height=300)
    
    # Tämä nappi laukaisee piirtämisen
    submitted = st.form_submit_button("Generoi kuva")

if submitted or text_input:
    # Yritetään luoda kuva ja napataan mahdolliset virheet
    try:
        parsed = parse_data(text_input)
        
        if len(parsed) == 0:
            st.warning("Lista näyttää tyhjältä. Tarkista, että riveillä on numero alussa (esim '1 Otsikko').")
        else:
            final_img = create_infobox(parsed, width=width_slider)
            
            st.divider()
            st.write("### Esikatselu")
            st.image(final_img, caption="Valmis kuva", use_container_width=False)
            
            # Valmistellaan lataus
            buf = io.BytesIO()
            final_img.save(buf, format="PNG", dpi=(300, 300))
            byte_im = buf.getvalue()

            st.download_button(
                label="📥 Lataa kuva (PNG)",
                data=byte_im,
                file_name="verokarhut.png",
                mime="image/png"
            )

    except Exception as e:
        st.error(f"Tapahtui virhe kuvan luonnissa: {e}")
        st.write("Vinkki: Jos virhe liittyy fontteihin, tarkista että .otf tiedostot ovat oikeassa paikassa.")
