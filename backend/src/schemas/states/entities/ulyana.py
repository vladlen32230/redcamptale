from enum import Enum

class UlyanaClothes(str, Enum):
    ULYANA_UNIFORM = "ulyana_uniform"
    ULYANA_SPORT = "ulyana_sport"

    @classmethod
    def get_clothes_description(cls, clothes: 'UlyanaClothes') -> str:
        return {
            cls.ULYANA_UNIFORM: "Soviet pioneer uniform with white shirt and blue skirt.",
            cls.ULYANA_SPORT: "Sportswear with red shirt and green shorts. Shirt has a label 'USSR' on the chest."
        }.get(clothes, "Unknown")

class UlyanaFacialExpression(str, Enum):
    ULYANA_GRIN = "ulyana_grin"
    ULYANA_LAUGH = "ulyana_laugh"
    ULYANA_LAUGH2 = "ulyana_laugh2"
    ULYANA_NORMAL = "ulyana_normal"
    ULYANA_SAD = "ulyana_sad"
    ULYANA_SMILE = "ulyana_smile"

    ULYANA_FRUSTRATED = "ulyana_frustrated"
    ULYANA_FROWNING = "ulyana_frowning"
    ULYANA_FEAR = "ulyana_fear"
    ULYANA_UPSET = "ulyana_upset"

    ULYANA_CRY = "ulyana_cry"
    ULYANA_CRY2 = "ulyana_cry2"
    ULYANA_SHY = "ulyana_shy"
    ULYANA_SHY2 = "ulyana_shy2"
    ULYANA_SURPRISE = "ulyana_surprise"
    ULYANA_SURPRISE2 = "ulyana_surprise2"
    ULYANA_SURPRISE3 = "ulyana_surprise3"

    @classmethod
    def get_facial_expression_description(cls, facial_expression: 'UlyanaFacialExpression') -> str:
        return {
            cls.ULYANA_GRIN: "Grinning and happy.",
            cls.ULYANA_SHY: "Very shy.",
            cls.ULYANA_CRY: "Crying and sad.",
            cls.ULYANA_NORMAL: "Normal and casual.",
            cls.ULYANA_LAUGH: "Laughing and happy.",
            cls.ULYANA_SAD: "Sad.",
            cls.ULYANA_SMILE: "Smiling.",
            cls.ULYANA_SURPRISE: "Surprised and smiling.",
            cls.ULYANA_SURPRISE2: "Very surprised or shocked.",
            cls.ULYANA_SURPRISE3: "Surprised and shy.",
            cls.ULYANA_FRUSTRATED: "Frustrated.",
            cls.ULYANA_FROWNING: "Frowning",
            cls.ULYANA_FEAR: "Fearful",
            cls.ULYANA_UPSET: "Upset.",
            cls.ULYANA_LAUGH2: "Laughing and happy.",
            cls.ULYANA_CRY2: "Hysterical crying.",
            cls.ULYANA_SHY2: "Very shy or embarrassed.",
        }.get(facial_expression, "Unknown")

class UlyanaPose(str, Enum):
    ULYANA_NORMAL = "ulyana_normal"
    ULYANA_ANGRY = "ulyana_angry"
    ULYANA_CONFUSED = "ulyana_confused"

    @classmethod
    def get_pose_description(cls, pose: 'UlyanaPose') -> str:
        return {
            cls.ULYANA_NORMAL: "Casual and happy or a bit sad.",
            cls.ULYANA_ANGRY: "Angry, upset or scared.",
            cls.ULYANA_CONFUSED: "Crying, shy or surprised."
        }.get(pose, "Unknown")
