import codecs
import csv
import os

import bpy

from ..utils import ADDON_ID


def GetTranslationDict():
    dict = {}
    path = os.path.join(os.path.dirname(__file__), "translation_dictionary.csv")

    with codecs.open(path, "r", "utf-8") as f:
        reader = csv.reader(f)
        dict["zh_HANS"] = {}
        for row in reader:
            if row:
                for context in bpy.app.translations.contexts:
                    dict["zh_HANS"][(context, row[1].replace("\\n", "\n"))] = row[0].replace("\\n", "\n")
    return dict


def register():
    try:
        bpy.app.translations.register(ADDON_ID, GetTranslationDict())
    except:
        pass


def unregister():
    try:
        bpy.app.translations.unregister(ADDON_ID)
    except:
        pass
