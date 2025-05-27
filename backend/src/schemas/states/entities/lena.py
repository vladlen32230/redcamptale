from src.schemas.states.entities.base import Clothes, FacialExpression, Pose

class LenaClothes(Clothes):
    LENA_UNIFORM = "lena_uniform"
    LENA_SPORT = "lena_sport"

    @classmethod
    def get_clothes_description(cls, clothes: 'LenaClothes') -> str:
        return {
            cls.LENA_UNIFORM: "Soviet pioneer uniform with white shirt and blue skirt.",
            cls.LENA_SPORT: "Sportswear with a white t-shirt and blue shorts."
        }.get(clothes, "Unknown")


class LenaFacialExpression(FacialExpression):
    LENA_ANGRY = "lena_angry"
    LENA_NORMAL = "lena_normal"
    LENA_EVIL_SMILE = "lena_evil_smile"
    LENA_SHY = "lena_shy"
    LENA_SMILE = "lena_smile"
    LENA_SMILE2 = "lena_smile2"

    LENA_CRY = "lena_cry"
    LENA_CRY_SMILE = "lena_cry_smile"
    LENA_SAD = "lena_sad"
    LENA_SCARED = "lena_scared"
    LENA_SHOCKED = "lena_shocked"
    LENA_SURPRISED = "lena_surprised"

    LENA_ANGRY2 = "lena_angry2"
    LENA_GRIN = "lena_grin"
    LENA_LAUGH = "lena_laugh"
    LENA_RAGE = "lena_rage"
    LENA_SERIOUS = "lena_serious"
    LENA_SMILE3 = "lena_smile3"

    @classmethod
    def get_facial_expression_description(cls, facial_expression: 'LenaFacialExpression') -> str:
        return {
            cls.LENA_NORMAL: "Normal and casual.",
            cls.LENA_ANGRY: "Angry.",
            cls.LENA_EVIL_SMILE: "Smiling evil.",
            cls.LENA_SHY: "Shy.",
            cls.LENA_SMILE: "Smiling.",
            cls.LENA_SMILE2: "Smiling very happily.",
            cls.LENA_CRY: "Crying.",
            cls.LENA_CRY_SMILE: "Crying and smiling.",
            cls.LENA_SAD: "Sad.",
            cls.LENA_SCARED: "Scared.",
            cls.LENA_SHOCKED: "Shocked.",
            cls.LENA_SURPRISED: "Surprised.",
            cls.LENA_ANGRY2: "Angry.",
            cls.LENA_GRIN: "Grinning.",
            cls.LENA_LAUGH: "Laughing.",
            cls.LENA_RAGE: "Raging.",
            cls.LENA_SERIOUS: "Serious.",
            cls.LENA_SMILE3: "Smiling."
        }.get(facial_expression, "Unknown")


class LenaPose(Pose):
    LENA_NORMAL = "lena_normal"
    LENA_SAD = "lena_sad"
    LENA_SERIOUS = "lena_serious"

    @classmethod
    def get_pose_description(cls, pose: 'LenaPose') -> str:
        return {
            cls.LENA_NORMAL: "Smiling or angry.",
            cls.LENA_SAD: "Sad or surprised.",
            cls.LENA_SERIOUS: "Serious or grinning."
        }.get(pose, "Unknown")
