from src.schemas.states.entities.base import Clothes, FacialExpression, Pose

class AliceClothes(Clothes):
    ALICE_UNIFORM = "alice_uniform"
    ALICE_CLEAVAGE = "alice_cleavage"

    @classmethod
    def get_clothes_description(cls, clothes: 'AliceClothes') -> str:
        return {
            cls.ALICE_UNIFORM: "Soviet pioneer uniform with white shirt and blue skirt.",
            cls.ALICE_CLEAVAGE: "Soviet pioneer uniform with white shirt and blue skirt, but with a cleavage and exposed belly."
        }.get(clothes, "Unknown")

class AliceFacialExpression(FacialExpression):
    ALICE_CRY = "alice_cry"
    ALICE_SCARED = "alice_scared"
    ALICE_SHOCKED = "alice_shocked"
    ALICE_SURPRISED = "alice_surprised"

    ALICE_GRIN = "alice_grin"

    ALICE_GUILTY = "alice_guilty"
    ALICE_SAD = "alice_sad"
    ALICE_SHY = "alice_shy"

    ALICE_LAUGH = "alice_laugh"
    ALICE_NORMAL = "alice_normal"
    ALICE_SMILE = "alice_smile"
    
    ALICE_ANGRY = "alice_angry"
    ALICE_RAGE = "alice_rage"

    @classmethod
    def get_facial_expression_description(cls, facial_expression: 'AliceFacialExpression') -> str:
        return {
            cls.ALICE_NORMAL: "Normal and casual.",
            cls.ALICE_SHY: "Very shy.",
            cls.ALICE_LAUGH: "Laughing and happy.",
            cls.ALICE_SAD: "Scared and frightened.",
            cls.ALICE_GUILTY: "Guilty and ashamed.",
            cls.ALICE_SMILE: "Smiling and happy.",
            cls.ALICE_ANGRY: "Angry.",
            cls.ALICE_RAGE: "Raging.",
            cls.ALICE_CRY: "Crying.",
            cls.ALICE_SCARED: "Scared and frightened.",
            cls.ALICE_SHOCKED: "Shocked.",
            cls.ALICE_SURPRISED: "Surprised.",
            cls.ALICE_GRIN: "Grinning."
        }.get(facial_expression, "Unknown")

class AlicePose(Pose):
    ALICE_NORMAL = "alice_normal"
    ALICE_CONSTRAINED = "alice_constrained"
    ALICE_ANGRY = "alice_angry"
    ALICE_CONFUSED = "alice_confused"
    ALICE_GRIN = "alice_grin"

    @classmethod
    def get_pose_description(cls, pose: 'AlicePose') -> str:
        return {
            cls.ALICE_NORMAL: "Normal or happy.",
            cls.ALICE_CONSTRAINED: "Guilty, sad or shy.",
            cls.ALICE_ANGRY: "Very angry.",
            cls.ALICE_CONFUSED: "Confused.",
            cls.ALICE_GRIN: "Grinning."
        }.get(pose, "Unknown")
