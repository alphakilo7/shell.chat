import os
import re
import sys
import json

# TODO
#   1.
#     method > to_yml$public
#     params > filename:str
#     returns > None


class SectionNotFoundError(Exception):
	pass


class KeyNotFoundError(Exception):
	pass


class SectionExistsError(Exception):
	pass


class NoValueError(Exception):
	pass


class INIParser:
	def __init__(self, filename, backup=False):
		'''
		INIParser object initialization method

		method > __init__$private
		params >
			filename:str - Name of the ini file
			backup:bool=False - set True to take backup of the file
		returns >
			None
		raises >
			None
		'''
		self.__file = filename
		if backup:
			os.system(f"cp {self.__file} {self.__file}-bak")
		self.__ini = open(self.__file, 'r').read().split('\n')

		self.__sections = []
		self.__settings = {}
		self.__comments = {}
		
		self.__persist_comments()
		self.__remove_blanks_and_comments()
		self.__get_sects()
		self.__get_settings()

	# PRIVATE FUNCTIONAL METHODS
	def __persist_comments(self):
		'''
		Comment persistence method. Keeps the comments in ini file safe
		method > 
			__persist_comments$private
		params >
			None
		returns >
			None
		raises >
			None
		'''
		lcount = 0
		for line in self.__ini:
			lcount += 1
			if not line == '':
				if line.lstrip()[0] == ";" or line.lstrip()[0] == "#":
					self.__comments[lcount] = line

	def __remove_blanks_and_comments(self):
		'''
		Remove blank lines and comments ['#', ';'] from the ini file
		method >
			__remove_blanks_and_comments$private
		params >
			None
		returns >
			None
		raises >
			None
		'''
		ini_t = self.__ini[:]
		self.__ini.clear()
		for line in ini_t:
			if not line == '' and not line.lstrip()[0] == ";" and not line.lstrip()[0] == "#":
				self.__ini.append(line)

	def __get_sects(self):
		'''
		Reads and stores ini file sections in sections list
		method >
			__get_sects$private
		params >
			None
		returns >
			None
		raises >
			None
		'''
		for line in self.__ini:
			if re.match(r"\[[a-zA-Z0-9\:_\-]+\]", line):
				self.__sections.append(re.sub(r"[\[]{1}|[\]]{1}", "", line))

	def __get_settings(self):
		'''
		Reads and stores ini settings respective to the sections in dictionary
		method >
			__get_settings$private
		params >
			None
		returns >
			None
		raises >
			None
		'''
		for line in self.__ini:
			if re.match(r"\[[a-zA-Z0-9\:_\-]+\]", line):
				head = re.sub(r"[\[]{1}|[\]]{1}", "", line)
				self.__settings[head] = dict()
			else:
				_key = line.split("=", 1)[0]
				_val = line.split("=", 1)[1]
				self.__settings[head][_key] = _val

	# GETTER METHODS
	def get_sections(self):
		'''
		Get the list of sections available in an ini file
		method >
			get_sections$public
		params >
			None
		return >
			sections:list - list of sections in ini file
		raises >
			None
		'''
		return self.__sections

	def get_all(self):
		'''
		Get all the section-wise settings at one place
		method >
			get_all$public
		params >
			None
		returns >
			settings:dict - Dictionary of dictionary of the settings, listed section-wise
		raises >
			None
		'''
		return self.__settings

	def get(self, section, key=None):
		'''
		Get the value of section or key in the ini file as per requirement.
		method >
			get$public
		params >
			section:str - name of the section in ini file to get values of
			key:str=None - name of the key under a section to get value of
		returns >
			section:dict - Dictionary of key value pairs under a section
			value:str - value of the asked key under the section
		raises >
			SectionNotFoundError - if the param section is not present in the ini file
			KeyNotFoundError - if the param key is nt present under the designated sections
		'''
		if key == None:
			if not section in self.__sections:
				raise SectionNotFoundError(f"The section {section} does not exist in the configuration!")
			else:
				return self.__settings[section]
		else:
			try:
				return self.__settings[section][key]
			except KeyError:
				raise KeyNotFoundError(f"The key {key} does not exist in the section {section}! Operation failed.")


	# SETTER METHOD
	def set(self, section, key=None, value=None):
		'''
		Set the value for a particular key in a section.
		Allows overriding of the existing keys also.
		method >
			set$public
		params >
			section:str - name of the section to search value under
			key:str=None - name of the key under section to set value of
			param:obj=None - value of the key
		returns >
			None
		raises >
			SectionExistsError - if the section already exists and not key, value are provided
			NoValueError - if the key is given but not value
		'''
		if key == None and value == None and not section in self.__sections:
			self.__settings[section] = dict()
		elif key == None and value == None and section in self.__sections:
			raise SectionExistsError(f"The {section} already exists! Provide key and value pair to set.")
		else:
			if value == None:
				raise NoValueError(f"There is no value available for key {key} to set! Enter one.")
			try:
				self.__settings[section][key] = value
			except KeyError:
				self.__settings[section] = dict()
				self.__settings[section][key] = value

	# DELETE METHOD
	def delete(self, section, key=None):
		'''
		Delete the section or key under a section
		method >
			delete$public
		params >
			section:str - name of the section to delete. deletes whole section if not key is provided
			key:str=None - name of the key under a section to delete
		returns >
			None
		raises >
			SectionNotFoundError - if param section does not exist to delete
			KeyNotFoundError - if param key is not available under a section to delete
		'''
		if key == None and not section in self.__sections:
			raise SectionNotFoundError(f"The {section} does not exist! Operation failed!")
		elif key == None and section in self.__sections:
			del self.__settings[section]
		else:
			try:
				del self.__settings[section][key]
			except KeyError:
				raise KeyNotFoundError(f"The key {key} in section {section} does not exist! Operation failed!")

	# COMMIT METHOD
	def __pre_commit(self):
		'''
		Pre commit method to write changes in internal ini structure
		Compiles sections, key-value pairs and comments in internal ini structure
		method >
			__pre_commit$private
		params >
			None
		returns >
			None
		raises >
			None
		'''
		self.__ini.clear()
		for sect in self.__settings.keys():
			self.__ini.append("[" + str(sect) + "]\n")
			for k, v in self.__settings[sect].items():
				self.__ini.append(str(k) + "=" + str(v) + "\n")
			self.__ini.append("\n")
	
		for line_num, cmnt in self.__comments.items():
			self.__ini.insert(line_num - 1, cmnt + "\n")

	def commit(self):
		'''
		The final commit method to write internal ini structure in the file.
		Truncates the existing file and writes compiled configuration to it
		method >
			commit$public
		params >
			None
		returns >
			None
		raises >
			None
		'''
		write_file = open(self.__file, "a+")
		write_file.truncate(0)
		self.__pre_commit()
		for line in self.__ini:
			write_file.write(line)
		write_file.close()

	def to_json(self, filename="output.json", indent=2):
		'''
		Write INI file contents to a JSON file. JSON can be imported easily in many other languages.
		method >
			to_json$public
		params >
			filename:str=output.json - name of the file to write contents in. By default, writes to output.json
			indent:int=2 - the indentation to be given in the json files to pretty-print
		returns >
			None
		raises >
			None
		'''
		inijson=json.dumps(self.__settings, indent=indent)
		outfile=open(filename, "w")
		outfile.write(inijson)
		outfile.close()


def run():
	'''
	Runner method
	'''
	# Initiate INIParser
	ini = INIParser('app.ini')

	# Get a section
	print(ini.get("host:warlax-co"))

	# Create a blank section
	ini.set("host:agsft-com")

	# Set value under new section
	ini.set("host:agsft-com", "server_count", 8)

	# Write value to new section directly
	ini.set("host:groots-in", "username", "ubuntu-user")
	ini.set("host:groots-in", "password", "user@123987")

	ini.set("baseconfig", "superuser", "dexter")
	
	# Delete certain key
	ini.delete("baseconfig", "port")

	# Commit the changes to the file
	ini.commit()

	# Get the output in json file
	ini.to_json("Filename.json", indent=4)


if __name__ == "__main__":
	# run()
	pass
