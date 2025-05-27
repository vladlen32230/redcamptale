import random
from src.schemas.states.other import CharacterLocation
from src.schemas.states.locations import Location
from src.schemas.states.characters import Character, CharacterSprite
from src.schemas.states.times import Time
from src.schemas.states.entities.ulyana import UlyanaClothes, UlyanaFacialExpression, UlyanaPose
from src.schemas.states.entities.alice import AliceClothes, AliceFacialExpression, AlicePose
from src.schemas.database import Environment, GameState, MapState, Message
from src.schemas.api.game_state import GameStateInterface
from src.schemas.states.music import music_urls
from src.schemas.api.game_state import CharacterSpriteURLS, MessageGameState
from src.auxiliary.config import static_url_root
from src.schemas.api.game_state import CharacterMapLocation
from src.schemas.states.entities.base import Clothes, FacialExpression, Pose
from src.schemas.states.entities.miku import MikuFacialExpression, MikuPose, MikuClothes
from src.schemas.states.entities.slavya import SlavyaClothes, SlavyaFacialExpression, SlavyaPose
from src.schemas.states.entities.lena import LenaClothes, LenaFacialExpression, LenaPose

next_time_dictionary: dict[Time, Time] = {
    Time.DAY: Time.SUNSET,
    Time.SUNSET: Time.NIGHT,
    Time.NIGHT: Time.DAY
}

character_time_clothe: dict[Time, dict[Character, Clothes]] = {
    Time.DAY: {
        Character.ULYANA: UlyanaClothes.ULYANA_UNIFORM,
        Character.ALICE: AliceClothes.ALICE_UNIFORM,
        Character.MIKU: MikuClothes.MIKU_UNIFORM,
        Character.SLAVYA: SlavyaClothes.SLAVYA_UNIFORM,
        Character.LENA: LenaClothes.LENA_UNIFORM
    },
    Time.SUNSET: {
        Character.ULYANA: UlyanaClothes.ULYANA_SPORT,
        Character.ALICE: AliceClothes.ALICE_CLEAVAGE,
        Character.MIKU: MikuClothes.MIKU_UNIFORM,
        Character.SLAVYA: SlavyaClothes.SLAVYA_UNIFORM,
        Character.LENA: LenaClothes.LENA_SPORT
    },
    Time.NIGHT: {
        Character.ULYANA: UlyanaClothes.ULYANA_SPORT,
        Character.ALICE: AliceClothes.ALICE_CLEAVAGE,
        Character.MIKU: MikuClothes.MIKU_UNIFORM,
        Character.SLAVYA: SlavyaClothes.SLAVYA_SPORT,
        Character.LENA: LenaClothes.LENA_SPORT
    }
}

character_random_location: dict[Character, list[Location]] = {
    Character.ALICE: [Location.ULYANA_ALICE_HOME, Location.BEACH, Location.DINING_HALL, Location.FIELD, Location.SQUARE, Location.STAGE, Location.FOREST, Location.BOATHOUSE, Location.ISLAND],
    Character.ULYANA: [Location.ULYANA_ALICE_HOME, Location.BEACH, Location.DINING_HALL, Location.FIELD, Location.SQUARE, Location.FOREST, Location.STAGE, Location.ISLAND, Location.BOATHOUSE],
    Character.LENA: [Location.STAGE, Location.AIDPOST, Location.BEACH, Location.BOATHOUSE, Location.DINING_HALL, Location.FIELD, Location.FOREST, Location.LIBRARY, Location.OUTSIDE, Location.SQUARE, Location.LENA_MIKU_HOME, Location.ISLAND],
    Character.MIKU: [Location.LENA_MIKU_HOME, Location.BEACH, Location.BOATHOUSE, Location.DINING_HALL, Location.SQUARE, Location.FIELD, Location.STAGE],
    Character.SLAVYA: [Location.AIDPOST, Location.BEACH, Location.BOATHOUSE, Location.ISLAND, Location.DINING_HALL, Location.LIBRARY, Location.SQUARE, Location.STAGE, Location.WAREHOUSE, Location.FIELD]
}

