import codecs
import csv
import os
from pathlib import Path

import bpy

cwf = Path(__file__)
cwd = cwf.parent


def GetTranslationDict():
    dict = {}
    path = cwd / "translation_dictionary.csv"

    with codecs.open(path, "r", "utf-8") as f:
        reader = csv.reader(f)
        dict["zh_HANS"] = {}
        for row in reader:
            if not row or row[1] == "":
                continue
            if row:
                for context in bpy.app.translations.contexts:
                    try:
                        dict["zh_HANS"][(context, row[0].replace("\\n", "\n"))] = row[1].replace("\\n", "\n")
                    except IndexError as e:
                        print("翻译字典错误:\n", e)
                        pass
    return dict


def register():
    try:
        bpy.app.translations.register(__package__, GetTranslationDict())
    except Exception as e:
        print(e)


def unregister():
    try:
        bpy.app.translations.unregister(__package__)
    except Exception as e:
        print(e)
