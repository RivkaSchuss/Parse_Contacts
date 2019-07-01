from collections import defaultdict
from datetime import datetime
from base64 import b64decode
from os.path import isfile
from re import sub
import webbrowser
from sys import argv

date_format = '%Y-%m-%d %H:%M:%S'
standard_length = 16


def main():
    if len(argv) == 1:
        file_name = 'ex_v7'
    else:
        file_name = argv[1]

    parser = Parser(file_name)

    # create a dictionary, according to the first identifier of each line of the file
    attribute_dic = {'86B7': 'first_contact', '9E60': 'last_contact', '5159': 'numbers', 'D812': 'record', '6704': 'image'}

    attributes, contact_identifiers = parser.parse(attribute_dic)
    contact_list = list()

    # creating an identifier for each contact value
    for identifier in contact_identifiers:
        first_contact = attributes['first_contact'][identifier]
        last_contact = attributes['last_contact'][identifier]
        numbers = attributes['numbers'][identifier]
        record = attributes['record'][identifier]
        image = attributes['image'][identifier]

        contact_list.append(Contact(first_contact, last_contact, numbers, record, image))

    # print all of the contacts
    print '\n'
    for contact in contact_list:
        print contact


class Parser:
    def __init__(self, file_name, len_id=4, len_info=5):
        self.file_name = file_name
        self.len_id = len_id
        self.len_info = len_info

    def parse(self, attribute, attribute_list=None):
        with open(self.file_name, 'r') as f:
            file_lines = f.readlines()

        attribute_dic = {}
        contact_identifiers = set()

        if not attribute_list:
            attribute_list = ['numbers', 'record']

        for line in file_lines:
            attribute_name = attribute[line[:self.len_id]]
            index = self.len_id
            line_length = len(line.strip())

            if attribute_name not in attribute_dic:
                attribute_dic[attribute_name] = defaultdict(lambda: [] if attribute_name in attribute_list else '')

            while index < line_length:
                contact_id = line[index:index + self.len_id]
                index += self.len_id
                contact_identifiers.add(contact_id)
                info_len = int(line[index:index + self.len_info], standard_length)
                index += self.len_info
                if attribute_name in attribute_list:
                    attribute_dic[attribute_name][contact_id].append(
                        line[index:index + info_len])
                else:
                    attribute_dic[attribute_name][contact_id] = line[index:index + info_len]

                index += info_len

        return attribute_dic, contact_identifiers


class Contact(object):
    def __init__(self, first_name, last_name, numbers, records, image):
        self.first_name = first_name
        self.last_name = last_name
        self.numbers = numbers
        self.records = records
        self.image = image
        self.full_name = self.first_name + ' ' + self.last_name

    # function to convert all of the contact details into one continuous string
    def __str__(self):
        contact_as_string = ''
        contact_as_string += 'Name: '
        contact_as_string += self.first_name + ' ' + self.last_name + '\n'
        contact_as_string += 'Phone number(s): '
        for phone in self.numbers:
            contact_as_string += phone + '\n'
        contact_as_string += 'Call records: '
        for call_record in self.records:
            contact_as_string += call_record + '\n'
        return contact_as_string

    def show_image(self):
        self.save_image()
        image_name = self.full_name + '.jpg'
        if isfile(image_name):
            webbrowser.open(image_name)

    def save_image(self):
        if self.image:
            image_name = self.full_name + '.jpg'

            if not isfile(image_name):
                image_data = b64decode(self.image)

                with open(image_name, 'wb') as f:
                    f.write(image_data)

    @property
    def records(self):
        return self._records

    @records.setter
    def records(self, value):
        self._records = []
        for time_stamp in value:
            self._records.append(datetime.fromtimestamp(int(time_stamp)).strftime(date_format))

    @property
    def numbers(self):
        return self._numbers

    @numbers.setter
    def numbers(self, value):
        self._numbers = value

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        # removing non-ascii spaces
        self._first_name = sub(r'[^\x00-\x7F]+', ' ', value)

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = sub(r'[^\x00-\x7F]+', ' ', value)

    @property
    def full_name(self):
        return self._full_name

    @full_name.setter
    def full_name(self, value):
        self._full_name = value.strip()


if __name__ == '__main__':
    main()