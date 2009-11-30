-- ucc.ddl

-- The schema for the ast database.

---------------------------------------------------------------------------
-- These are the tables populated by the parse_file method.
---------------------------------------------------------------------------
create table symbol_table (
    id integer not null primary key,
    context integer references symbol_table(id),
    label varchar(255) not null collate nocase,
    kind varchar(255) not null,
        -- e.g.:
           -- 'function'
           -- 'task'
           -- 'const'
           -- 'var'
           -- 'parameter' -- int1 is parameter number
           -- 'label'
           -- 'placeholder'
    source_filename varchar(4096),      -- full path to source file
    type_id int references type(id),
    int1 int,
    side_effects bool default 0,        -- only for functions/tasks
    suspends bool default 0,            -- only for functions/tasks
    unique (label, context)
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

create table ast (
    -- The Abstract Syntax Tree (AST).  See AbstractSyntaxTree page in google
    -- code project wiki.

    id integer not null primary key,
    word_symbol_id int not null references symbol_table(id),

    -- For macro expansions:
    --id_replaced int unique references ast(id),
    --root_id_replaced int references ast(id),
    --replacement_depth int,

    kind varchar(255),                         -- type of ast node
       -- possible values are:
          -- 'approx': int1 = number_as_integer, int2 = binary_pt
             -- actual number == int1 * 2^int2
          -- 'int': int1 = integer
          -- 'ratio': int1 = numerator, int2 = denominator
          -- 'string': str1 = string
          -- 'call': first arg = fn
          -- 'word': label = word label, symbol_id = symbol_id of word
          -- 'ioreg': label = ioreg name (e.g., 'io.portd')
          -- 'ioreg-bit': label = ioreg name (e.g., 'io.portd'), int1 = bit#
          -- 'no-op':
          -- 'label': label = label
          -- 'jump': label = target
          -- 'if-false': label = jump-false target, first arg is condition
          -- 'if-true': label = jump-true target, first arg is condition
          -- 'series': args are statements to splice in
          -- 'None': line, column info not set

    label varchar(255),                        -- word label
    symbol_id int references symbol_table(id),
    int1 int,
    int2 int,
    str1 varchar(2000),
    str2 varchar(2000),                        -- not used, but leaving it here
                                               -- for the moment...

    expect varchar(255),                       -- what's expected by the parent
       -- possible values are:
          -- 'statement'
          -- 'condition'
          -- 'value' (rvalue)
          -- 'lvalue'
          -- 'producer'
          -- 'start_stop'

    type_id int references type(id),

    -- ast argument nodes are linked to their parent nodes:
    parent_node int references ast(id),        -- null for top-level
    parent_arg_num int,
    arg_order int,                             -- for list arguments, else 0

    -- for nodes generated by the parser:
    line_start int,
    column_start int,
    line_end int,
    column_end int,

    --unique (root_id_replaced, replacement_depth),
    unique (parent_node, parent_arg_num, arg_order)
);

create index word_index on ast (symbol_id, kind, expect);

create index word_body_index on ast (word_symbol_id,
                                     parent_node, parent_arg_num, arg_order);


---------------------------------------------------------------------------
-- Needed to construct the next two tables
---------------------------------------------------------------------------
create table fn_calls (
    -- who calls who
    caller_id int not null references symbol_table(id),
    called_id int not null references symbol_table(id),
    primary key (caller_id, called_id)
);

---------------------------------------------------------------------------
-- Needed to generate the intermediate code
---------------------------------------------------------------------------
create table fn_global_var_uses (
    -- the global variables used by a function (directly or indirectly)
    fn_id int not null references symbol_table(id),
    var_id int not null references symbol_table(id),
    sets bool not null,
    depth int not null default 0,
    primary key (fn_id, var_id, sets)
);

---------------------------------------------------------------------------
-- ucc.database.crud.gensym stores info here.
--
-- Nobody else knows about this...
---------------------------------------------------------------------------
create table gensym_indexes (
    prefix varchar(255) not null,
    last_used_index int not null
);


---------------------------------------------------------------------------
-- These are the tables for the intermediate code.
---------------------------------------------------------------------------
create table blocks (
    id integer not null primary key,
    name varchar(255) not null unique,

    last_triple_id int references triples(id),
    next varchar(255) references blocks(name),
    next_conditional varchar(255) references blocks(name)
);

create table block_successors (
    predecessor int not null references blocks(id),
    successor int not null references blocks(id)
);

create index block_successors_predecessor_index
    on block_successors (predecessor);

create index block_successors_successor_index on block_successors (successor);

create table triples (
    id integer not null primary key,
    block_id int not null references blocks(id),
    operator varchar(255) not null,
       -- special values:
       --   'input'            -- string is port name
       --   'input-bit'        -- string is port name, int_1 is bit#
       --   'output'           -- string is port name, int_1 is triples id
       --   'output-bit-set'   -- string is port name, int_1 is bit#
       --   'output-bit-clear' -- string is port name, int_1 is bit#
       --   'global_addr'      -- int_1 is symbol_table id
       --   'global'           -- int_1 is symbol_table id
       --   'local_addr'       -- int_1 is symbol_table id
       --   'local'            -- int_1 is symbol_table id
       --   'int'              -- int_1
       --   'ratio'            -- int_1 is numerator, int_2 is denominator
       --   'approx'           -- int_1 * 2**int_2
       --   'param'            -- int_1 is which param, int_2 is triples id
       --   'call_direct'      -- int_1 is symbol_table id
       --   'call_indirect'    -- int_1 is triples id
       --   'return'           -- int_1 is optional triples id
       --   'if_false'         -- int_1 is triples id to cond, string is label
       --   'if_true'          -- int_1 is triples id to cond, string is label
       -- else operator applies to int_1 and int_2 as triples ids
    int1 int,
    int2 int,
    string varchar(32768),
    line_start int,
    column_start int,
    line_end int,
    column_end int
);

-- also serves as labels for the triples
create table gens (
    block_id int not null references blocks(id),
    symbol_id int not null references symbol_table(id),
    triple_id int not null references triples(id)
);

create table triple_order_constraints (
    predecessor int not null references triples(id),
    successor int not null references triples(id)
);

create table kills (
    block_id int not null references blocks(id),
    symbol_id int not null references symbol_table(id),
    unique (block_id, symbol_id)
);

create table ins (
    block_id int not null references blocks(id),
    symbol_id int not null references symbol_table(id),
    triple_id int not null references triples(id),
    unique (block_id, symbol_id, triple_id)
);

create table outs (
    block_id int not null references blocks(id),
    symbol_id int not null references symbol_table(id),
    triple_id int not null references triples(id),
    unique (block_id, symbol_id, triple_id)
);


---------------------------------------------------------------------------
-- The tables the hold the assembler sources.
--
-- These are broken out by blocks to facilitate the assembler playing games
-- with the block orders to maximize the use of smaller jmp and call insts.
---------------------------------------------------------------------------
create table assembler_words (
    id integer not null primary key,
    section varchar(255) not null,
        -- 'code'
        -- 'data'
        -- 'bss'
        -- 'eeprom' (this probably gets broken out into several tables)
    label varchar(255) unique,
    address int,
    length int
);

create table assembler_code (
    id integer not null primary key,
    block_id int not null references assembler_blocks(id),
    inst_order int not null,
    label varchar(255) unique,
    opcode varchar(255),
        -- special opcodes:
           -- 'bytes', operand1 has data value in hex form (no initial '0x')
              -- or in 'string' or "string" form (with standard python escapes).
           -- 'int8', operand1 has data value in string form
              -- (may have '0x' prefix)
           -- 'int16', operand1 has data value in string form
              -- (may have '0x' prefix)
           -- 'int32', operand1 has data value in string form
              -- (may have '0x' prefix)
           -- 'zeroes', operand1 has data length in string form.
    operand1 varchar(255),
    operand2 varchar(255),
    length int not null,           -- in bytes
    clocks int,                    -- for machine instructions (code section)
    line_start int,
    column_start int,
    line_end int,
    column_end int,

    unique (block_id, inst_order)
);