def generate_character_locations(time: Time) -> list[dict]:
    if time == Time.NIGHT:
        return [
            CharacterLocation(
                location=Location.ULYANA_ALICE_HOME,
                character=Character.ALICE,
                clothes=character_time_clothe[time][Character.ALICE]
            ).model_dump(),
            CharacterLocation(
                location=Location.ULYANA_ALICE_HOME,
                character=Character.ULYANA,
                clothes=character_time_clothe[time][Character.ULYANA]
            ).model_dump(),
            CharacterLocation(
                location=Location.LENA_MIKU_HOME,
                character=Character.LENA,
                clothes=character_time_clothe[time][Character.LENA]
            ).model_dump(),
            CharacterLocation(
                location=Location.LENA_MIKU_HOME,
                character=Character.MIKU,
                clothes=character_time_clothe[time][Character.MIKU]
            ).model_dump(),
            CharacterLocation(
                location=Location.MAIN_CHARACTER_HOME,
                character=Character.SLAVYA,
                clothes=character_time_clothe[time][Character.SLAVYA]
            ).model_dump()
        ]

    locations = []
    for character in Character:
        if character == Character.MAIN_CHARACTER:
            continue

        locations.append(
            CharacterLocation(
                location=random.choice(character_random_location[character]),
                character=character,
                clothes=character_time_clothe[time][character]
            ).model_dump()
        )

    return locations

time_location_to_url: dict[Time, dict[Location, str]] = {
    Time.DAY: {
        Location.MAIN_CHARACTER_HOME: "locations/day/int_house_of_mt_day.jpg",
        Location.BEACH: "locations/day/ext_beach_day.jpg",
        Location.FIELD: "locations/day/ext_playground_day.jpg",
        Location.FOREST: "locations/day/ext_polyana_day.jpg",
        Location.ULYANA_ALICE_HOME: "locations/day/int_house_of_dv_day.jpg",
        Location.BOATHOUSE: "locations/day/ext_boathouse_day.jpg",
        Location.ISLAND: "locations/day/ext_island_day.jpg",
        Location.SQUARE: "locations/day/ext_square_day.jpg",
        Location.STAGE: "locations/day/ext_stage_normal_day.jpg",
        Location.AIDPOST: "locations/day/int_aidpost_day.jpg",
        Location.UNDERGROUND_BUNKER: "locations/day/int_catacombs_living.jpg",
        Location.DINING_HALL: "locations/day/int_dining_hall_day.jpg",
        Location.LENA_MIKU_HOME: "locations/day/int_house_of_un_day.jpg",
        Location.LIBRARY: "locations/day/int_library_day.jpg",
        Location.WAREHOUSE: "locations/day/int_clubs_male_day.jpg",
        Location.OUTSIDE: "locations/day/ext_road_day.jpg"
    },
    Time.SUNSET: {
        Location.MAIN_CHARACTER_HOME: "locations/sunset/int_house_of_mt_sunset.jpg",
        Location.BEACH: "locations/sunset/ext_beach_sunset.jpg",
        Location.FIELD: "locations/sunset/ext_playground_day.jpg",
        Location.FOREST: "locations/sunset/ext_polyana_sunset.jpg",
        Location.ULYANA_ALICE_HOME: "locations/sunset/int_house_of_dv_day.jpg",
        Location.BOATHOUSE: "locations/sunset/ext_boathouse_day.jpg",
        Location.ISLAND: "locations/sunset/ext_island_day.jpg",
        Location.SQUARE: "locations/sunset/ext_square_sunset.jpg",
        Location.STAGE: "locations/sunset/ext_stage_normal_day.jpg",
        Location.AIDPOST: "locations/sunset/int_aidpost_day.jpg",
        Location.UNDERGROUND_BUNKER: "locations/sunset/int_catacombs_living.jpg",
        Location.DINING_HALL: "locations/sunset/int_dining_hall_sunset.jpg",
        Location.LENA_MIKU_HOME: "locations/sunset/int_house_of_un_day.jpg",
        Location.LIBRARY: "locations/sunset/int_library_day.jpg",
        Location.WAREHOUSE: "locations/sunset/int_clubs_male_sunset.jpg",
        Location.OUTSIDE: "locations/sunset/ext_road_sunset.jpg"
    },
    Time.NIGHT: {
        Location.MAIN_CHARACTER_HOME: "locations/night/int_house_of_mt_noitem_night.jpg",
        Location.BEACH: "locations/night/ext_beach_night.jpg",
        Location.FIELD: "locations/night/ext_playground_night.jpg",
        Location.FOREST: "locations/night/ext_polyana_night.jpg",
        Location.ULYANA_ALICE_HOME: "locations/night/int_house_of_dv_night.jpg",
        Location.BOATHOUSE: "locations/night/ext_boathouse_night.jpg",
        Location.ISLAND: "locations/night/ext_island_night.jpg",
        Location.SQUARE: "locations/night/ext_square_night.jpg",
        Location.STAGE: "locations/night/ext_stage_normal_night.jpg",
        Location.AIDPOST: "locations/night/int_aidpost_night.jpg",
        Location.UNDERGROUND_BUNKER: "locations/night/int_catacombs_living.jpg",
        Location.DINING_HALL: "locations/night/int_dining_hall_night.jpg",
        Location.LENA_MIKU_HOME: "locations/night/int_house_of_un_night.jpg",
        Location.LIBRARY: "locations/night/int_library_night.jpg",
        Location.WAREHOUSE: "locations/night/int_clubs_male2_night_nolight.jpg",
        Location.OUTSIDE: "locations/night/ext_road_night2.jpg"
    }
}

