from aiogram.fsm.state import State, StatesGroup


class AddSectionStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_image_url = State()


class AddSubsectionStates(StatesGroup):
    waiting_for_section_id = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_image_url = State()


class AddMaterialStates(StatesGroup):
    waiting_for_section_id = State()
    waiting_for_subsection_id = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_tg_link = State()
    waiting_for_image_url = State()


class EditStates(StatesGroup):
    waiting_for_entity_type = State()   # section / subsection / material
    waiting_for_entity_id = State()
    waiting_for_field_name = State()
    waiting_for_new_value = State()