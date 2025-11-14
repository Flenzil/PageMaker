import questionary

from src.card import Card, DoubleSidedCard
from src.card_parser import CardParser
from src.cli_args_manager import CLIArgs
from PIL.Image import Image as PILImageType
import src.get_images as get_images
import xml.etree.ElementTree as ET

import src.params as params
import src.helpers as helpers

'''
Extracts card information from supplied XML file from XML_PATH and creates a list of DoubleSidedCard
objects, containing card information. 

Finds any images present in CUSTOM_IMAGE_PATH and prompts the user as to whether they would like
to add those card images to the project as front side cards or back side cards.

Calls get_images to fetch card images from disk or download images from Google Drive.
'''

def create_xml(id: str, slots: str, name: str, query: str) -> ET.Element:
    '''
    Create an in-memory XML element, matching the XML elements from MPCFill
    cards.
    '''
    card = ET.Element("card")
    ET.SubElement(card, "id").text = id
    ET.SubElement(card, "slots").text = slots
    ET.SubElement(card, "name").text = name
    ET.SubElement(card, "query").text = query
    return card


def add_image_to_page_prompt(extra_images: list[str], cards: list[Card]) -> dict:
    '''Prompt user to assign images that don't have an id to be
    added or added as a back to another card.

    Args:
        extra_images list(str): list of images that don't have an id
        cards (list[Card]): list of Card objects
    '''
    image_pairs = {}
    for image in extra_images:
        if image in image_pairs:
            #Image has been chosen as front face of a previous image
            continue

        add_to_page = questionary.select(f'Would you like to add {image} as a front face or a back face?',
                choices=['front', 'back']).ask()

        if add_to_page == 'front':
            image_pairs[image] = ''

        elif add_to_page == 'back':
            card_name_map = {card.name:card for card in cards}
            choices = []
            for card_name in card_name_map:
                if card_name not in image_pairs:
                    choices.append(card_name)

            for other_image in extra_images:
                if other_image not in image_pairs.values() and other_image != image:
                    if image_pairs.get(other_image, '') == '':
                        choices.append(other_image)

            front_image = questionary.select(f'Which card would you like to add {image} to the back of?',
                    choices=sorted(choices)).ask()
            
            try:
                image_pairs[card_name_map[front_image].id] = image
            except KeyError:
                image_pairs[front_image] = image

    return image_pairs


def add_extra_images(cards: list[Card]) -> tuple[list[Card], list[Card]]:
    '''Search params.CUSTOM_IMAGE_PATH for images 
    prompt to ask the user if they want to add them.

    Args:
        cards (list[Card]): list of Card objects

    Returns:
        list[Card]: list of Card objects generated from images in CUSTOM_IMAGE_PATH
    '''
    extra_images = helpers.get_all_images_from_folder(params.CUSTOM_IMAGE_PATH)

    if not extra_images:
        return [], []

    image_pairs = add_image_to_page_prompt(extra_images, cards)
    
    extra_cards = []
    extra_backs = []
    slot_number = 1000
    x_count = 1

    for front, back in image_pairs.items():
        # Cards with no backs
        if back == '':
            name = str(front)
            id = 'x' * x_count
            slots = str(slot_number)

            card_xml = create_xml(
                id=id,
                slots=slots,
                name=name,
                query=name
            )

            card = CardParser(card_xml).extract_card()
            extra_cards.append(card)

        elif isinstance(front, str) and '.' not in front and '.' not in back:
            # Cards with MPCFill front and custom back
            name = str(back)
            id = 'x' * x_count
            slots = ",".join(next(card.slots for card in cards if card.id == front))
            card_xml = create_xml(
                id=id,
                slots=slots,
                name=name,
                query=name
            )

            card = CardParser(card_xml).extract_card()
            extra_backs.append(card)

        else:
            # Cards with custom front and back
            name = str(front)
            id = 'x' * x_count
            slots = str(slot_number)

            x_count += 1

            name_back = str(back)
            id_back = 'x' * x_count

            card_xml = create_xml(
                id=id,
                slots=slots,
                name=name,
                query=name
            )

            card_xml_back = create_xml(
                id=id_back,
                slots=slots,
                name=name_back,
                query=name_back
            )

            card = CardParser(card_xml).extract_card()
            back = CardParser(card_xml_back).extract_card()

            extra_cards.append(card)
            extra_backs.append(back)

        slot_number += 1
        x_count += 1

    return extra_cards, extra_backs