pose_to_url: dict[Pose, str] = {
    UlyanaPose.ULYANA_NORMAL: "characters/ulyana/poses/us_1_body.png",
    UlyanaPose.ULYANA_CONFUSED: "characters/ulyana/poses/us_3_body.png",
    UlyanaPose.ULYANA_ANGRY: "characters/ulyana/poses/us_2_body.png",

    AlicePose.ALICE_NORMAL: "characters/alice/poses/dv_4_body.png",
    AlicePose.ALICE_CONSTRAINED: "characters/alice/poses/dv_3_body.png",
    AlicePose.ALICE_ANGRY: "characters/alice/poses/dv_5_body.png",
    AlicePose.ALICE_CONFUSED: "characters/alice/poses/dv_1_body.png",
    AlicePose.ALICE_GRIN: "characters/alice/poses/dv_2_body.png",

    MikuPose.MIKU_NORMAL: "characters/miku/poses/mi_1_body.png",
    MikuPose.MIKU_LOVELY: "characters/miku/poses/mi_2_body.png",
    MikuPose.MIKU_SERIOUS: "characters/miku/poses/mi_3_body.png",

    SlavyaPose.SLAVYA_NORMAL: "characters/slavya/poses/sl_1_body.png",
    SlavyaPose.SLAVYA_HAPPY: "characters/slavya/poses/sl_2_body.png",
    SlavyaPose.SLAVYA_CONFUSED: "characters/slavya/poses/sl_3_body.png",
    SlavyaPose.SLAVYA_SCARED: "characters/slavya/poses/sl_4_body.png",

    LenaPose.LENA_NORMAL: "characters/lena/poses/un_1_body.png",
    LenaPose.LENA_SAD: "characters/lena/poses/un_2_body.png",
    LenaPose.LENA_SERIOUS: "characters/lena/poses/un_3_body.png"
}

