from enum import Enum

class Location(str, Enum):
    ULYANA_ALICE_HOME = "ulyana_alice_home"
    MAIN_CHARACTER_HOME = "main_character_home"
    BEACH = "beach"
    FOREST = "forest"
    FIELD = "field"
    BOATHOUSE = "boathouse"
    ISLAND = "island"
    SQUARE = "square"
    STAGE = "stage"
    AIDPOST = "aidpost"
    UNDERGROUND_BUNKER = "underground_bunker"
    DINING_HALL = "dining_hall"
    LENA_MIKU_HOME = "lena_miku_home"
    LIBRARY = "library"
    WAREHOUSE = "warehouse"
    OUTSIDE = "outside"

    @classmethod
    def get_description(cls, location: 'Location') -> str:
        descriptions = {
            cls.ULYANA_ALICE_HOME: "Small room of Ulyana and Alice.",
            cls.MAIN_CHARACTER_HOME: "The protagonist's room. It is clean and tidy. There also lives Slavya.",
            cls.BEACH: "A serene beach with golden sands and gentle waves.",
            cls.FOREST: "A dense forest with tall trees and undergrowth. It is quiet here.",
            cls.FIELD: "A big park with football field, tennis court and sport's playground.",
            cls.BOATHOUSE: "A boathouse on the lake. There is a small island nearby.",
            cls.ISLAND: "An small island nearby boathouse. It is quiet here.",
            cls.SQUARE: "A big square for gatherings.",
            cls.STAGE: "A big stage for musical performances.",
            cls.AIDPOST: "An clean aidpost with medicine. ",
            cls.UNDERGROUND_BUNKER: "A small underground bunker used for sheltering from nuclear attack. There is quite cozy depsite being abandoned. There is beds and some survival equipment.",
            cls.DINING_HALL: "A big dining hall with tables and chairs. There is a kitchen in the back.",
            cls.LENA_MIKU_HOME: "A small room of Lena and Miku.",
            cls.LIBRARY: "A big library with bookshelves and a table.",
            cls.WAREHOUSE: "A warehouse with stuff.",
            cls.OUTSIDE: "Outside the camp. There is a long road leading to the city."
        }

        return descriptions.get(location, "Unknown")