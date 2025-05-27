from enum import Enum
from src.schemas.states.locations import Location
from src.schemas.states.times import Time
import random

class Music(str, Enum):
    FUNNY = "funny"
    SAD = "sad"
    NORMAL = "normal"
    HAPPY = "happy"
    ROMANTIC = "romantic"
    NONE = "none"
    CONFUSING = "confusing"
    ANGRY = "angry"
    SCARY = "scary"
    SEXY = "sexy"

    @classmethod
    def get_default_music(cls, location: 'Location', time: Time) -> 'Music':
        return Music.NORMAL

    @classmethod
    def get_music_description(cls, music: 'Music') -> str:
        descriptions = {
            cls.FUNNY: "Funny",
            cls.SAD: "Sad and melancholic",
            cls.NORMAL: "Normal",
            cls.HAPPY: "Happy and cheerful",
            cls.ROMANTIC: "Romantic and sweet",
            cls.NONE: "None",
            cls.CONFUSING: "Confusing and mysterious",
            cls.ANGRY: "Angry and aggressive",
            cls.SCARY: "Scary and frightening",
            cls.SEXY: "Sexy and sensual"
        }

        return descriptions.get(music, "Unknown")

    
music_urls: dict[Music, list[str]] = {
    Music.FUNNY: [
        "music/always_ready.ogg", "music/eat_some_trouble.ogg", "music/i_want_to_play.ogg",
        "music/went_fishing_caught_a_girl.ogg"
    ],
    Music.SAD: [
        "music/a_promise_from_distant_days.ogg", "music/i_dont_blame_you.ogg", "music/lets_be_friends.ogg",
        "music/memories.ogg"
    ],
    Music.NORMAL: [
        "music/afterword.ogg", "music/dance_of_fireflies.ogg", "music/confession.ogg", 
        "music/feeling_good.ogg", "music/gentle_predator.ogg", "music/goodbye_home_shores.ogg",
        "music/heather.ogg", "music/my_daily_life.ogg", "music/reflection_on_water.ogg",
        "music/smooth_machine.ogg", "music/sweet_darkness.ogg", "music/trapped_in_dreams.ogg",
        "music/tried_to_bring_it_back.ogg", "music/two_glasses_of_melancholy.ogg",
        "music/your_bright_side.ogg"
    ],
    Music.HAPPY: [
        "music/farewell_to_the_past.ogg", "music/forest_maiden.ogg", "music/get_to_know_me_better.ogg",
        "music/lightness.ogg", "music/so_good_to_be_careless.ogg", "music/take_me_beautifully.ogg",
        "music/timid_girl.ogg"
    ],
    Music.ROMANTIC: [
        "music/mystery_girl.ogg", "music/raindrops.ogg", "music/reminiscences.ogg",
        "music/she_is_kind.ogg", "music/silhouette_in_sunset.ogg", "music/waltz_of_doubts.ogg",
        "music/what_do_you_think_of_me.ogg"
    ],
    Music.CONFUSING: [
        "music/door_to_nightmare.ogg", "music/drown.ogg", "music/into_the_unknown.ogg",
        "music/just_think.ogg", "music/no_tresspassing.ogg", "music/orchid.ogg",
        "music/you_lost_me.ogg"
    ],
    Music.ANGRY: [
        "music/awakening_power.ogg", "music/doomed_to_be_defeated.ogg", "music/pile.ogg",
        "music/revenga.ogg", "music/scarytale.ogg", "music/that_s_our_madhouse.ogg"
    ],
    Music.SCARY: ["music/faceless.ogg", "music/sunny_day.ogg", "music/torture.ogg"],
    Music.SEXY: ["music/eternal_longing.ogg", "music/glimmering_coals.ogg", "music/you_won_t_let_me_down.ogg"],
    Music.NONE: []
}