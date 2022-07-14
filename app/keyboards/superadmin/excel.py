from enum import Enum

from aiogram.dispatcher.filters.callback_data import CallbackData

from app.keyboards.superadmin.registry import Registry


class ExcelAction(Enum):
    IMPORT = "export_data"
    EXPORT = "export"


class ExcelCallbackFactory(CallbackData, prefix="excel"):
    action: ExcelAction
    registry: Registry
