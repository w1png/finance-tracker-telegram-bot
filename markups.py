from aiogram import types
import text_templates as tt

btnCancelDelete = types.InlineKeyboardButton(text=tt.back, callback_data="cancelDelete")
btnBackMyInvites = types.InlineKeyboardButton(text=tt.back, callback_data="myInvites")
btnMyInvites = types.InlineKeyboardButton(text=tt.my_invites, callback_data="myInvites")
btnBackKickFromFamily = types.InlineKeyboardButton(text=tt.back, callback_data="kickFromFamily")

def single_button(button):
    markup = types.InlineKeyboardMarkup()
    markup.add(button)
    return markup

def get_markup_start(user):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user.is_in_family():
        markup.add(types.KeyboardButton(text=tt.family_bills_last_30_days))
        markup.add(types.KeyboardButton(text=tt.my_bills_last_30_days))
        if user.get_user_id() == user.get_family().get_creator().get_user_id():
            markup.add(types.KeyboardButton(text=tt.invite_to_family), types.KeyboardButton(text=tt.kick_from_family))
        markup.add(types.KeyboardButton(text=tt.leave_family))
    else:
        markup.add(types.KeyboardButton(text=tt.create_family), types.KeyboardButton(text=tt.my_invites))
        markup.add(types.KeyboardButton(text=tt.get_my_id))
    return markup


def get_markup_myInvites(user):
    markup = types.InlineKeyboardMarkup()
    for invite in user.get_invites():
        markup.add(types.InlineKeyboardButton(text=invite, callback_data="None"), types.InlineKeyboardButton(text=tt.accept, callback_data=f"acceptFamily{invite}"), types.InlineKeyboardButton(text=tt.decline, callback_data=f"declineFamily{invite}"))
    return markup

    
def get_markup_kickFromFamily(family):
    markup = types.InlineKeyboardMarkup()
    for user in family.get_user_list():
        markup.add(types.InlineKeyboardButton(text=str(user.get_user_id()), callback_data=f"kickFromFamily{user.get_user_id()}"))
    return markup