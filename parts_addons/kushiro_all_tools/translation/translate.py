import bpy
import os, csv, codecs

def GetTranslationDict():
	dict = {}
	path = os.path.join(os.path.dirname(__file__), "translation_dictionary.csv")

	with codecs.open(path, 'r', 'utf-8') as f:
		reader = csv.reader(f)
		dict['zh_HANS'] = {}
		for row in reader:
			if row:
				for context in bpy.app.translations.contexts:
					dict['zh_HANS'][(context, row[1].replace('\\n', '\n'))] = row[0].replace('\\n', '\n')

	return dict