# metaparser.py

"""This parses the metasyntax (used to define parsers).

See the METASYNTAX file for the grammar that this recognizes.

See http://www.dabeaz.com/ply/ply.html for syntax of grammer definitions used
here.
""" 

from __future__ import with_statement

import string
import sys

from ucc.parser import metascanner, scanner_init
from ucc.ast import ast


tokens = metascanner.tokens

Tokens_used = set()

def p_file(p):
    ''' file : file2
             | file2 rule
    '''
    p[0] = Tokens_used

def p_none(p):
    ''' file2 :
              | file2 NEWLINE_TOK
              | file2 rule NEWLINE_TOK
        param_list_opt :
    '''
    p[0] = None

def p_first(p):
    ''' word : parameterized_word
        parameters_opt : parameters
        param_list_opt : param_list
        parameterized_word : sub_rule
        sub_rule : simple_word
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
    p[0] = p[1] + (p[len(p) - 1],)

def p_rule1(p):
    ''' rule : NONTERMINAL param_list_opt ':' alternatives
    '''
    gen_alternatives(p[1], p[4], normal_wrapup, p[2])

def gen_alternatives(rule_name, alternatives, wrapup_fn, param_list = None):
    for words in alternatives:
        p_fn_name = ast.gensym('p_' + rule_name)
        output("""
            def $fn_name(p):
                r''' $rule_name : $production
                '''
            """,
            fn_name = p_fn_name, rule_name = rule_name,
            production = ' '.join(word[0] for word in words))
        prep = []
        args = []
        last_arg = None
        tuple_offset = None
        has_ellipsis = False
        if param_list is not None:
            fn_word_params = param_list
            fn_word_offset = None
        else:
            fn_word_params = None
            fn_word_offset = None
        for i, (rule_text, type, offset, prep_code, params) in enumerate(words):
            if prep_code: prep.append(prep_code % {'offset': offset + i + 1})
            if type == 'fn_word':
                if fn_word_params is not None:
                    scanner_init.syntaxerror(
                      "duplicate function words in production")
                fn_word_offset = offset + i + 1
                fn_word_params = params
            else:
                assert not params, "non function word has parameters"
                if type == 'ignore':
                    pass
                elif type == 'single_arg':
                    args.append('args.append(p[%d])' % (offset + i + 1))
                    last_arg = offset + i + 1
                elif type == 'tuple':
                    args.append('args.append(p[%d])' % (offset + i + 1))
                    if tuple_offset is not None:
                        if not has_ellipsis:
                            tuple_offset = 'dup'
                    else:
                        tuple_offset = i
                elif type == 'ellipsis':
                    args.append('args.extend(p[%d])' % (offset + i + 1))
                    has_ellipsis = True

        if prep:
            print '\n'.join('    ' + p for p in prep)

        wrapup_fn(fn_word_params, fn_word_offset, args, last_arg, tuple_offset,
                  has_ellipsis)
        print

def normal_wrapup(fn_word_params, fn_word_offset, args, last_arg, tuple_offset,
                  has_ellipsis):
    if fn_word_params is None:
        if has_ellipsis or len(args) != 1 or last_arg is None:
            scanner_init.syntaxerror("missing function word in production")
        print "    p[0] = p[%s]" % last_arg
    else:
        print "    args = []"
        for arg in args: print "    " + arg
        if fn_word_params:
            print "    p[0] = ast.ast(p[1], p[len(p) - 1], %s, *args)" % (
                     ', '.join("%s=%s" %
                                 (key, value % {'offset': fn_word_offset})
                               for key, value in fn_word_params.iteritems())
                  )
        elif fn_word_offset is None:
            scanner_init.syntaxerror(
              "empty parameter list on nonterminal declaration")
        else:
            print "    p[0] = ast.ast(p[1], p[len(p) - 1], " \
                                     "word=p[%s], *args)" % fn_word_offset

def wrapup_tuple(fn_word_params, fn_word_offset, args, last_arg, tuple_offset,
                 has_ellipsis):
    if fn_word_params is not None:
        print "    args = []"
        for arg in args: print "    " + arg
        if fn_word_params:
            print "    p[0] = (ast.ast(p[1], p[len(p) - 1], %s, *args),)" \
                  % ', '.join("%s=%s" %
                                 (key, value % {'offset': fn_word_offset})
                               for key, value in fn_word_params.iteritems())
        else:
            print "    p[0] = (ast.ast(p[1], p[len(p) - 1], *args),)"
    elif has_ellipsis:
        scanner_init.syntaxerror(
          "ellipsis in production without function word")
    elif tuple_offset == 'dup':
        scanner_init.syntaxerror("duplicate tuples in production")
    elif tuple_offset is None:
        # Make a singleton tuple out of a single argument.
        if len(args) == 1:
            print "    args = []"
            print '    ' + args[0]
            print "    p[0] = tuple(args)"
        else:
            scanner_init.SyntaxError("no tuple in production")
    else:
        print "    p[0] = p[%d]" % (tuple_offset + 1)

def p_rule2(p):
    ''' rule : TUPLE_NONTERMINAL ':' alternatives
    '''
    gen_alternatives(p[1], p[3], wrapup_tuple)

def p_opt_word(p):
    ''' word : sub_rule '?'
    '''
    rule_text, type, offset, prep_code, params = p[1]
    rule_name = ast.gensym('optional')
    p_fn_name_0, p_fn_name_n = \
      ast.gensym('p_optional'), ast.gensym('p_optional')
    output("""
        def $fn_name1(p):
            r''' $rule_name :
            '''
            p[0] = None

        def $fn_name2(p):
            r''' $rule_name : $production
            '''
            $prep_code
            p[0] = p[$offset]

        """,
        fn_name1 = p_fn_name_0,
        rule_name = rule_name,
        fn_name2 = p_fn_name_n,
        production = rule_text,
        prep_code = prep_code % {'offset': offset + 1} if prep_code else '',
        offset = offset + 1)
    p[0] = rule_name, type, 0, None, None

def p_one_or_more_word(p):
    ''' word : sub_rule '+'
    '''
    rule_text, type, offset, prep_code, params = p[1]
    rule_name = ast.gensym('one_or_more')
    p_fn_name_1, p_fn_name_n = \
      ast.gensym('p_one_or_more'), ast.gensym('p_one_or_more')
    prep = prep_code % {'offset': offset + 2} if prep_code else ''
    output("""
        def $fn_name1(p):
            r''' $rule_name : $production
            '''
            $prep_code
            p[0] = (p[$offset1],)

        def $fn_name2(p):
            r''' $rule_name : $rule_name $production
            '''
            $prep_code
            p[0] = p[1] + (p[$offset2],)

        """,
        fn_name1 = p_fn_name_1,
        rule_name = rule_name,
        production = rule_text,
        prep_code = prep,
        offset1 = offset + 1,
        fn_name2 = p_fn_name_n,
        offset2 = offset + 2)
    p[0] = rule_name, 'tuple', 0, None, None

def p_zero_or_more_word(p):
    ''' word : sub_rule '*'
    '''
    rule_text, type, offset, prep_code, params = p[1]
    rule_name = ast.gensym('zero_or_more')
    p_fn_name_0, p_fn_name_n = \
      ast.gensym('p_zero_or_more'), ast.gensym('p_zero_or_more')
    output("""
        def $fn_name1(p):
            r''' $rule_name :
            '''
            p[0] = ()

        def $fn_name2(p):
            r''' $rule_name : $rule_name $production
            '''
            $prep_code
            p[0] = p[1] + (p[$offset],)

        """,
        fn_name1 = p_fn_name_0,
        rule_name = rule_name,
        fn_name2 = p_fn_name_n,
        production = rule_text,
        prep_code = prep_code % {'offset': offset + 2} if prep_code else '',
        offset = offset + 2)
    p[0] = rule_name, 'tuple', 0, None, None

def p_word_ellipsis(p):
    ''' word : sub_rule ELLIPSIS
    '''
    rule_text, type, offset, prep_code, params = p[1]
    rule_name = ast.gensym('ellipsis')
    p_fn_name_0, p_fn_name_n = \
      ast.gensym('p_ellipsis'), ast.gensym('p_ellipsis')
    output("""
        def $fn_name1(p):
            r''' $rule_name :
            '''
            p[0] = ()

        def $fn_name2(p):
            r''' $rule_name : $rule_name $production
            '''
            $prep_code
            p[0] = p[1] + (p[$offset],)

        """,
        fn_name1 = p_fn_name_0,
        rule_name = rule_name,
        fn_name2 = p_fn_name_n,
        production = rule_text,
        prep_code = prep_code % {'offset': offset + 2} if prep_code else '',
        offset = offset + 2)
    p[0] = rule_name, 'ellipsis', 0, None, None

def p_parameterized_word(p):
    ''' parameterized_word : simple_word param_list
    '''
    rule_text, type, offset, prep_code, params = p[1]
    if params:
        scanner_init.syntaxerror("duplicate initialization parameters")
    param_list = p[2]
    p[0] = rule_text, 'fn_word', offset, prep_code, param_list

def p_sub_rule(p):
    ''' sub_rule : simple_word AS_TOK NONTERMINAL
    '''
    rule_text, type, offset, prep_code, params = p[1]
    if prep_code:
        prep_code += '\n    '
    else:
        prep_code = ''
    p[0] = rule_text, type, offset, \
           prep_code + "p[%(offset)d].expect = '" + p[3] + "'", \
           params

def p_sub_rule2(p):
    ''' sub_rule : '{' alternatives '}'
    '''
    rule_name = ast.gensym('sub_rule')
    gen_alternatives(rule_name, p[2], normal_wrapup)
    p[0] = rule_name, 'single_arg', 0, None, None

def p_token_ignore(p):
    ''' simple_word : TOKEN_IGNORE
    '''
    global Tokens_used
    Tokens_used.add(p[1])
    p[0] = p[1], 'ignore', 0, None, None

def p_char_token(p):
    ''' simple_word : CHAR_TOKEN
    '''
    p[0] = p[1], 'ignore', 0, None, None

def p_token(p):
    ''' simple_word : TOKEN
    '''
    global Tokens_used
    Tokens_used.add(p[1])
    p[0] = p[1], 'single_arg', 0, None, None

def p_nonterminal(p):
    ''' simple_word : NONTERMINAL
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
    ''' parameter : NONTERMINAL PYTHON_CODE
    '''
    p[0] = (p[1], p[2])

def p_error(t):
    if t is None:
        raise SyntaxError("invalid syntax", scanner_init.syntaxerror_params())
    else:
        raise SyntaxError("invalid syntax", scanner_init.syntaxerror_params(t))

def output(str, **kws):
    sys.stdout.write(string.Template(strip_indent(str)).substitute(kws))

def strip_indent(str):
    r'''Strip initial indent off of all lines in str.

    >>> strip_indent('    hi\n    mom\n        indented\n')
    'hi\nmom\n    indented\n'
    >>> strip_indent('\n    hi\n    mom\n        indented\n')
    'hi\nmom\n    indented\n'
    '''
    assert '\t' not in str, "tabs not allowed in output strings"
    str = str.replace('\r', '')
    if str[0] == '\n': str = str[1:]
    stripped = str.lstrip(' ')
    indent = len(str) - len(stripped)
    return stripped.replace('\n' + ' ' * indent, '\n')

def init():
    global Tokens_used
    Tokens_used = set()
