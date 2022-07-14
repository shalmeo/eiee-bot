import dataclass_factory
import openpyxl

from typing import BinaryIO

from app.misc.exceptions import ExcelCellValidateError
from app.misc.models import GroupModel


def import_groups_excel(downloaded: BinaryIO):
    workbook = openpyxl.load_workbook(downloaded)
    worksheet = workbook.active
    factory = dataclass_factory.Factory()

    groups = []
    for row in worksheet.iter_rows(min_row=2, min_col=2, max_col=16):
        group_info = []
        for cell in row:
            group_info.append(cell.value)
        try:
            group, students = _get_group_model(group_info)
            print(group)
        except (ExcelCellValidateError, ValueError, AttributeError):
            continue
        serialized = factory.dump(group)
        groups.append([serialized, students])

    return len(groups), groups


def _get_group_model(group_info: list) -> tuple[GroupModel, list[int]]:
    unique_id_col = 0
    creator_id_col = 1
    title_col = 2
    description_col = 3
    teacher_id_col = 4
    students_col = 5

    unique_id = group_info[unique_id_col]
    creator_id = group_info[creator_id_col]
    title = group_info[title_col]
    description = group_info[description_col]
    teacher_id = group_info[teacher_id_col]
    students = group_info[students_col:]

    if not all(()):
        raise ExcelCellValidateError()

    return (
        GroupModel(
            uuid=unique_id,
            admin_id=creator_id,
            title=title,
            description=description,
            teacher_id=teacher_id,
        ),
        students,
    )
