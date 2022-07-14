from enum import Enum


class Registry(Enum):
    ADMINISTRATORS = "admins"
    TEACHERS = "teachers"
    STUDENTS = "students"
    GROUPS = "groups"
    UNREG = "unreg users"
