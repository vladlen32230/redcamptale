from enum import Enum

class SlavyaClothes(str, Enum):
    SLAVYA_UNIFORM = "slavya_uniform"
    SLAVYA_SPORT = "slavya_sport"

    @classmethod
    def get_clothes_description(cls, clothes: 'SlavyaClothes') -> str:
        return {
            cls.SLAVYA_UNIFORM: "Soviet pioneer uniform with white shirt and blue skirt.",
            cls.SLAVYA_SPORT: "Black sportswear with white stripes and shorts.",
        }.get(clothes, "Unknown")


class SlavyaFacialExpression(str, Enum):
    SLAVYA_NORMAL = "slavya_normal"
    SLAVYA_SERIOUS = "slavya_serious"
    SLAVYA_SMILE = "slavya_smile"

    SLAVYA_HAPPY = "slavya_happy"
    SLAVYA_LAUGHING = "slavya_laughing"
    SLAVYA_SHY = "slavya_shy"
    SLAVYA_SMILE2 = "slavya_smile2"

    SLAVYA_ANGRY = "slavya_angry"
    SLAVYA_SAD = "slavya_sad"
    SLAVYA_SURPRISE = "slavya_surprise"

    SLAVYA_SCARED = "slavya_scared"
    SLAVYA_TENDER = "slavya_tender"

    @classmethod
    def get_facial_expression_description(cls, facial_expression: 'SlavyaFacialExpression') -> str:
        return {
            cls.SLAVYA_NORMAL: "Normal and casual.",
            cls.SLAVYA_SERIOUS: "Serious.",
            cls.SLAVYA_SMILE: "Smiling.",
            cls.SLAVYA_HAPPY: "Happy.",
            cls.SLAVYA_LAUGHING: "Laughing.",
            cls.SLAVYA_SHY: "Shy.",
            cls.SLAVYA_SMILE2: "Smiling.",
            cls.SLAVYA_ANGRY: "Angry.",
            cls.SLAVYA_SAD: "Sad.",
            cls.SLAVYA_SURPRISE: "Surprised.",
            cls.SLAVYA_SCARED: "Scared.",
            cls.SLAVYA_TENDER: "Tender.",
        }.get(facial_expression, "Unknown")


class SlavyaPose(str, Enum):
    SLAVYA_NORMAL = "slavya_normal"
    SLAVYA_HAPPY = "slavya_happy"
    SLAVYA_CONFUSED = "slavya_confused"
    SLAVYA_SCARED = "slavya_scared"

    @classmethod
    def get_pose_description(cls, pose: 'SlavyaPose') -> str:
        return {
            cls.SLAVYA_NORMAL: "Normal and casual.",
            cls.SLAVYA_HAPPY: "Happy or a bit angry.",
            cls.SLAVYA_CONFUSED: "Confused.",
            cls.SLAVYA_SCARED: "Scared or shy.",
        }.get(pose, "Unknown")
