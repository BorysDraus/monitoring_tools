class SiteYearModel:
    def __init__(self, area_id, year, controll_flag, resignation_flag, cause_of_resignation,
                 nature_values, comments, site_description, habitat_description, owner,
                 date_of_controll, general_assessment, general_assessment_comments, x_coord,
                 y_coord, z_coord, z_min, z_max, site_area):
        self.area_id = area_id
        self.year = year
        self.controll_flag = controll_flag
        self.resignation_flag = resignation_flag
        self.cause_of_resignation = cause_of_resignation
        self.nature_values = nature_values
        self.comments = comments
        self.site_description = site_description
        self.habitat_description = habitat_description
        self.owner = owner
        self.date_of_controll = date_of_controll
        self.general_assessment = general_assessment
        self.general_assessment_comments = general_assessment_comments
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.z_coord = z_coord
        self.z_min = z_min
        self.z_max = z_max
        self.site_area = site_area
        # self.status_code = status_code
        # self.warnings_number = warnings_number
        # self.errors_number = errors_number

    def get_area_id(self):
        return self.area_id

    def set_area_id(self, area_id):
        self.area_id = area_id

    def get_year(self):
        return self.year

    def set_year(self, year):
        self.year = year

    def get_controll_flag(self):
        return self.controll_flag

    def set_controll_flag(self, controll_flag):
        self.controll_flag = controll_flag

    def get_resignation_flag(self):
        return self.resignation_flag

    def set_resignation_flag(self, resignation_flag):
        self.resignation_flag = resignation_flag

    def get_cause_of_resignation(self):
        return self.cause_of_resignation

    def set_cause_of_resignation(self, cause_of_resignation):
        self.cause_of_resignation = cause_of_resignation

    def get_nature_values(self):
        return self.nature_values

    def set_nature_values(self, nature_values):
        self.nature_values = nature_values

    def get_comments(self):
        return self.comments

    def set_comments(self, comments):
        self.comments = comments

    def get_site_description(self):
        return self.site_description

    def set_site_description(self, site_description):
        self.site_description = site_description

    def get_habitat_description(self):
        return self.habitat_description

    def set_habitat_description(self, habitat_description):
        self.habitat_description = habitat_description

    def get_owner(self):
        return self.owner

    def set_owner(self, owner):
        self.owner = owner

    def get_date_of_controll(self):
        return self.date_of_controll

    def set_date_of_controll(self, date_of_controll):
        self.date_of_controll = date_of_controll

    def get_general_assessmnent(self):
        return self.general_assessmnent

    def set_general_assessmnent(self, general_assessmnent):
        self.general_assessmnent = general_assessmnent

    def get_general_assessmnent_comments(self):
        return self.general_assessmnent_comments

    def set_general_assessmnent_comments(self, general_assessmnent_comments):
        self.general_assessmnent_comments = general_assessmnent_comments

    def get_x_coord(self):
        return self.x_coord

    def set_x_coord(self, x_coord):
        self.x_coord = x_coord

    def get_y_coord(self):
        return self.y_coord

    def set_y_coord(self, y_coord):
        self.y_coord = y_coord

    def get_z_coord(self):
        return self.z_coord

    def set_z_coord(self, z_coord):
        self.z_coord = z_coord

    def get_z_min(self):
        return self.z_min

    def set_z_min(self, z_min):
        self.z_min = z_min

    def get_z_max(self):
        return self.z_max

    def set_z_max(self, z_max):
        self.z_max = z_max

    def get_site_area(self):
        return self.site_area

    def set_site_area(self, site_area):
        self.site_area = site_area

    def get_status_code(self):
        return self.status_code

    def set_status_code(self, status_code):
        self.status_code = status_code

    def get_warnings_number(self):
        return self.warnings_number

    def set_warnings_number(self, warnings_number):
        self.warnings_number = warnings_number

    def get_errors_number(self):
        return self.errors_number

    def set_errors_number(self, errors_number):
        self.errors_number = errors_number