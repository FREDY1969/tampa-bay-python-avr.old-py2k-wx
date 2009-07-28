-- schema.ddl

create table ast (
    -- The Abstract Syntax Tree (AST).  See AbstractSyntaxTree page in google
    -- code project wiki.

    id integer not null primary key,
    word_body_id int references ast(id),       -- NULL for the word_body itself

    -- For macro expansions:
    id_replaced int unique references ast(id),
    root_id_replaced int references ast(id),
    replacement_depth int,

    kind varchar(255),                         -- type of ast node
       -- possible values are:
          -- 'word_body': word = name of word, str1: path to source file
          -- 'approx': int1 = number_as_integer, int2 = binary_pt
             -- actual number == int1 * 2^int2
          -- 'int': int1 = integer
          -- 'ratio': int1 = numerator, int2 = denominator
          -- 'string': str1 = string
          -- 'fn_call': word = name of fn word
          -- all of the following are assembler nodes.  These all use the
             following optional columns:
              -- label
              -- word is the opcode
              -- str1 and str2 are the operands
              -- int1 is the length (in bytes)
              -- int2 is the number of clock cycles (for machine instructions
                 in flash)
             and the kinds are:
              -- 'flash'
              -- 'data'
              -- 'bss'
              -- 'eeprom'

    label varchar(255),                        -- assembler label
    word varchar(255) collate nocase,
    int1 int,
    int2 int,
    str1 varchar(2000),
    str2 varchar(2000),

    expect varchar(255),                       -- what's expected by the parent
    type_id int references type(id),

    -- ast argument nodes are linked to their parent nodes:
    parent_node int references ast(id),
    parent_arg_num int,
    arg_order int,                             -- for list arguments, else 0

    -- for nodes generated by the parser:
    line_start int,
    column_start int,
    line_end int,
    column_end int,

    unique (root_id_replaced, replacement_depth),
    unique (parent_node, parent_arg_num, arg_order)
);

create index word_index on ast (word, kind, expect);

create index word_body_index on ast (word_body_id,
                                     parent_node, parent_arg_num, arg_order);

create table gensym_indexes (
    prefix varchar(255) not null,
    last_used_index int not null
);

create table type (
    -- Describes what is known about a value at compile time.

    id integer not null primary key,
    kind varchar(255) not null,
    min_value int,
    max_value int,
    binary_pt int,
    precision int,
    element_type int references type(id)
);
