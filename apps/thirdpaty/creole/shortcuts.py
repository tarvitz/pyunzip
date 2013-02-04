# coding: utf-8
from creole.html_emitter import HtmlEmitter
from creole import Parser

def creole_filter(value):
    p = Parser(value).parse()
    return HtmlEmitter(p).emit()

