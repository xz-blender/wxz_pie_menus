METRIC_UNITS = {
    "KILOMETERS": "km",
    "METERS": "m",
    "CENTIMETERS": "cm",
    "MILLIMETERS": "mm",
}

IMPERIAL_UNITS = {"FEET": "ft", "INCHES": "in"}

OUTLINE_GROUPING_ENUM = (
    ("NONE", "None", "No Grouping", 0),
    # ("HOLES", "Holes", "Group by Holes", 1),
    ("MATERIAL", "Material", "Group by Material", 1),
    ("COLLECTION", "Collection", "Group by Collection", 2),
)

NODE_COLOR_SOURCES = {
    "BSDF_PRINCIPLED": "Base Color",
    "BSDF_DIFFUSE": "Color",
    "BSDF_GLOSSY": "Color",
    "EMISSION": "Color",
}
