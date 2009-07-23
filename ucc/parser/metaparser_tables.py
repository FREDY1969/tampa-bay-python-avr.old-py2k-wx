
# ucc/parser/metaparser_tables.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = '\x1e\x9a\x98{\xaf\xef\xee\xb0\xee\x97H\x9b\x98\x19\x15\\'
    
_lr_action_items = {'NEWLINE_TOK':([0,1,3,5,7,8,12,13,18,19,20,21,22,23,24,25,26,28,29,30,33,34,36,37,38,39,41,43,44,],[-3,3,-4,8,-12,-5,-17,-14,-12,-12,-26,-13,-29,-25,-7,-27,-28,-10,-11,-30,-16,-15,-20,-19,-18,-21,-22,-24,-23,]),'CHAR_TOKEN':([7,13,18,19,20,21,22,23,24,25,26,27,28,29,30,34,36,37,38,39,41,43,44,],[-12,20,-12,-12,-26,-13,-29,-25,-7,-27,-28,-12,-10,-11,-30,20,-20,-19,-18,-21,-22,-24,-23,]),'TUPLE_NONTERMINAL':([0,1,3,7,8,13,18,19,20,21,22,23,24,25,26,27,28,29,30,34,36,37,38,39,41,43,44,],[-3,4,-4,-12,-5,22,-12,-12,-26,-13,-29,-25,-7,-27,-28,-12,-10,-11,-30,22,-20,-19,-18,-21,-22,-24,-23,]),')':([10,14,15,16,32,42,],[-31,30,-8,-32,-34,-33,]),'(':([6,20,22,23,25,26,29,],[10,-26,-29,-25,-27,-28,10,]),'+':([20,22,23,25,26,28,29,43,44,],[-26,-29,-25,-27,-28,37,-11,-24,-23,]),'*':([20,22,23,25,26,28,29,43,44,],[-26,-29,-25,-27,-28,36,-11,-24,-23,]),'}':([13,19,20,21,22,23,24,25,26,27,28,29,30,34,35,36,37,38,39,41,43,44,],[-14,-12,-26,-13,-29,-25,-7,-27,-28,-12,-10,-11,-30,-15,43,-20,-19,-18,-21,-22,-24,-23,]),',':([15,16,32,42,],[31,-32,-34,-33,]),'PYTHON_CODE':([17,],[32,]),'TOKEN':([7,13,18,19,20,21,22,23,24,25,26,27,28,29,30,34,36,37,38,39,41,43,44,],[-12,25,-12,-12,-26,-13,-29,-25,-7,-27,-28,-12,-10,-11,-30,25,-20,-19,-18,-21,-22,-24,-23,]),'AS_TOK':([20,22,23,25,26,29,],[-26,-29,-25,-27,-28,40,]),'?':([20,22,23,25,26,28,29,43,44,],[-26,-29,-25,-27,-28,38,-11,-24,-23,]),'ELLIPSIS':([20,22,23,25,26,28,29,43,44,],[-26,-29,-25,-27,-28,39,-11,-24,-23,]),'{':([7,13,18,19,20,21,22,23,24,25,26,27,28,29,30,34,36,37,38,39,41,43,44,],[-12,27,-12,-12,-26,-13,-29,-25,-7,-27,-28,-12,-10,-11,-30,27,-20,-19,-18,-21,-22,-24,-23,]),':':([4,6,9,11,30,],[7,-6,-9,18,-30,]),'TOKEN_IGNORE':([7,13,18,19,20,21,22,23,24,25,26,27,28,29,30,34,36,37,38,39,41,43,44,],[-12,23,-12,-12,-26,-13,-29,-25,-7,-27,-28,-12,-10,-11,-30,23,-20,-19,-18,-21,-22,-24,-23,]),'|':([7,12,13,18,19,20,21,22,23,24,25,26,27,28,29,30,33,34,35,36,37,38,39,41,43,44,],[-12,19,-14,-12,-12,-26,-13,-29,-25,-7,-27,-28,-12,-10,-11,-30,19,-15,19,-20,-19,-18,-21,-22,-24,-23,]),'NONTERMINAL':([0,1,3,7,8,10,13,18,19,20,21,22,23,24,25,26,27,28,29,30,31,34,36,37,38,39,40,41,43,44,],[-3,6,-4,-12,-5,17,26,-12,-12,-26,-13,-29,-25,-7,-27,-28,-12,-10,-11,-30,17,26,-20,-19,-18,-21,44,-22,-24,-23,]),'$end':([0,1,2,3,5,7,8,12,13,18,19,20,21,22,23,24,25,26,28,29,30,33,34,36,37,38,39,41,43,44,],[-3,-1,0,-4,-2,-12,-5,-17,-14,-12,-12,-26,-13,-29,-25,-7,-27,-28,-10,-11,-30,-16,-15,-20,-19,-18,-21,-22,-24,-23,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'file2':([0,],[1,]),'parameters_opt':([10,],[14,]),'parameters':([10,],[15,]),'param_list':([6,29,],[9,41,]),'simple_word':([13,34,],[29,29,]),'alternatives':([7,18,27,],[12,33,35,]),'rule':([1,],[5,]),'parameterized_word':([13,34,],[24,24,]),'production':([7,18,19,27,],[13,13,34,13,]),'param_list_opt':([6,],[11,]),'file':([0,],[2,]),'word':([13,34,],[21,21,]),'sub_rule':([13,34,],[28,28,]),'parameter':([10,31,],[16,42,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> file","S'",1,None,None,None),
  ('file -> file2','file',1,'p_file','ucc/parser/metaparser.py',25),
  ('file -> file2 rule','file',2,'p_file','ucc/parser/metaparser.py',26),
  ('file2 -> <empty>','file2',0,'p_none','ucc/parser/metaparser.py',31),
  ('file2 -> file2 NEWLINE_TOK','file2',2,'p_none','ucc/parser/metaparser.py',32),
  ('file2 -> file2 rule NEWLINE_TOK','file2',3,'p_none','ucc/parser/metaparser.py',33),
  ('param_list_opt -> <empty>','param_list_opt',0,'p_none','ucc/parser/metaparser.py',34),
  ('word -> parameterized_word','word',1,'p_first','ucc/parser/metaparser.py',39),
  ('parameters_opt -> parameters','parameters_opt',1,'p_first','ucc/parser/metaparser.py',40),
  ('param_list_opt -> param_list','param_list_opt',1,'p_first','ucc/parser/metaparser.py',41),
  ('parameterized_word -> sub_rule','parameterized_word',1,'p_first','ucc/parser/metaparser.py',42),
  ('sub_rule -> simple_word','sub_rule',1,'p_first','ucc/parser/metaparser.py',43),
  ('production -> <empty>','production',0,'p_empty_tuple','ucc/parser/metaparser.py',48),
  ('production -> production word','production',2,'p_append','ucc/parser/metaparser.py',53),
  ('alternatives -> production','alternatives',1,'p_alternatives_1','ucc/parser/metaparser.py',58),
  ('alternatives -> alternatives | production','alternatives',3,'p_alternatives_n','ucc/parser/metaparser.py',63),
  ('rule -> NONTERMINAL param_list_opt : alternatives','rule',4,'p_rule1','ucc/parser/metaparser.py',68),
  ('rule -> TUPLE_NONTERMINAL : alternatives','rule',3,'p_rule2','ucc/parser/metaparser.py',181),
  ('word -> sub_rule ?','word',2,'p_opt_word','ucc/parser/metaparser.py',186),
  ('word -> sub_rule +','word',2,'p_one_or_more_word','ucc/parser/metaparser.py',214),
  ('word -> sub_rule *','word',2,'p_zero_or_more_word','ucc/parser/metaparser.py',245),
  ('word -> sub_rule ELLIPSIS','word',2,'p_word_ellipsis','ucc/parser/metaparser.py',273),
  ('parameterized_word -> simple_word param_list','parameterized_word',2,'p_parameterized_word','ucc/parser/metaparser.py',301),
  ('sub_rule -> simple_word AS_TOK NONTERMINAL','sub_rule',3,'p_sub_rule','ucc/parser/metaparser.py',311),
  ('sub_rule -> { alternatives }','sub_rule',3,'p_sub_rule2','ucc/parser/metaparser.py',323),
  ('simple_word -> TOKEN_IGNORE','simple_word',1,'p_token_ignore','ucc/parser/metaparser.py',330),
  ('simple_word -> CHAR_TOKEN','simple_word',1,'p_char_token','ucc/parser/metaparser.py',337),
  ('simple_word -> TOKEN','simple_word',1,'p_token','ucc/parser/metaparser.py',342),
  ('simple_word -> NONTERMINAL','simple_word',1,'p_nonterminal','ucc/parser/metaparser.py',349),
  ('simple_word -> TUPLE_NONTERMINAL','simple_word',1,'p_tuple_simple_word','ucc/parser/metaparser.py',354),
  ('param_list -> ( parameters_opt )','param_list',3,'p_param_list','ucc/parser/metaparser.py',359),
  ('parameters_opt -> <empty>','parameters_opt',0,'p_no_parameters_opt','ucc/parser/metaparser.py',364),
  ('parameters -> parameter','parameters',1,'p_parameters1','ucc/parser/metaparser.py',369),
  ('parameters -> parameters , parameter','parameters',3,'p_parametersn','ucc/parser/metaparser.py',374),
  ('parameter -> NONTERMINAL PYTHON_CODE','parameter',2,'p_parameter','ucc/parser/metaparser.py',380),
]
