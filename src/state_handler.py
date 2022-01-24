from aiogram.dispatcher.filters.state import StatesGroup, State

class InviteToFamily(StatesGroup):
    invited_id = State()


class changeName(StatesGroup):
    name = State()