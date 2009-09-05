# answers.tst testing

>>> from xml.etree import ElementTree
>>> from ucc.word import answers, xml_access

>>> root = ElementTree.fromstring('''
... <answers>
...     <answer name="q1" type="bool" value="True" />
...     <answer name="q2" type="number" value="123" />
...     <answer name="q3" type="int" value="123" repeated="True" />
...     <answer name="q3" type="int" value="124" repeated="True" />
...     <answer name="q4" type="rational" value="1.3/4" />
...     <answer name="q5" type="real" value="1.23" />
...     <answer name="q6" type="string" value="Hi Mom!" />
...     <answer name="q7" repeated="False" />
...     <answer name="q8" repeated="True" />
... </answers>
... ''')
>>> a_dict = answers.from_xml(root)
>>> keys = sorted(a_dict.keys())
>>> keys
['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8']
>>> for k in keys: print a_dict[k]
<ans_bool q1='True'>
<ans_number q2='123'>
[<ans_int q3='123'>, <ans_int q3='124'>]
<ans_rational q4='1.3/4'>
<ans_real q5='1.23'>
<ans_string q6='Hi Mom!'>
None
[]

>>> root = ElementTree.Element('answers')
>>> answers.add_xml_answers(root, a_dict)
>>> xml_access.indent(root)
>>> print ElementTree.tostring(root)
<answers>
    <answer name="q1" repeated="False" type="bool" value="True" />
    <answer name="q2" repeated="False" type="number" value="123" />
    <answer name="q3" repeated="True" type="int" value="123" />
    <answer name="q3" repeated="True" type="int" value="124" />
    <answer name="q4" repeated="False" type="rational" value="1.3/4" />
    <answer name="q5" repeated="False" type="real" value="1.23" />
    <answer name="q6" repeated="False" type="string" value="Hi Mom!" />
    <answer name="q7" repeated="False" />
    <answer name="q8" repeated="True" />
</answers>
<BLANKLINE>

>>> root = ElementTree.fromstring('''
... <answers>
...     <answer name="q1" type="choice">
...         <options>
...             <option value="foo">
...                 <answers>
...                     <answer name="q6" type="string" value="Hi Mom!" />
...                 </answers>
...             </option>
...         </options>
...     </answer>
...     <answer name="q2" type="multichoice">
...         <options>
...             <option value="3">
...                 <answers>
...                     <answer name="q6" type="string" value="Hi Mom!" />
...                 </answers>
...             </option>
...             <option value="1" />
...         </options>
...     </answer>
...     <answers name="q3">
...         <answer name="q5" type="rational" value="1.3/4" />
...         <answer name="q4" type="real" value="1.23" />
...     </answers>
... </answers>
... ''')
>>> a_dict = answers.from_xml(root)
>>> keys = sorted(a_dict.keys())
>>> keys
['q1', 'q2', 'q3']
>>> for k in keys: print a_dict[k]
<ans_choice q1=foo->{'q6': <ans_string q6='Hi Mom!'>}>
<ans_multichoice for q2>
<ans_series for q3>

>>> q1 = a_dict['q1']
>>> q1.tag
'foo'
>>> q1.subanswers
{'q6': <ans_string q6='Hi Mom!'>}

>>> q2 = a_dict['q2']
>>> sorted(q2.answers.keys())
[1, 3]
>>> q2.answers[1]
>>> q2.answers[3]
{'q6': <ans_string q6='Hi Mom!'>}

>>> q3 = a_dict['q3']
>>> q3.q4
<ans_real q4='1.23'>
>>> q3.q5
<ans_rational q5='1.3/4'>

>>> root = ElementTree.Element('answers')
>>> answers.add_xml_answers(root, a_dict)
>>> xml_access.indent(root)
>>> print ElementTree.tostring(root)
<answers>
    <answer name="q1" repeated="False" type="choice">
        <options>
            <option value="foo">
                <answers>
                    <answer name="q6" repeated="False" type="string" value="Hi Mom!" />
                </answers>
            </option>
        </options>
    </answer>
    <answer name="q2" repeated="False" type="multichoice">
        <options>
            <option value="1" />
            <option value="3">
                <answers>
                    <answer name="q6" repeated="False" type="string" value="Hi Mom!" />
                </answers>
            </option>
        </options>
    </answer>
    <answers name="q3" repeated="False">
        <answer name="q4" repeated="False" type="real" value="1.23" />
        <answer name="q5" repeated="False" type="rational" value="1.3/4" />
    </answers>
</answers>
<BLANKLINE>