facial_expression_to_url: dict[Pose, dict[FacialExpression, str]] = {
    UlyanaPose.ULYANA_NORMAL: {
        UlyanaFacialExpression.ULYANA_NORMAL: "characters/ulyana/faces/us_1_normal.png",
        UlyanaFacialExpression.ULYANA_GRIN: "characters/ulyana/faces/us_1_grin.png",
        UlyanaFacialExpression.ULYANA_LAUGH: "characters/ulyana/faces/us_1_laugh.png",
        UlyanaFacialExpression.ULYANA_LAUGH2: "characters/ulyana/faces/us_1_laugh2.png",
        UlyanaFacialExpression.ULYANA_SAD: "characters/ulyana/faces/us_1_sad.png",
        UlyanaFacialExpression.ULYANA_SMILE: "characters/ulyana/faces/us_1_smile.png"
    },
    UlyanaPose.ULYANA_CONFUSED: {
        UlyanaFacialExpression.ULYANA_CRY: "characters/ulyana/faces/us_3_cry.png",
        UlyanaFacialExpression.ULYANA_SHY: "characters/ulyana/faces/us_3_shy.png",
        UlyanaFacialExpression.ULYANA_SURPRISE: "characters/ulyana/faces/us_3_surp1.png",
        UlyanaFacialExpression.ULYANA_SURPRISE2: "characters/ulyana/faces/us_3_surp2.png",
        UlyanaFacialExpression.ULYANA_SURPRISE3: "characters/ulyana/faces/us_3_surp3.png",
        UlyanaFacialExpression.ULYANA_CRY2: "characters/ulyana/faces/us_3_cry2.png",
        UlyanaFacialExpression.ULYANA_SHY2: "characters/ulyana/faces/us_3_shy2.png"
    },
    UlyanaPose.ULYANA_ANGRY: {
        UlyanaFacialExpression.ULYANA_FRUSTRATED: "characters/ulyana/faces/us_2_calml.png",
        UlyanaFacialExpression.ULYANA_FROWNING: "characters/ulyana/faces/us_2_dontlike.png",
        UlyanaFacialExpression.ULYANA_FEAR: "characters/ulyana/faces/us_2_fear.png",
        UlyanaFacialExpression.ULYANA_UPSET: "characters/ulyana/faces/us_2_upset.png"
    },

    AlicePose.ALICE_NORMAL: {
        AliceFacialExpression.ALICE_NORMAL: "characters/alice/faces/dv_4_normal.png",
        AliceFacialExpression.ALICE_LAUGH: "characters/alice/faces/dv_4_laugh.png",
        AliceFacialExpression.ALICE_SMILE: "characters/alice/faces/dv_4_smile.png"
    },
    AlicePose.ALICE_CONSTRAINED: {
        AliceFacialExpression.ALICE_SAD: "characters/alice/faces/dv_3_sad.png",
        AliceFacialExpression.ALICE_SHY: "characters/alice/faces/dv_3_shy.png",
        AliceFacialExpression.ALICE_GUILTY: "characters/alice/faces/dv_3_guilty.png"
    },
    AlicePose.ALICE_ANGRY: {
        AliceFacialExpression.ALICE_ANGRY: "characters/alice/faces/dv_5_angry.png",
        AliceFacialExpression.ALICE_RAGE: "characters/alice/faces/dv_5_rage.png"
    },
    AlicePose.ALICE_CONFUSED: {
        AliceFacialExpression.ALICE_CRY: "characters/alice/faces/dv_1_cry.png",
        AliceFacialExpression.ALICE_SCARED: "characters/alice/faces/dv_1_scared.png",
        AliceFacialExpression.ALICE_SHOCKED: "characters/alice/faces/dv_1_shocked.png",
        AliceFacialExpression.ALICE_SURPRISED: "characters/alice/faces/dv_1_surprise.png"
    },
    AlicePose.ALICE_GRIN: {
        AliceFacialExpression.ALICE_GRIN: "characters/alice/faces/dv_2_grin.png",
    },

    MikuPose.MIKU_NORMAL: {
        MikuFacialExpression.MIKU_CRY: "characters/miku/faces/mi_1_cry.png",
        MikuFacialExpression.MIKU_FROWNING: "characters/miku/faces/mi_1_dontlike.png",
        MikuFacialExpression.MIKU_LAUGH: "characters/miku/faces/mi_1_laugh.png",
        MikuFacialExpression.MIKU_SCARED: "characters/miku/faces/mi_1_scared.png",
        MikuFacialExpression.MIKU_SHOCKED: "characters/miku/faces/mi_1_shocked.png",
        MikuFacialExpression.MIKU_SHY: "characters/miku/faces/mi_1_shy.png",
        MikuFacialExpression.MIKU_SURPRISED: "characters/miku/faces/mi_1_surprise.png"
    },
    MikuPose.MIKU_LOVELY: {
        MikuFacialExpression.MIKU_CRY_SMILE: "characters/miku/faces/mi_2_cry_smile.png",
        MikuFacialExpression.MIKU_GRIN: "characters/miku/faces/mi_2_grin.png",
        MikuFacialExpression.MIKU_HAPPY: "characters/miku/faces/mi_2_happy.png",
        MikuFacialExpression.MIKU_SAD: "characters/miku/faces/mi_2_sad.png",
        MikuFacialExpression.MIKU_SMILE: "characters/miku/faces/mi_2_smile.png"
    },
    MikuPose.MIKU_SERIOUS: {
        MikuFacialExpression.MIKU_ANGRY: "characters/miku/faces/mi_3_angry.png",
        MikuFacialExpression.MIKU_NORMAL: "characters/miku/faces/mi_3_normal.png",
        MikuFacialExpression.MIKU_RAGE: "characters/miku/faces/mi_3_rage.png",
        MikuFacialExpression.MIKU_SERIOUS: "characters/miku/faces/mi_3_serious.png",
        MikuFacialExpression.MIKU_UPSET: "characters/miku/faces/mi_3_upset.png"
    },

    SlavyaPose.SLAVYA_NORMAL: {
        SlavyaFacialExpression.SLAVYA_NORMAL: "characters/slavya/faces/sl_1_normal.png",
        SlavyaFacialExpression.SLAVYA_SERIOUS: "characters/slavya/faces/sl_1_serious.png",
        SlavyaFacialExpression.SLAVYA_SMILE: "characters/slavya/faces/sl_1_smile.png"
    },
    SlavyaPose.SLAVYA_HAPPY: {
        SlavyaFacialExpression.SLAVYA_HAPPY: "characters/slavya/faces/sl_2_happy.png",
        SlavyaFacialExpression.SLAVYA_LAUGHING: "characters/slavya/faces/sl_2_laugh.png",
        SlavyaFacialExpression.SLAVYA_SHY: "characters/slavya/faces/sl_2_shy.png",
        SlavyaFacialExpression.SLAVYA_SMILE2: "characters/slavya/faces/sl_2_smile2.png"
    },
    SlavyaPose.SLAVYA_CONFUSED: {
        SlavyaFacialExpression.SLAVYA_ANGRY: "characters/slavya/faces/sl_3_angry.png",
        SlavyaFacialExpression.SLAVYA_SAD: "characters/slavya/faces/sl_3_sad.png",
        SlavyaFacialExpression.SLAVYA_SURPRISE: "characters/slavya/faces/sl_3_surprise.png"
    },
    SlavyaPose.SLAVYA_SCARED: {
        SlavyaFacialExpression.SLAVYA_SCARED: "characters/slavya/faces/sl_4_scared.png",
        SlavyaFacialExpression.SLAVYA_TENDER: "characters/slavya/faces/sl_4_tender.png"
    },

    LenaPose.LENA_NORMAL: {
        LenaFacialExpression.LENA_NORMAL: "characters/lena/faces/un_1_normal.png",
        LenaFacialExpression.LENA_ANGRY: "characters/lena/faces/un_1_angry.png",
        LenaFacialExpression.LENA_EVIL_SMILE: "characters/lena/faces/un_1_evil_smile.png",
        LenaFacialExpression.LENA_SHY: "characters/lena/faces/un_1_shy.png",
        LenaFacialExpression.LENA_SMILE: "characters/lena/faces/un_1_smile.png",
        LenaFacialExpression.LENA_SMILE2: "characters/lena/faces/un_1_smile2.png"
    },
    LenaPose.LENA_SAD: {
        LenaFacialExpression.LENA_CRY: "characters/lena/faces/un_2_cry.png",
        LenaFacialExpression.LENA_CRY_SMILE: "characters/lena/faces/un_2_cry_smile.png",
        LenaFacialExpression.LENA_SAD: "characters/lena/faces/un_2_sad.png",
        LenaFacialExpression.LENA_SCARED: "characters/lena/faces/un_2_scared.png",
        LenaFacialExpression.LENA_SHOCKED: "characters/lena/faces/un_2_shocked.png",
        LenaFacialExpression.LENA_SURPRISED: "characters/lena/faces/un_2_surprise.png"
    },
    LenaPose.LENA_SERIOUS: {
        LenaFacialExpression.LENA_ANGRY2: "characters/lena/faces/un_3_angry2.png",
        LenaFacialExpression.LENA_GRIN: "characters/lena/faces/un_3_grin.png",
        LenaFacialExpression.LENA_LAUGH: "characters/lena/faces/un_3_laugh.png",
        LenaFacialExpression.LENA_RAGE: "characters/lena/faces/un_3_rage.png",
        LenaFacialExpression.LENA_SERIOUS: "characters/lena/faces/un_3_serious.png",
        LenaFacialExpression.LENA_SMILE3: "characters/lena/faces/un_3_smile3.png"
    }
}

