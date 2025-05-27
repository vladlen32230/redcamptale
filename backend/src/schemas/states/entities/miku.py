from enum import Enum

class MikuClothes(str, Enum):
    MIKU_UNIFORM = "miku_uniform"

    @classmethod
    def get_clothes_description(cls, clothes: 'MikuClothes') -> str:
        return {
            cls.MIKU_UNIFORM: "Soviet pioneer uniform with white shirt and blue skirt. Also wears stockings.",
        }.get(clothes, "Unknown")


class MikuFacialExpression(str, Enum):
    MIKU_CRY = "miku_cry"
    MIKU_FROWNING = "miku_frowning"
    MIKU_LAUGH = "miku_laugh"
    MIKU_SCARED = "miku_scared"
    MIKU_SHOCKED = "miku_shocked"
    MIKU_SHY = "miku_shy"
    MIKU_SURPRISED = "miku_surprised"
    MIKU_CRY_SMILE = "miku_cry_smile"
    MIKU_GRIN = "miku_grin"
    MIKU_HAPPY = "miku_happy"
    MIKU_SAD = "miku_sad"
    MIKU_SMILE = "miku_smile"

    MIKU_ANGRY = "miku_angry"
    MIKU_NORMAL = "miku_normal"
    MIKU_RAGE = "miku_rage"
    MIKU_SERIOUS = "miku_serious"
    MIKU_UPSET = "miku_upset"

    @classmethod
    def get_facial_expression_description(cls, facial_expression: 'MikuFacialExpression') -> str:
        return {
            cls.MIKU_CRY: "Crying.",
            cls.MIKU_FROWNING: "Frowning.",
            cls.MIKU_LAUGH: "Laughing.",
            cls.MIKU_SCARED: "Scared.",
            cls.MIKU_SHOCKED: "Shocked.",
            cls.MIKU_SHY: "Shy.",
            cls.MIKU_SURPRISED: "Surprised.",
            cls.MIKU_CRY_SMILE: "Smiling very happy, almost crying.",
            cls.MIKU_GRIN: "Grinning.",
            cls.MIKU_HAPPY: "Happy.",
            cls.MIKU_SAD: "Sad.",
            cls.MIKU_SMILE: "Smiling.",
            cls.MIKU_NORMAL: "Normal.",
            cls.MIKU_RAGE: "Rage.",
            cls.MIKU_SERIOUS: "Serious.",
            cls.MIKU_UPSET: "Upset.",
            cls.MIKU_ANGRY: "Angry.",
        }.get(facial_expression, "Unknown")


class MikuPose(str, Enum):
    MIKU_NORMAL = "miku_normal"
    MIKU_LOVELY = "miku_lovely"
    MIKU_SERIOUS = "miku_serious"

    @classmethod
    def get_pose_description(cls, pose: 'MikuPose') -> str:
        return {
            cls.MIKU_NORMAL: "Surprised, happy, upset or shy.",
            cls.MIKU_LOVELY: "Very happy.",
            cls.MIKU_SERIOUS: "Serious or upset.",
        }.get(pose, "Unknown")
