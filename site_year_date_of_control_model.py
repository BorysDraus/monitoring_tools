class SiteYearDateOfControllModel:
    def __init__(self, area_id, year, date_of_controll, availability, description):
        self.area_id = area_id
        self.year = year
        self.date_of_controll = date_of_controll
        self.availability = availability
        self.description = description

    def get_area_id(self):
        return self.area_id

    def set_area_id(self, area_id):
        self.area_id = area_id

    def get_year(self):
        return self.year

    def set_year(self, year):
        self.year = year

    def get_date_of_controll(self):
        return self.date_of_controll

    def set_date_of_controll(self, date_of_controll):
        self.date_of_controll = date_of_controll

    def get_availability(self):
        return self.availability

    def set_availability(self, availability):
        self.availability = availability

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description