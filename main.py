import os
import math

from PIL.Image import Image

from utils.google import get_worksheet_data
from utils.image import CardImage, SheetBuilder

SERVICE_ACCOUNT_FILE = "rb-mitgliederausweise-credentials.json"

VALID_CATEGORIES = [
    "ordentliches Mitglied",
    "Familienmitgliedschaft"
]


def generate_card_image(row):
    card = CardImage(
        base_image_path="resources/RB_Mitgliedsausweis.png",
        font_path="resources/ARCADE.otf",
        font_size=30
    )

    mitgliedsnummer = row.get("Mitgliedsnummer")
    if mitgliedsnummer is None:
        print("Skipping row with missing Mitgliedsnummer")
        return None
    mitgliedsnummer = str(mitgliedsnummer)

    eintrittsdatum = row.get("Datum Eintritt")
    if eintrittsdatum is None:
        print("Skipping row with missing Eintrittsdatum")
        return None
    eintrittsdatum = str(eintrittsdatum)

    card.add_text({
        "Mitgliedsnummer": mitgliedsnummer,
        "Datum Eintritt": eintrittsdatum
    })

    return card.get_image()


def generate_all_sheets(cards: list[Image], output_dir="output", columns=2, rows=5, spacing=40):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    total_rows = len(cards)
    pages = math.ceil(total_rows / (columns * rows))

    for i in range(pages):
        chunk = cards[i * columns * rows:(i + 1) * columns * rows]
        sheet = SheetBuilder()
        sheet.add_cards(chunk, columns=columns, spacing=spacing)
        output_path = os.path.join(output_dir, f"mitgliedsausweise_page_{i + 1}.png")
        sheet.save(output_path)


def main():
    data = get_worksheet_data(SERVICE_ACCOUNT_FILE)
    # skip first row
    data = data[1:]
    cards = []
    for row in data:
        # check if row contains a "Name", to determine whether we're at the end of the data
        if not row.get("Name"):
            break
        # check if the category is valid
        if row.get("Mitglieder-kategorie") not in VALID_CATEGORIES:
            print(f"Skipping row with invalid category: {row.get('Mitglieder-kategorie')}")
            continue

        card_image = generate_card_image(row)
        if card_image:
            cards.append(card_image)

    if not cards:
        print("No valid cards generated. Exiting.")
        return

    print(f"Generated {len(cards)} cards. Creating sheets...")
    generate_all_sheets(cards, output_dir="output")


if __name__ == "__main__":
    main()