pose_clothes_to_url: dict[Pose, dict[Clothes, str]] = {
    UlyanaPose.ULYANA_NORMAL: {
        UlyanaClothes.ULYANA_UNIFORM: "characters/ulyana/clothes/us_1_pioneer.png",
        UlyanaClothes.ULYANA_SPORT: "characters/ulyana/clothes/us_1_sport.png"
    },
    UlyanaPose.ULYANA_CONFUSED: {
        UlyanaClothes.ULYANA_UNIFORM: "characters/ulyana/clothes/us_3_pioneer.png",
        UlyanaClothes.ULYANA_SPORT: "characters/ulyana/clothes/us_3_sport.png"
    },
    UlyanaPose.ULYANA_ANGRY: {
        UlyanaClothes.ULYANA_UNIFORM: "characters/ulyana/clothes/us_2_pioneer.png",
        UlyanaClothes.ULYANA_SPORT: "characters/ulyana/clothes/us_2_sport.png"
    },

    AlicePose.ALICE_NORMAL: {
        AliceClothes.ALICE_UNIFORM: "characters/alice/clothes/dv_4_pioneer.png",
        AliceClothes.ALICE_CLEAVAGE: "characters/alice/clothes/dv_4_pioneer2.png"
    },
    AlicePose.ALICE_CONSTRAINED: {
        AliceClothes.ALICE_UNIFORM: "characters/alice/clothes/dv_3_pioneer.png",
        AliceClothes.ALICE_CLEAVAGE: "characters/alice/clothes/dv_3_pioneer2.png"
    },
    AlicePose.ALICE_ANGRY: {
        AliceClothes.ALICE_UNIFORM: "characters/alice/clothes/dv_5_pioneer.png",
        AliceClothes.ALICE_CLEAVAGE: "characters/alice/clothes/dv_5_pioneer2.png"
    },
    AlicePose.ALICE_CONFUSED: {
        AliceClothes.ALICE_UNIFORM: "characters/alice/clothes/dv_1_pioneer.png",
        AliceClothes.ALICE_CLEAVAGE: "characters/alice/clothes/dv_1_pioneer2.png"
    },
    AlicePose.ALICE_GRIN: {
        AliceClothes.ALICE_UNIFORM: "characters/alice/clothes/dv_2_pioneer.png",
        AliceClothes.ALICE_CLEAVAGE: "characters/alice/clothes/dv_2_pioneer2.png"
    },

    MikuPose.MIKU_NORMAL: {
        MikuClothes.MIKU_UNIFORM: "characters/miku/clothes/mi_1_pioneer.png"
    },
    MikuPose.MIKU_LOVELY: {
        MikuClothes.MIKU_UNIFORM: "characters/miku/clothes/mi_2_pioneer.png"
    },
    MikuPose.MIKU_SERIOUS: {
        MikuClothes.MIKU_UNIFORM: "characters/miku/clothes/mi_3_pioneer.png"
    },

    SlavyaPose.SLAVYA_NORMAL: {
        SlavyaClothes.SLAVYA_UNIFORM: "characters/slavya/clothes/sl_1_pioneer.png",
        SlavyaClothes.SLAVYA_SPORT: "characters/slavya/clothes/sl_1_sport.png"
    },
    SlavyaPose.SLAVYA_HAPPY: {
        SlavyaClothes.SLAVYA_UNIFORM: "characters/slavya/clothes/sl_2_pioneer.png",
        SlavyaClothes.SLAVYA_SPORT: "characters/slavya/clothes/sl_2_sport.png"
    },
    SlavyaPose.SLAVYA_CONFUSED: {
        SlavyaClothes.SLAVYA_UNIFORM: "characters/slavya/clothes/sl_3_pioneer.png",
        SlavyaClothes.SLAVYA_SPORT: "characters/slavya/clothes/sl_3_sport.png"
    },
    SlavyaPose.SLAVYA_SCARED: {
        SlavyaClothes.SLAVYA_UNIFORM: "characters/slavya/clothes/sl_4_pioneer.png",
        SlavyaClothes.SLAVYA_SPORT: "characters/slavya/clothes/sl_4_sport.png"
    },

    LenaPose.LENA_NORMAL: {
        LenaClothes.LENA_UNIFORM: "characters/lena/clothes/un_1_pioneer.png",
        LenaClothes.LENA_SPORT: "characters/lena/clothes/un_1_sport.png"
    },
    LenaPose.LENA_SAD: {
        LenaClothes.LENA_UNIFORM: "characters/lena/clothes/un_2_pioneer.png",
        LenaClothes.LENA_SPORT: "characters/lena/clothes/un_2_sport.png"
    },
    LenaPose.LENA_SERIOUS: {
        LenaClothes.LENA_UNIFORM: "characters/lena/clothes/un_3_pioneer.png",
        LenaClothes.LENA_SPORT: "characters/lena/clothes/un_3_sport.png"
    }
}

