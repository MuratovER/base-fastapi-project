import enum


class ReviewStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    DRAFT = "DRAFT"
    COMPLETED = "COMPLETED"


class UserRoleEnum(str, enum.Enum):
    EMPLOYER = "EMPLOYER"
    LEAD = "LEAD"
    MENTOR = "MENTOR"
    ADMIN = "ADMIN"


class FileStorageEnum(str, enum.Enum):
    FILESYSTEM = "FILESYSTEM"
    S3 = "S3"
