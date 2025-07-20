# image.py
# This file uses PILLOW to generate card images for each member and then generate a printable PNG containing multiple cards.

from PIL import Image, ImageDraw, ImageFont


class CardImage:
    def __init__(self, base_image_path: str, font_path: str, font_size: int, width_mm=79.6, height_mm=47.98, dpi=300):
        self.width_px = int(width_mm / 25.4 * dpi)
        self.height_px = int(height_mm / 25.4 * dpi)
        self.base = Image.open(base_image_path).convert("RGBA").resize(
            (self.width_px, self.height_px), Image.Resampling.LANCZOS
        )
        self.image = self.base.copy()
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype(font_path, size=font_size)

    def add_text(self, data: dict[str, str]):
        mitgliedsnummer_textbox = self.draw.textbbox((0,0), data.get("Mitgliedsnummer", ""), font=self.font)
        eintrittsdatum_textbox = self.draw.textbbox((0,0), data.get("Datum Eintritt", ""), font=self.font)

        # Adjust positions based on text size
        mitgliedsnummer_textbox_width = mitgliedsnummer_textbox[2] - mitgliedsnummer_textbox[0]
        eintrittsdatum_textbox_width = eintrittsdatum_textbox[2] - eintrittsdatum_textbox[0]

        right_edge = 480
        x_text_mitgliedsnummer = right_edge - mitgliedsnummer_textbox_width
        x_text_eintrittsdatum = right_edge - eintrittsdatum_textbox_width

        y_text_mitgliedsnummer = 175
        y_text_eintrittsdatum = 315

        self.draw.text((x_text_mitgliedsnummer, y_text_mitgliedsnummer), data.get("Mitgliedsnummer", ""), fill="black", font=self.font)
        self.draw.text((x_text_eintrittsdatum, y_text_eintrittsdatum), data.get("Datum Eintritt", ""), fill="black", font=self.font)

    def get_image(self):
        return self.image


class SheetBuilder:
    def __init__(self, dpi=300):
        self.a4_width_px = int(210 / 25.4 * dpi)
        self.a4_height_px = int(297 / 25.4 * dpi)
        self.sheet = Image.new("RGBA", (self.a4_width_px, self.a4_height_px), "white")

    def add_cards(self, card_images: list[Image.Image], columns=2, spacing=20):
        card_width, card_height = card_images[0].size

        for index, card in enumerate(card_images):
            col = index % columns
            row = index // columns
            x = col * (card_width + spacing)
            y = row * (card_height + spacing)

            x = spacing + col * (card_width + spacing)
            y = spacing + row * (card_height + spacing)
            self.sheet.paste(card, (x, y))

    def save(self, output_path: str):
        self.sheet.save(output_path, format="PNG", dpi=(300, 300), quality=95)
        print(f"Sheet saved to {output_path}")