character_to_head_url: dict[Character, str] = {
    Character.ULYANA: "heads/ulyana_head.png",
    Character.ALICE: "heads/alice_head.png",
    Character.MIKU: "heads/miku_head.png",
    Character.SLAVYA: "heads/slavya_head.png",
    Character.LENA: "heads/lena_head.png",
    Character.MAIN_CHARACTER: "heads/main_character_head.png"
}

valid_character_expressions: dict[Pose, tuple[FacialExpression]] = {
    UlyanaPose.ULYANA_NORMAL: (UlyanaFacialExpression.ULYANA_NORMAL, UlyanaFacialExpression.ULYANA_GRIN, UlyanaFacialExpression.ULYANA_LAUGH, UlyanaFacialExpression.ULYANA_SAD, UlyanaFacialExpression.ULYANA_SMILE, UlyanaFacialExpression.ULYANA_LAUGH2),
    UlyanaPose.ULYANA_CONFUSED: (UlyanaFacialExpression.ULYANA_SURPRISE2, UlyanaFacialExpression.ULYANA_SHY2, UlyanaFacialExpression.ULYANA_CRY, UlyanaFacialExpression.ULYANA_SHY, UlyanaFacialExpression.ULYANA_SURPRISE, UlyanaFacialExpression.ULYANA_SURPRISE3, UlyanaFacialExpression.ULYANA_CRY2),
    UlyanaPose.ULYANA_ANGRY: (UlyanaFacialExpression.ULYANA_FRUSTRATED, UlyanaFacialExpression.ULYANA_FROWNING, UlyanaFacialExpression.ULYANA_FEAR, UlyanaFacialExpression.ULYANA_UPSET),

    AlicePose.ALICE_NORMAL: (AliceFacialExpression.ALICE_NORMAL, AliceFacialExpression.ALICE_LAUGH),
    AlicePose.ALICE_CONSTRAINED: (AliceFacialExpression.ALICE_SAD, AliceFacialExpression.ALICE_SHY, AliceFacialExpression.ALICE_GUILTY, AliceFacialExpression.ALICE_SMILE),
    AlicePose.ALICE_ANGRY: (AliceFacialExpression.ALICE_ANGRY, AliceFacialExpression.ALICE_RAGE),
    AlicePose.ALICE_CONFUSED: (AliceFacialExpression.ALICE_CRY, AliceFacialExpression.ALICE_SCARED, AliceFacialExpression.ALICE_SHOCKED, AliceFacialExpression.ALICE_SURPRISED),
    AlicePose.ALICE_GRIN: (AliceFacialExpression.ALICE_GRIN,),

    MikuPose.MIKU_NORMAL: (MikuFacialExpression.MIKU_NORMAL, MikuFacialExpression.MIKU_CRY, MikuFacialExpression.MIKU_FROWNING, MikuFacialExpression.MIKU_LAUGH, MikuFacialExpression.MIKU_SCARED, MikuFacialExpression.MIKU_SHOCKED, MikuFacialExpression.MIKU_SHY, MikuFacialExpression.MIKU_SURPRISED),
    MikuPose.MIKU_LOVELY: (MikuFacialExpression.MIKU_CRY_SMILE, MikuFacialExpression.MIKU_GRIN, MikuFacialExpression.MIKU_HAPPY, MikuFacialExpression.MIKU_SAD, MikuFacialExpression.MIKU_SMILE),
    MikuPose.MIKU_SERIOUS: (MikuFacialExpression.MIKU_ANGRY, MikuFacialExpression.MIKU_NORMAL, MikuFacialExpression.MIKU_RAGE, MikuFacialExpression.MIKU_SERIOUS, MikuFacialExpression.MIKU_UPSET),

    SlavyaPose.SLAVYA_NORMAL: (SlavyaFacialExpression.SLAVYA_NORMAL, SlavyaFacialExpression.SLAVYA_SERIOUS, SlavyaFacialExpression.SLAVYA_SMILE),
    SlavyaPose.SLAVYA_HAPPY: (SlavyaFacialExpression.SLAVYA_HAPPY, SlavyaFacialExpression.SLAVYA_LAUGHING, SlavyaFacialExpression.SLAVYA_SHY, SlavyaFacialExpression.SLAVYA_SMILE2),
    SlavyaPose.SLAVYA_CONFUSED: (SlavyaFacialExpression.SLAVYA_ANGRY, SlavyaFacialExpression.SLAVYA_SAD, SlavyaFacialExpression.SLAVYA_SURPRISE),
    SlavyaPose.SLAVYA_SCARED: (SlavyaFacialExpression.SLAVYA_SCARED, SlavyaFacialExpression.SLAVYA_TENDER),

    LenaPose.LENA_NORMAL: (LenaFacialExpression.LENA_NORMAL, LenaFacialExpression.LENA_ANGRY, LenaFacialExpression.LENA_EVIL_SMILE, LenaFacialExpression.LENA_SHY, LenaFacialExpression.LENA_SMILE, LenaFacialExpression.LENA_SMILE2),
    LenaPose.LENA_SAD: (LenaFacialExpression.LENA_CRY, LenaFacialExpression.LENA_CRY_SMILE, LenaFacialExpression.LENA_SAD, LenaFacialExpression.LENA_SCARED, LenaFacialExpression.LENA_SHOCKED, LenaFacialExpression.LENA_SURPRISED),
    LenaPose.LENA_SERIOUS: (LenaFacialExpression.LENA_ANGRY2, LenaFacialExpression.LENA_GRIN, LenaFacialExpression.LENA_LAUGH, LenaFacialExpression.LENA_RAGE, LenaFacialExpression.LENA_SERIOUS, LenaFacialExpression.LENA_SMILE3)
}

