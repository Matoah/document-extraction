from typing import Union
from model.announcement import Announcement
from model.equation import Equation
from model.image import Image
from model.code import Code
from model.notice import Notice
from model.text import Text
from model.toc import TOC
from model.table import Table
from model.foreword import Foreword

DocumentContentItem = Union[Announcement, Code, Equation, Image, Notice, Table, Text, TOC, Foreword]