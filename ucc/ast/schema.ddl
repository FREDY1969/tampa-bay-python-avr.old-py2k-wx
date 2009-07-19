-- schema.ddl

create table node (
    -- The Abstract Syntax Tree (AST).  See AbstractSyntaxTree page in google
    -- code project wiki.

    id integer not null primary key,

    -- For macro expansions:
    id_replaced int references node(id),
    root_id_replaced int references node(id),
    replacement_depth int,

    kind varchar(255),                         -- type of ast
    expect varchar(255),                       -- what's expected by the parent
    type_id int references type(id),

    word_id int,
    int1 int,
    int2 int,
    str varchar(2000),

    -- ast nodes are linked to their parent nodes:
    parent_node int references node(id),
    parent_arg_num int,
    arg_position int

    -- for nodes generated by the parser:
    line_start int,
    column_start int,
    line_end int,
    column_end int
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