valid_character_poses: dict[Character, tuple[Pose]] = {
    Character.ULYANA: (UlyanaPose.ULYANA_NORMAL, UlyanaPose.ULYANA_CONFUSED, UlyanaPose.ULYANA_ANGRY),
    Character.ALICE: (AlicePose.ALICE_NORMAL, AlicePose.ALICE_CONSTRAINED, AlicePose.ALICE_ANGRY, AlicePose.ALICE_CONFUSED, AlicePose.ALICE_GRIN),
    Character.MIKU: (MikuPose.MIKU_NORMAL, MikuPose.MIKU_LOVELY, MikuPose.MIKU_SERIOUS),
    Character.SLAVYA: (SlavyaPose.SLAVYA_NORMAL, SlavyaPose.SLAVYA_HAPPY, SlavyaPose.SLAVYA_CONFUSED, SlavyaPose.SLAVYA_SCARED),
    Character.LENA: (LenaPose.LENA_NORMAL, LenaPose.LENA_SAD, LenaPose.LENA_SERIOUS)
}

default_character_view: dict[Clothes, tuple[Pose, FacialExpression]] = {
    UlyanaClothes.ULYANA_SPORT: (UlyanaPose.ULYANA_NORMAL, UlyanaFacialExpression.ULYANA_NORMAL),
    UlyanaClothes.ULYANA_UNIFORM: (UlyanaPose.ULYANA_NORMAL, UlyanaFacialExpression.ULYANA_NORMAL),

    AliceClothes.ALICE_CLEAVAGE: (AlicePose.ALICE_NORMAL, AliceFacialExpression.ALICE_NORMAL),
    AliceClothes.ALICE_UNIFORM: (AlicePose.ALICE_NORMAL, AliceFacialExpression.ALICE_NORMAL),

    MikuClothes.MIKU_UNIFORM: (MikuPose.MIKU_SERIOUS, MikuFacialExpression.MIKU_NORMAL),

    SlavyaClothes.SLAVYA_SPORT: (SlavyaPose.SLAVYA_NORMAL, SlavyaFacialExpression.SLAVYA_NORMAL),
    SlavyaClothes.SLAVYA_UNIFORM: (SlavyaPose.SLAVYA_NORMAL, SlavyaFacialExpression.SLAVYA_NORMAL),

    LenaClothes.LENA_SPORT: (LenaPose.LENA_NORMAL, LenaFacialExpression.LENA_NORMAL),
    LenaClothes.LENA_UNIFORM: (LenaPose.LENA_NORMAL, LenaFacialExpression.LENA_NORMAL),
}

