import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import re
import os
import io

# --- ASETUKSET ---
# Nämä ovat ne tiedostot, jotka sinun pitäisi ladata GitHubiin saadaksesi parhaan tuloksen.
USER_FONT_REGULAR = "MinionPro-Regular.otf"
USER_FONT_BOLD = "MinionPro-Bold.otf"

# Värit (hienostuneempi paletti)
BG_COLOR = "#FDFBF7"       # Hieman lämpimämpi paperin sävy
TEXT_COLOR = "#1A1A1A"     # Pehmeä musta
ACCENT_COLOR = "#8B0000"   # Syvä viininpunainen
LINE_COLOR = "#D3D3D3"     # Haalea harmaa viivoille

def get_font(font_path_user, font_name_system, size):
    """
    Yrittää ladata käyttäjän fontin. 
    Jos ei löydy, yrittää ladata Linuxin/Windowsin tyylikkään vakiofontin.
    Tämä korjaa 'skandiongelman'.
    """
    # 1. Käyttäjän oma fontti (paras)
    if os.path.exists(font_path_user):
        return ImageFont.truetype(font_path_user, size)
    
    # 2. Järjestelmän vakio Serif-fontit (Linux/Streamlit Cloud & Windows)
    # Streamlit Cloudissa on yleensä 'DejaVuSerif' tai 'LiberationSerif'
    system_fonts = [
        "DejaVuSerif.ttf",          # Yleinen Linuxissa
        "LiberationSerif-Regular.ttf", # Yleinen Linuxissa
        "times.ttf",                # Windows
        "arial.ttf"                 # Hätävara (sans-serif, mutta toimii ääkkösillä)
    ]
    
    for font in system_fonts:
        try:
            return ImageFont.truetype(font, size)
        except IOError:
            continue
            
    # 3. Jos mikään ei toimi (erittäin epätodennäköistä), käytetään rumaa oletusta
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
    # Skaalataan fonttikoot leveyden mukaan, jotta suhteet pysyvät hyvinä
    scale_factor = width / 600.0 
    
    padding = int(40 * scale_factor)
    font_size_title = int(36 * scale_factor)
    font_size_main = int(24 * scale_factor)
    font_size_sub = int(20 * scale_factor)
    
    # Ladataan fontit
    # Huom: Käytämme samaa logiikkaa boldille, jos bold-tiedosto puuttuu
    title_font = get_font(USER_FONT_BOLD, "DejaVuSerif-Bold.ttf", font_size_title)
    main_font = get_font(USER_FONT_BOLD, "DejaVuSerif-Bold.ttf", font_size_main)
    sub_font = get_font(USER_FONT_REGULAR, "DejaVuSerif.ttf", font_size_sub)

    # Lasketaan tarvittava korkeus tiiviimmällä välityksellä
    row_h_main = int(40 * scale_factor)
    row_h_sub = int(28 * scale_factor)
    
    current_y = padding + int(60 * scale_factor) # Otsikon tila
    
    for item in data:
        current_y += row_h_sub if item['is_sub'] else row_h_main
        # Lisätään pieni rako ryhmien väliin
        if not item['is_sub']:
            current_y += int(10 * scale_factor)

    total_height = current_y + padding
    
    # --- PIIRTÄMINEN ---
    img = Image.new('RGB', (width, total_height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Tyylikkäämpi reunus (double border)
    border_out = int(10 * scale_factor)
    border_in = int(14 * scale_factor)
    
    draw.rectangle(
        [border_out, border_out, width - border_out, total_height - border_out], 
        outline="#444444", width=2
    )
    draw.rectangle(
        [border_in, border_in, width - border_in, total_height - border_in], 
        outline="#444444", width=1
    )

    # Otsikko
    title_text = "Verokarhut"
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) / 2, padding), title_text, font=title_font, fill=ACCENT_COLOR)

    # Lista
    y = padding + int(70 * scale_factor)
    indent_main = int(25 * scale_factor)
    indent_text = int(70 * scale_factor)
    indent_sub = int(80 * scale_factor)
    indent_sub_text = int(140 * scale_factor)

    for item in data:
        num = item['num']
        text = item['text']
        
        if not item['is_sub']:
            # PÄÄKOHTA
            y += int(15 * scale_factor)
            draw.text((padding + indent_main, y), num, font=main_font, fill=ACCENT_COLOR)
            draw.text((padding + indent_text, y), text, font=main_font, fill=TEXT_COLOR)
            
            # Ohut viiva pääkohdan alle
            line_y = y + row_h_main - int(5 * scale_factor)
            draw.line(
                [padding + indent_main, line_y, width - padding - indent_main, line_y], 
                fill=LINE_COLOR, width=1
            )
            y += row_h_main + int(10 * scale_factor)
        else:
            # ALAKOHTA
            draw.text((padding + indent_sub, y), num, font=sub_font, fill="#555555")
            draw.text((padding + indent_sub_text, y), text, font=sub_font, fill=TEXT_COLOR)
            y += row_h_sub

    return img

# --- UI ---
st.set_page_config(page_title="Infolaatikko-kone", layout="centered")

st.title("🗞️ Sukututkijan infolaatikko")
st.markdown("Tämä työkalu luo tyylikkään, painokelpoisen kuvan aikakauslehteä varten.")

col1, col2 = st.columns([1, 1])

with col1:
    width_slider = st.slider("Kuvan leveys (px)", min_value=300, max_value=1200, value=500, step=50)
    
with col2:
    st.info("💡 Vinkki: 500-600px on hyvä leveys tekstipalstalle. Pienempi arvo tekee kuvasta tiiviimmän.")

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

text_input = st.text_area("Sisältö", value=default_text, height=300)

if text_input:
    parsed = parse_data(text_input)
    # Generoidaan kuva käyttäjän valitsemalla leveydellä
    final_img = create_infobox(parsed, width=width_slider)
    
    st.divider()
    st.write("### Valmis kuva")
    st.image(final_img, caption="Esikatselu", use_container_width=False)
    
    # Latauspainike
    buf = io.BytesIO()
    final_img.save(buf, format="PNG", dpi=(300, 300)) # Määritellään DPI painokelpoisuutta varten
    byte_im = buf.getvalue()

    st.download_button(
        label="📥 Lataa valmis kuva (PNG)",
        data=byte_im,
        file_name="verokarhut.png",
        mime="image/png"
    )

    # Tarkistus käyttäjälle
    if not os.path.exists(USER_FONT_REGULAR):
        st.warning("⚠️ Minion Pro -fonttia ei löytynyt. Käytetään korvaavaa fonttia (DejaVu Serif), joka toimii ääkkösillä, mutta ei näytä täysin samalta.")
