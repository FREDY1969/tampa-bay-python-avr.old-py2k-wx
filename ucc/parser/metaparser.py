# metaparser.py

""" See http://www.dabeaz.com/ply/ply.html for syntax of grammer definitions.
""" 

from __future__ import with_statement
from ply import yacc
from ucc.parser import metascanner, scanner_init
from ucc.ast import ast

tokens = metascanner.tokens

def p_none(p):
    ''' file :
             | file NEWLINE_TOK
             | file rule NEWLINE_TOK
        param_list_opt :
    '''
    p[0] = None

def p_first(p):
    ''' word: parameterized_word
        parameters_opt : parameters
        param_list_opt : param_list
        parameterized_word : sub_rule
    '''
    p[0] = p[1]

def p_empty_tuple(p):
    ''' production :
    '''
    p[0] = ()

def p_singleton_tuple(p):
    ''' alternatives : production
    '''
    p[0] = (p[1],)

def p_append(p):
    ''' alternatives : alternatives '|' production
        production : production word
    '''
    p[0] = p[1] + (p[-1],)

def p_rule1(p):
    ''' rule : NONTERMINAL param_list_opt ':' alternatives
    '''
    rule_name = p[1]
    param_list = p[2]
    for words in p[4]:
        p_fn_name = ast.gensym('p_' + rule_name)
        print """
def %s(p):
    r''' %s : %s
    '''
    """ % (p_fn_name, rule_name, ' '.join(word[0] for word in words))
        prep = []
        args = []
        if param_list is not None:
            fn_word_params = param_list
            fn_word_offset = None
        else:
            fn_word_params = None
            fn_word_offset = None
        for i, (rule_text, type, offset, prep_code, params) in enumerate(words):
            if prep_code: prep.append(prep_code % {'offset': offset + i + 1})
            if type == 'fn_word':
                if fn_word_offset:
                    raise SyntaxError("duplicate function words in production",
                                      scanner_init.syntaxerror_params(p[1]))
                fn_word_offset = offset + i + 1
                fn_word_params = params
            else:
                assert not params, "non fn_word has parameters"
                if type == 'ignore':
                    pass
                elif type == 'single_arg':
                    args.append('args.append(p[%d])' % (offset + i + 1))
                elif type == 'tuple':
                    args.append('args.append(p[%d])' % (offset + i + 1))
                elif type == 'ellipsis':
                    args.append('args.extend(p[%d])' % (offset + i + 1))
        if fn_word_offset is None:
            raise SyntaxError("missing function word in production",
                              scanner_init.syntaxerror_params(p[1]))
        if prep:
            print '\n    '.join(prep)
            print '    ',

        print "args = []"
        for arg in args: print "    ", arg
        if fn_word_params:
            print "p[0] = ast.ast(p[1], p[-1], %s, *args)" % (
                     ', '.join("%s=%s" %
                                 (key, value % {'offset': fn_word_offset})
                               for key, value in fn_word_params.iteritems())
                  )
        else:
            print "p[0] = ast.ast(p[1], p[-1], *args)"

def p_rule2(p):
    ''' rule : TUPLE_NONTERMINAL ':' alternatives
    '''
    rule_name = p[1]
    for words in p[3]:
        p_fn_name = ast.gensym('p_' + rule_name)
        print """
def %s(p):
    r''' %s : %s
    '''
    """ % (p_fn_name, rule_name, ' '.join(word[0] for word in words))
        prep = []
        args = []
        fn_word_params = None
        fn_word_offset = None
        tuple_offset = None
        for i, (rule_text, type, offset, prep_code, params) in enumerate(words):
            if prep_code: prep.append(prep_code % {'offset': offset + i + 1})
            if type == 'fn_word':
                fn_word_offset = offset + i + 1
                fn_word_params = params
            else:
                assert not params, "non fn_word has parameters"
                if type == 'ignore':
                    pass
                elif type == 'single_arg':
                    args.append('args.append(p[%d])' % (offset + i + 1))
                elif type == 'tuple':
                    args.append('args.append(p[%d])' % (offset + i + 1))
                    if tuple_offset is not None:
                        if tuple_offset is not 'ellipsis':
                            tuple_offset = 'dup'
                    else:
                        tuple_offset = i
                elif type == 'ellipsis':
                    tuple_offset = 'ellipsis'
                    args.append('args.extend(p[%d])' % (offset + i + 1))
        if prep:
            print '\n    '.join(prep)
            print '    ',
        if fn_word_offset is not None:
            print "args = []"
            for arg in args: print "    ", arg
            if fn_word_params:
                print "p[0] = (ast.ast(p[1], p[-1], %s, *args),)" % (
                         ', '.join("%s=%s" %
                                     (key, value % {'offset': fn_word_offset})
                                   for key, value in fn_word_params.iteritems())
                      )
            else:
                print "p[0] = (ast.ast(p[1], p[-1], *args),)"
        elif tuple_offset is None:
            if len(args) == 1:
                print "args = []"
                print '    ', args[0]
                print "    p[0] = tuple(args,)"
            else:
                raise SyntaxError("no tuple in production",
                                  scanner_init.syntaxerror_params(p[1]))
        elif tuple_offset == 'dup':
            raise SyntaxError("duplicate tuples in production",
                              scanner_init.syntaxerror_params(p[1]))
        elif tuple_offset == 'ellipsis':
            raise SyntaxError("ellipsis in production without function word",
                              scanner_init.syntaxerror_params(p[1]))
        else:
            print "p[0] = p[%d]" % (tuple_offset + 1)