def parse_game_to_interface(
    environment: Environment, 
    game_state: GameState,
    map_state: MapState,
    message: Message | None = None
) -> GameStateInterface:
    music_urls_api = music_urls[game_state.music]
    music_urls_api = [static_url_root + music_url for music_url in music_urls_api]

    background_url = static_url_root + time_location_to_url.get(map_state.time, None).get(environment.location, None)
    
    character_sprites = []

    for character in game_state.characters:
        pose = static_url_root + pose_to_url.get(character['pose'], None)
        clothes = static_url_root + pose_clothes_to_url.get(character['pose'], None).get(character['clothes'], None)
        facial_expression = static_url_root + facial_expression_to_url.get(character['pose'], None).get(character['facial_expression'], None)

        character_sprites.append(CharacterSpriteURLS(
            pose_url=pose,
            clothes_url=clothes,
            facial_expression_url=facial_expression
        ))

    interface = GameStateInterface(
        id=game_state.id,
        characters=character_sprites,
        background_url=background_url,
        message=MessageGameState(
            message=message,
            game_state_id=game_state.id
        ).model_dump() if message else None,
        followers_head_urls=[
            static_url_root + character_to_head_url.get(character, None) for character in game_state.followers
        ],
        time=map_state.time,
        music_urls=music_urls_api,
        music_type=game_state.music
    )

    return interface

def parse_map_state_to_character_locations(map_state: MapState) -> list[CharacterMapLocation]:
    locations = []

    for character_location in map_state.character_location:
        locations.append(
            CharacterMapLocation(
                location=character_location['location'],
                character=character_location['character'],
                character_head_url=static_url_root + character_to_head_url.get(character_location['character'], None)
            )
        )

    return locations


def get_character_sprites_by_location(
    location: Location, 
    character_locations: list[dict]
) -> list[CharacterSprite]:
    character_sprites = []

    for character_location in character_locations:
        if character_location['location'] == location:
            pose, face = default_character_view[character_location['clothes']]
            character = character_location['character']
            character_sprites.append(
                CharacterSprite(
                    character=character,
                    pose=pose,
                    facial_expression=face,
                    clothes=character_location['clothes']
                ).model_dump()
            )

    return character_sprites
