#!python
# Copyright 2019 Vale
# parse vulcan map files using a DSL engine
# v1.0 04/2018 paulo.ernesto

import sys, os.path
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.zip')

import lark

#%import common.WS
#%import common.CNAME
mapfile_grammar = r"""
  WS: /[ \t\f\r\n]/+
  LCASE_LETTER: "a".."z"
  UCASE_LETTER: "A".."Z"
  LETTER: UCASE_LETTER | LCASE_LETTER
  WORD: LETTER+
  DIGIT: "0".."9"
  CNAME: ("_"|LETTER) ("_"|LETTER|DIGIT)*

  ?start: file

  ?value: definition
        | tab
        | pair
        | terminal

  file: value+ "END" "$FILE"
  COMMENT: /\*.*/
  definition: "BEGIN" "$DEF" CNAME value+ "END" "$DEF" CNAME
  tab: "BEGIN" "$TAB" CNAME value+ "END" "$TAB" CNAME
  ESCAPED_STRING: "'" ("\\'"|/[^']/)* "'"
  terminal: ESCAPED_STRING | CNAME
  pair: CNAME "=" [terminal]


  %ignore WS
  %ignore COMMENT
"""

class MapfileTransformer(lark.Transformer):
  pair = lambda self, _: [_[0].value, _[1]]
  definition = lambda self, _: [_[0].value, _[1:-1]]
  tab = lambda self, _: [_[0].value, _[1:-1]]
  file = dict
  terminal = lambda self, _: str.strip(_[0],"'")

def mapfile_parse(input_path):
  parser = lark.Lark(mapfile_grammar, parser='lalr', transformer=MapfileTransformer())
  with open(input_path) as f:
    return(parser.parse(f.read()))
  return({})

class VulcanScd(object):

  def __init__(self, input_path, v_def = None, v_tab = None):
    self._parse = mapfile_parse(input_path)
    
    self._device_color = None
    if 'DEVICE_COLOUR' in self._parse:
      self._device_color = self._parse['DEVICE_COLOUR'][0][1]

    self._def = None
    self._tab = None
    if v_def is not None:
      if v_def in self._parse:
        self._def = self._parse[v_def]
      
      if v_tab is not None:
        v_tab = str(v_tab).upper()
        self._tab = dict(self._def)
        if v_tab in self._tab:
          self._tab = self._tab[v_tab]

  def __getitem__(self, key):
    if self._def is None or self._tab is None:
      return(None)
    c = None
    for i in range(len(self._tab)):
      if self._tab[i].upper() == str(key).upper():
        c = int(self._tab[i - 1])
        break
    rgb = (1,1,1)
    if c is not None and self._device_color is not None:
      for i in range(0,len(self._device_color),4):
        if int(self._device_color[i]) == c:
          rgb = [float(self._device_color[_]) / 15.0 for _ in (i+1, i+3, i+2)]
    return(rgb)
