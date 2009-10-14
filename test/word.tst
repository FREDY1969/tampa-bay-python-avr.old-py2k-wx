# word.tst

>>> from xml.etree import ElementTree
>>> from ucc.word import word, xml_access

>>> root = ElementTree.fromstring('''
... <word>
...     <name>output_pin</name>
...     <label>Output pin</label>
...     <kind>declaration</kind>
...     <defining>True</defining>
...     <questions>
...         <question>
...             <name>q1</name>
...             <label>Q1</label>
...             <type>int</type>
...             <validation>
...                 <validator type="range" minvalue="1" maxvalue="10" />
...             </validation>
...         </question>
...     </questions>
...     <answers>
...         <answer name="q5" type="int" value="123" />
...         <answer name="q6" type="string" value="Hi Mom!" />
...     </answers>
... </word>
... ''')
>>> w = word.from_xml(root)
>>> w
<word output_pin>
>>> w.name
'output_pin'
>>> w.label
'Output pin'
>>> w.defining
True
>>> w.kind
'declaration'
>>> w.questions
[<q_int q1>]
>>> w.questions[0].validation
[<range 1-10>]
>>> w.get_answer('q5')
<ans_int q5='123'>
>>> w.get_answer('q6')
<ans_string q6='Hi Mom!'>

>>> root = w.to_xml()
>>> xml_access.indent(root)
>>> print ElementTree.tostring(root)
<word>
    <name>output_pin</name>
    <label>Output pin</label>
    <kind>declaration</kind>
    <defining>True</defining>
    <answers>
        <answer name="q5" repeated="False" type="int" value="123" />
        <answer name="q6" repeated="False" type="string" value="Hi Mom!" />
    </answers>
    <questions>
        <question>
            <name>q1</name>
            <label>Q1</label>
            <type>int</type>
            <validation>
                <validator maxvalue="10" minvalue="1" type="range" />
            </validation>
        </question>
    </questions>
</word>
<BLANKLINE>

