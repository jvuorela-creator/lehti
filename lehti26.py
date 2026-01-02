import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import re
import os
import io

# --- ASETUKSET ---
USER_FONT_REGULAR = "MinionPro-Regular.otf"
USER_FONT_BOLD = "MinionPro-Bold.otf"

# Värit
BG_COLOR = "#FDFBF7"       # Paperin sävy
TEXT_COLOR = "#1A1A1A"     # Teksti
ACCENT_COLOR = "#8B0000"   # Numerot ja otsikko
LINE_COLOR = "#D3D3D3"     # Erotinviivat
BORDER_COLOR = "#444444"   # Kehys

def get_font(font_path_user, font_name_system, size):
    """Hakee käyttäjän fontin tai toimivan järjestelmäfontin."""
    if os.path.exists(font_path_user):
        return ImageFont.truetype(font_path_user, size)
    
    system_fonts = [
        "DejaVuSerif.ttf",           # Linux/Streamlit default
        "LiberationSerif-Regular.ttf",
        "times.ttf",                 # Windows
        "arial.ttf"
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
    row_h_main = int(45 * scale_factor) # Hieman väljempi kuin aiemmin
    row_h_sub = int(30 * scale_factor)
    extra_gap_after_main = int(10 * scale_factor) # Rako pääkohdan jälkeen
    
    header_space = int(80 * scale_factor) # Tila otsikolle

    # --- 1. LASKETAAN TARVITTAVA KORKEUS TARKASTI ---
    # Simuloidaan listan läpikäynti, jotta tiedetään pikselintarkka korkeus
    content_height = 0
    for item in data:
        if not item['is_sub']:
            # Pääkohta + sen jälkeinen rako
            content_height += row_h_main + extra_gap_after_main
        else:
            # Alakohta
            content_height += row_h_sub

    # Lisätään lopuksi reilusti tyhjää tilaa (1.5 x padding)
    bottom_white_space = int(padding * 1.5)
