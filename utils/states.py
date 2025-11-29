from aiogram.fsm.state import StatesGroup, State


class AddResponseState(StatesGroup):
    waiting_for_trigger = State()
    waiting_for_type = State()
    waiting_for_content = State()


class DeleteResponseState(StatesGroup):
    waiting_for_trigger = State()


class EditResponseState(StatesGroup):
    waiting_for_trigger = State()
    waiting_for_type = State()
    waiting_for_content = State()


class BroadcastState(StatesGroup):
    waiting_for_text = State()


class ManagerAddState(StatesGroup):
    waiting_for_tg_id = State()


class ManagerRemoveState(StatesGroup):
    waiting_for_tg_id = State()
