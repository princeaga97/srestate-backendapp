from email import message
from ntpath import join
from property.message_mapping import MSG_MAPPING


def create_msg(jobject):
    msg_string = ""

    for estate in jobject:
        msg_string = msg_string + " \n \n" + str(estate["estate_name"]).upper()
        for attribute, value in estate.items():
            if attribute in MSG_MAPPING.keys():
                msg_string = msg_string + " \n" + MSG_MAPPING[attribute] + " " + str(value)
    

    return msg_string


