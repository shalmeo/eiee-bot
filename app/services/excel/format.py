from openpyxl.styles import Alignment, Border, Side
from openpyxl.worksheet.worksheet import Worksheet


def format_row(worksheet: Worksheet, row: int, max_col=None) -> None:
    worksheet.row_dimensions[row].height = 30
    for tuple_cell in worksheet.iter_cols(min_row=row, max_row=row, max_col=max_col):
        cell = tuple_cell[0]
        cell.alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )

        if cell.column == 1:
            cell.border = Border(
                left=Side(style="medium"),
                top=Side(style="medium", color="CCCCCC"),
                bottom=Side(style="medium", color="CCCCCC"),
                right=Side(style="medium", color="CCCCCC"),
            )
        elif cell.column == max_col:
            cell.border = Border(
                right=Side(style="medium"),
                top=Side(style="medium", color="CCCCCC"),
                bottom=Side(style="medium", color="CCCCCC"),
                left=Side(style="medium", color="CCCCCC"),
            )
        else:
            cell.border = Border(
                top=Side(style="medium", color="CCCCCC"),
                bottom=Side(style="medium", color="CCCCCC"),
                right=Side(style="medium", color="CCCCCC"),
                left=Side(style="medium", color="CCCCCC"),
            )