def p_opt_word(p):
    ''' word: sub_rule '?'
    '''
    rule_text, type, offset, prep_code, params = p[1]
    rule_name = ast.gensym('optional')
    p_fn_name_0, p_fn_name_n = \
      ast.gensym('p_optional_no'), ast.gensym('p_optional_yes')
    print """
def %s(p):
    r''' %s :
    '''
    p[0] = None

def %s(p):
    r''' %s : %s
    '''
    %s
    p[0] = p[1]
""" % (p_fn_name_0, rule_name, p_fn_name_n, rule_name, rule_text,
       prep_code % {'offset': offset + 1})
    return rule_name, type, 0, None, None

def p_one_or_more_word(p):
    ''' word: sub_rule '+'
    '''
    rule_text, type, offset, prep_code, params = p[1]
    rule_name = ast.gensym('one_or_more')
    p_fn_name_1, p_fn_name_n = \
      ast.gensym('p_one_or_more_1'), ast.gensym('p_one_or_more_n')
    print """
def %s(p):
    r''' %s : %s
    '''
    %s
    p[0] = ()

def %s(p):
    r''' %s : %s %s
    '''
    %s
    p[0] = p[1] + (p[offset + 2],)
""" % (p_fn_name_1, rule_name, rule_text, prep_code % {'offset': offset + 1},
       p_fn_name_n, rule_name, rule_name, rule_text,
       prep_code % {'offset': offset + 2})
    return rule_name, tuple, 0, None, None

def p_zero_or_more_word(p):
    ''' word: sub_rule '*'
    '''
    rule_text, type, offset, prep_code, params = p[1]
    rule_name = ast.gensym('zero_or_more')
    p_fn_name_0, p_fn_name_n = \
      ast.gensym('p_zero_or_more_0'), ast.gensym('p_zero_or_more_n')
    print """
def %s(p):
    r''' %s :
    '''
    p[0] = ()

def %s(p):
    r''' %s : %s %s
    '''
    %s
    p[0] = p[1] + (p[offset + 2],)
""" % (p_fn_name_0, rule_name, p_fn_name_n, rule_name, rule_name, rule_text,
       prep_code % {'offset': offset + 2})
    return rule_name, tuple, 0, None, None

def p_word_ellipsis(p):
    ''' word: sub_rule ELLIPSIS
    '''
    rule_text, type, offset, prep_code, params = p[1]
    rule_name = ast.gensym('ellipsis')
    p_fn_name_0, p_fn_name_n = \
      ast.gensym('p_ellipsis_0'), ast.gensym('p_ellipsis_n')
    print """
def %s(p):
    r''' %s :
    '''
    p[0] = ()

def %s(p):
    r''' %s : %s %s
    '''
    %s
    p[0] = p[1] + (p[offset + 2],)
""" % (p_fn_name_0, rule_name, p_fn_name_n, rule_name, rule_name, rule_text,
       prep_code % {'offset': offset + 2})
    return rule_name, ellipsis, 0, None, None

def p_parameterized_word(p):
    ''' parameterized_word : simple_word param_list
    '''
    rule_text, type, offset, prep_code, params = p[1]
    if params:
        raise SyntaxError("duplicate initialization parameters",
                          scanner_init.syntaxerror_params(p[2]))
    param_list = p[2]
    p[0] = rule_text, 'fn_word', offset, prep_code, param_list

def p_ignored_word(p):
    ''' simple_word : TOKEN_IGNORE
                    | CHAR_TOKEN
    '''
    p[0] = p[1], 'ignore', 0, None, None

def p_simple_word(p):
    ''' simple_word : TOKEN
                    | NONTERMINAL
    '''
    p[0] = p[1], 'single_arg', 0, None, None

def p_tuple_simple_word(p):
    ''' simple_word : TUPLE_NONTERMINAL
    '''
    p[0] = p[1], 'tuple', 0, None, None

def p_param_list(p):
    ''' param_list : '(' parameters_opt ')'
    '''
    p[0] = p[2]

def p_no_parameters_opt(p):
    ''' parameters_opt : 
    '''
    p[0] = {}

def p_parameters1(p):
    ''' parameters : parameter
    '''
    p[0] = {p[1][0]: p[1][1]}

def p_parametersn(p):
    ''' parameters : parameters ',' parameter
    '''
    p[1][p[3][0]] = p[3][1]
    p[0] = p[1]

def p_parameter(p):
    ''' parameter: NONTERMINAL PYTHON_CODE
    '''
    p[0] = (p[1], p[2])

def p_error(t):
    if t is None:
        raise SyntaxError("invalid syntax", scanner_init.syntaxerror_params())
    else:
        raise SyntaxError("invalid syntax", scanner_init.syntaxerror_params(t))

