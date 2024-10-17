class ControlModel:
    def __init__(self, area_id, year, error_code, error_name, error_poz_name, error_description, warning_flag,
                 error_status_flag, error_query):
        self.area_id = area_id
        self.year = year
        self.error_code = error_code
        self.error_name = error_name
        self.error_poz_name = error_poz_name
        self.error_description = error_description
        self.warning_flag = warning_flag
        self.error_status_flag = error_status_flag
        self.error_query = error_query



    def get_area_id(self):
        return self.area_id

    def set_area_id(self, area_id):
        self.area_id = area_id

    def get_year(self):
        return self.year

    def set_year(self, year):
        self.year = year

    def get_error_code(self):
        return self.error_code

    def set_error_code(self, error_code):
        self.error_code = error_code

    def get_error_name(self):
        return self.error_name

    def set_error_name(self, error_name):
        self.error_name = error_name

    def get_error_poz_name(self):
        return self.error_poz_name

    def set_error_poz_name(self, error_poz_name):
        self.error_poz_name = error_poz_name

    def get_error_description(self):
        return self.error_description

    def set_error_description(self, error_description):
        self.error_description = error_description

    def get_warning_flag(self):
        return self.warning_flag

    def set_warning_flag(self, warning_flag):
        self.warning_flag = warning_flag

    def get_error_status_flag(self):
        return self.error_status_flag

    def set_error_status_flag(self, error_status_flag):
        self.error_status_flag = error_status_flag

    def get_error_query(self):
        return self.error_query

    def set_error_query(self, error_query):
        self.error_query = error_query

