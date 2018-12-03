class APIMandatoryFieldList(object):
    field_list = {
        'signup': ['email', 'phone'],
        'add_contact_list': ['owner', 'contact_list'],
        'search_contact': ['owner', 'search_key'],
    }

    @staticmethod
    def get_mandatory_field_list(key):
        try:
            return APIMandatoryFieldList.field_list[key]
        except AttributeError:
            return None
