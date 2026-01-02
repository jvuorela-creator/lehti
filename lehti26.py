from PIL import Image, ImageDraw, ImageFont
import re
import os
import sys

# --- VIANETSINTÄ-ASETUKSET ---
# Käytetään perusfonttia varmuuden vuoksi testivaiheessa
FONT_NAME = "arial.ttf" 

# Värit
BG_COLOR = "#F9F7F1"
TEXT_COLOR = "#2A2A2A"
ACCENT_COLOR = "#800000"
BORDER_COLOR = "#555555"

IMAGE_WIDTH = 800
PADDING = 60

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

def get_font(size):
    """Hakee perusfontin vianetsintää varten."""
    try:
        # Yritetään ladata Arial (yleisin Windows-fontti)
        return ImageFont.truetype(FONT_NAME, size)
    except IOError:
        # Jos ei onnistu, käytetään Pythonin sisäänrakennettua (ruma mutta toimii aina)
        print("Huom: Arial-fonttia ei löytynyt, käytetään bittikarttafonttia.")
        return ImageFont.load_default()

def parse_data(text):
    print("--- 1. Jäsennetään tekstiä ---")
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
            # Tulostetaan löydetty rivi varmistukseksi
            print(f"Löydetty: {number} - {content}")
    
    print(f"Yhteensä {len(parsed)} riviä löydetty.\n")
    return parsed

def create_infobox(data):
    if not data:
        print("VIRHE: Ei dataa piirrettäväksi!")
        return None

    print("--- 2. Lasketaan kuvan kokoa ---")
    title_font = get_font(40)
    main_font = get_font(28)
    sub_font = get_font(24)
    
    current_y = PADDING + 60
    for item in data:
        current_y += 35 if item['is_sub'] else 50
    total_height = current_y + PADDING
    print(f"Kuvan korkeudeksi tulee: {total_height} pikseliä")
    
    print("--- 3. Piirretään kuvaa ---")
    img = Image.new('RGB', (IMAGE_WIDTH, total_height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Reunukset
    draw.rectangle([15, 15, IMAGE_WIDTH - 15, total_height - 15], outline=BORDER_COLOR, width=2)

    # Otsikko
    draw.text((PADDING, PADDING), "Verokarhut (Testi)", font=title_font, fill=ACCENT_COLOR)

    # Lista
    y = PADDING + 80
    for item in data:
        num = item['num']
        text = item['text']
        
        if not item['is_sub']:
            # Pääkohta
            y += 15
            draw.text((PADDING + 20, y), num, font=main_font, fill=ACCENT_COLOR)
            draw.text((PADDING + 70, y), text, font=main_font, fill=TEXT_COLOR)
            y += 40
        else:
            # Alakohta
            indent = 90
            draw.text((PADDING + indent, y), num, font=sub_font, fill="#666666")
            draw.text((PADDING + indent + 60, y), text, font=sub_font, fill=TEXT_COLOR)
            y += 35

    return img

if __name__ == "__main__":
    parsed_data = parse_data(RAW_DATA)
    final_image = create_infobox(parsed_data)
    
    if final_image:
        filename = "verokarhut_testi.png"
        # Tallennetaan nykyiseen kansioon
        save_path = os.path.join(os.getcwd(), filename)
        
        final_image.save(save_path)
        print(f"\n--- VALMIS ---")
        print(f"Kuva tallennettu nimellä: {filename}")
        print(f"Täysi polku: {save_path}")
        
        # Yritetään avata
        try:
            final_image.show()
            print("Yritettiin avata kuva esikatseluun.")
        except:
            print("Kuvan automaattinen avaus epäonnistui, avaa tiedosto manuaalisesti.")
