import enum


class Analisi(str, enum.Enum):
    PRIMA = "prima"
    DOPO = "dopo"
    DIFF = "diff"
