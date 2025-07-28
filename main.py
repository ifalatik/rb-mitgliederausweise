import os
import math

import click
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


@click.command()
@click.option('-s', '--start-mitgliedsnummer', default=None, help='Start Mitgliedsnummer for filtering')
@click.option('-e', '--end-mitgliedsnummer', default=None, help='End Mitgliedsnummer for filtering')
def main(start_mitgliedsnummer: str, end_mitgliedsnummer: str):
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

        mitgliedsnummer = row.get("Mitgliedsnummer")
        if not mitgliedsnummer:
            print("Skipping row with missing Mitgliedsnummer")
            continue
        try:
            mitgliedsnummer = int(mitgliedsnummer)
        except ValueError:
            print(f"Skipping row with invalid Mitgliedsnummer: {row.get('Mitgliedsnummer')}")
            continue

        # check if the Mitgliedsnummer is greater or equal to the start Mitgliedsnummer
        if start_mitgliedsnummer and mitgliedsnummer < int(start_mitgliedsnummer):
            print(f"Skipping row with Mitgliedsnummer {row.get('Mitgliedsnummer')} less than {start_mitgliedsnummer}")
            continue

        # check if the Mitgliedsnummer is less than or equal to the end Mitgliedsnummer
        if end_mitgliedsnummer and mitgliedsnummer > int(end_mitgliedsnummer):
            print(f"Skipping row with Mitgliedsnummer {row.get('Mitgliedsnummer')} greater than {end_mitgliedsnummer}")
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
