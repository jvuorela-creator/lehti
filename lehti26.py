from PIL import Image, ImageDraw, ImageFont
import re
import os

# --- ASETUKSET ---
# Määritä polut Minion Pro -fontteihin. 
# Jos tiedostoja ei löydy, skripti yrittää käyttää järjestelmän oletusta.
FONT_REGULAR_PATH = "MinionPro-Regular.otf"
FONT_BOLD_PATH = "MinionPro-Bold.otf"

# Värit ja tyyli
BG_COLOR = "#F9F7F1"       # "Eggshell" / Vanha paperi -sävy
TEXT_COLOR = "#2A2A2A"     # Hyvin tumma harmaa (pehmeämpi kuin musta)
ACCENT_COLOR = "#800000"   # Tummanpunainen (numeroille/otsikoille)
BORDER_COLOR = "#555555"   # Reunuksen väri

IMAGE_WIDTH = 800
PADDING = 60
LINE_SPACING = 10

# Lähdeteksti (siistitty rivinvaihdoista)
RAW_DATA = """
1 Pakkotyöverokarhut
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
7.2 Liikevaihtoverokarhu ja Alvi-karhu
"""

def load_font(path, size, fallback="arial.ttf"):
    """Yrittää ladata halutun fontin, palauttaa oletuksen jos ei onnistu."""
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        print(f"Varoitus: Fonttia '{path}' ei löytynyt. Käytetään oletusta.")
        # Yritetään ladata yleinen serif-fontti Windows/Linux/Mac -poluista
        try:
             # Yleinen Windows polku Times New Romanille
            return ImageFont.truetype("times.ttf", size)
        except:
            return ImageFont.load_default()

def parse_data(text):
    """Jäsentää tekstin pääotsikoihin ja alaotsikoihin."""
    lines = text.strip().split('\n')
    parsed = []
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Etsitään numero alusta (esim "3" tai "3.1")
        match = re.match(r'^(\d+(\.\d+)?)', line)
        if match:
            number = match.group(1)
            content = line[len(number):].strip()
            is_sub = '.' in number # Jos numerossa on piste, se on alakohta
            parsed.append({'num': number, 'text': content, 'is_sub': is_sub})
    return parsed

def create_infobox(data):
    # 1. Ladataan fontit
    title_font = load_font(FONT_BOLD_PATH, 42)
    main_font_bold = load_font(FONT_BOLD_PATH, 28)
    sub_font_reg = load_font(FONT_REGULAR_PATH, 26)
    
    # 2. Lasketaan tarvittava korkeus
    # Arvioidaan korkeus (otsikko + rivit + välit)
    current_y = PADDING + 60 # Tila otsikolle
    for item in data:
        current_y += 35 if item['is_sub'] else 50
    
    total_height = current_y + PADDING
    
    # 3. Luodaan kuva
    img = Image.new('RGB', (IMAGE_WIDTH, total_height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # 4. Piirretään reunukset (kaksoisviiva tyylikkyyden vuoksi)
    border_gap = 15
    draw.rectangle(
        [border_gap, border_gap, IMAGE_WIDTH - border_gap, total_height - border_gap], 
        outline=BORDER_COLOR, width=2
    )
    draw.rectangle(
        [border_gap + 4, border_gap + 4, IMAGE_WIDTH - border_gap - 4, total_height - border_gap - 4], 
        outline=BORDER_COLOR, width=1
    )

    # 5. Piirretään pääotsikko
    title_text = "Verokarhut"
    # Keskitetään otsikko
    try:
        bbox = draw.textbbox((0, 0), title_text, font=title_font)
        text_width = bbox[2] - bbox[0]
    except AttributeError:
        # Vanhemmat Pillow versiot
        text_width = draw.textsize(title_text, font=title_font)[0]
        
    draw.text(((IMAGE_WIDTH - text_width) / 2, PADDING), title_text, font=title_font, fill=ACCENT_COLOR)

    # 6. Piirretään lista
    y = PADDING + 80
    
    for item in data:
        num = item['num']
        text = item['text']
        
        if not item['is_sub']:
            # PÄÄKOHTA (1, 2, 3...)
            y += 15 # Hieman extra väliä ennen uutta pääryhmää
            
            # Piirretään numero korostusvärillä
            draw.text((PADDING + 20, y), num, font=main_font_bold, fill=ACCENT_COLOR)
            # Piirretään teksti
            draw.text((PADDING + 70, y), text, font=main_font_bold, fill=TEXT_COLOR)
            y += 40
            
            # Piirretään ohut viiva pääkohdan alle
            draw.line([PADDING + 20, y - 5, IMAGE_WIDTH - PADDING - 20, y - 5], fill="#DDDDDD", width=1)
            
        else:
            # ALAKOHTA (3.1, 3.2...)
            # Sisennys
            indent = 90
            draw.text((PADDING + indent, y), num, font=sub_font_reg, fill="#666666")
            draw.text((PADDING + indent + 60, y), text, font=sub_font_reg, fill=TEXT_COLOR)
            y += 35

    return img

# --- AJO ---
if __name__ == "__main__":
    parsed_data = parse_data(RAW_DATA)
    final_image = create_infobox(parsed_data)
    
    output_filename = "verokarhut_infolaatikko.png"
    final_image.save(output_filename)
    print(f"Kuva luotu onnistuneesti: {output_filename}")
    
    # Avaa kuva heti (toimii useimmissa käyttöjärjestelmissä)
    try:
        final_image.show()
    except:
        pass