def get_cards_info_from_xml(xml_file) -> tuple[list[Card], list[Card], Card]:
    '''
    Extracts card information from xml file

    Args:
        xml (Path): Path object containing path to xml file

    Returns:
        cards (ET.Element): XML object containing card information
        backs (ET.Element|None): XML object containing card information for back side of cards 
                                 or None if backs is absent
        generic_card_back (ET.Element): XML object containing information for generic back side of cards
    '''
    try:
        root = ET.parse(xml_file).getroot()
        cards_xml = root.find('fronts')
        backs_xml = root.find('backs')
        generic_card_back_id_xml = root.findtext('cardback')
    except ET.ParseError:
        raise Exception('XML file is empty!')

    if cards_xml is None:
        raise Exception('No cards found.')
    else:
        cards = []
        for card_xml in cards_xml.findall("card"):
            card = CardParser(card_xml).extract_card()
            cards.append(card)

    if backs_xml is None:
        backs = []
    else:
        backs = []
        for back_xml in backs_xml.findall("card"):
            back = CardParser(back_xml).extract_card()
            backs.append(back)

    if generic_card_back_id_xml is None:
        raise Exception('Generic card back id is missing.')
    else:
        generic_card_back_xml = create_xml(
            id=generic_card_back_id_xml,
            slots='-1',
            name='Generic card back.jpg',
            query='Generic card back'
        )
        generic_card_back = CardParser(generic_card_back_xml).extract_card()

    return cards, backs, generic_card_back


def remove_old_images(exceptions: list[Card]):
    '''
    Removes images from IMAGE_PATH, except those in exceptions.
    '''
    image_paths = [card.image_path for card in exceptions]
    if params.IMAGE_PATH.is_dir():
        for image in params.IMAGE_PATH.iterdir():
            if image not in image_paths:
                image.unlink()


def assign_images_to_cards(cards: list[Card], card_images: dict[str, PILImageType]) -> None:
    '''
    Assigns card images to card objects, adding generic back image if given.

    Args:
        cards (list[Card]): List of card objects containing card information
        card_images (dict[str, PILImageType]): dict mapping card IDs to their corresponding images
    '''

    for card in cards:

        # Skip custom cards whose images come from CUSTOM_IMAGE_PATH and not
        # from get_images
        if card.id not in card_images:
            continue

        image = card_images[card.id]

        card.set_image(image)


def combine_front_and_backs(fronts: list[Card], backs: list[Card], generic_back: Card|None = None) -> list[DoubleSidedCard]:
    '''
    Combine Card objects describing the fron and the back of a card into one single
    Card object using the `slots` parameter as the matching criterion.

    Args:
        fronts (list[Card]): list of Card objects representing front sides
        backs (list[Card]): list of Card objects representing back sides
        generic_back (Card|None): Card object representing the generic back side of the cards
    Returns:
        (list[DoubleSidedCard]): list of DoubleSidedCard objects representin front and back cards
    '''
    cards = []
    for front in fronts:

        back = next(
            (b for b in backs if (set(front.slots) & set(b.slots))),
            None 
        )

        if back is not None:
            card = front // back
        elif generic_back is not None:
            card = front // generic_back
            card.has_generic_back = True
        else:
            card = front // None

        cards.append(card)

    return cards


def create_cards(args: CLIArgs, xml = None) -> list[DoubleSidedCard]:
    '''
    Entry point for create_cards.

    Finds card information from .xml file and creates a list of Card objects
    from it.

    Args:
        args (CLIArgs): Object containing normalised command-line arguments.

    Returns:
        list[Card]: List of Card objects, each representing a unique card.
    '''

    if xml is None:
        xml_file = open(params.XML_PATH / 'cards.xml') 
    else: 
        xml_file = xml
    # Transform card data from xml elements to Card objects
    fronts, backs, generic_back = get_cards_info_from_xml(xml_file)

    # Remove images from a previous run except those that are shared with this run
    remove_old_images(exceptions=fronts+backs+[generic_back])

    # Load in cards from CUSTOM_IMAGE_PATH
    extra_fronts, extra_backs = add_extra_images(fronts)

    fronts = fronts + extra_fronts
    backs = backs + extra_backs

    # Asynchronously load card images - downloading if necessary. 
    card_images = get_images.get_card_images(fronts + backs + [generic_back])

    # Add image to the Card objects
    assign_images_to_cards(fronts + backs + [generic_back], card_images)

    # Transform fronts and backs into single card objects
    if args.use_generic_card_backs:
        cards = combine_front_and_backs(fronts, backs, generic_back=generic_back)
    else:
        cards = combine_front_and_backs(fronts, backs, generic_back=None)

    #Place all cards with backs first, minimising the number of 2-sided pages.
    return sorted(cards, key=lambda x: x.back is not None, reverse=True)
