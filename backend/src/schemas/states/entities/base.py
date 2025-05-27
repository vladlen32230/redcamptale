from enum import Enum

class Clothes(str, Enum):
    @classmethod
    def get_clothes_description(cls, clothes: 'Clothes') -> str:
        raise NotImplementedError

class FacialExpression(str, Enum):
    @classmethod
    def get_facial_expression_description(cls, facial_expression: 'FacialExpression') -> str:
        raise NotImplementedError

class Pose(str, Enum):
    @classmethod
    def get_pose_description(cls, pose: 'Pose') -> str:
        raise NotImplementedError
    