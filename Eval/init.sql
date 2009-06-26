-- init.sql

-- words:
insert into word (id, name, kind, defining_word)
values (1, 'defining', 1, 1);

insert into word (id, name, kind, defining_word)
values (2, 'const', 1, 1);

insert into word (id, name, kind, defining_word)
values (3, 'var', 1, 1);

insert into word (id, name, kind, defining_word)
values (4, 'to', 1, 1);

insert into word (id, name, kind, defining_word)
values (5, 'task', 1, 1);


-- answers:

-- for 'defining':

-- answers to: 'question':

    -- 'question'
    insert into answer (id, position, question_id, word_id, answer)
    values (1, 1, 1, 1, 'question');

        -- subquestions:

        -- 'subquestion'
        insert into answer (id, parent, position, question_id, word_id, answer)
        values (2, 1, 2, 2, 1, '1');

        -- 'repeatable'
        insert into answer (id, parent, position, question_id, word_id, answer)
        values (3, 1, 1, 2, 1, 'repeatable');

    -- 'filename suffix'
    insert into answer (id, position, question_id, word_id, answer)
    values (4, 2, 1, 1, 'filename suffix');

-- answers to: 'repeatable':

    -- 'question':
    insert into answer (id, parent, question_id, word_id, answer)
    values (5, 1, 3, 1, 'True');

    -- 'repeatable':
    insert into answer (id, parent, question_id, word_id, answer)
    values (6, 3, 3, 1, 'False');

    -- 'subquestion':
    insert into answer (id, parent, question_id, word_id, answer)
    values (7, 2, 3, 1, 'True');

    -- 'filename suffix':
    insert into answer (id, parent, question_id, word_id, answer)
    values (8, 4, 3, 1, 'False');

-- answer to: 'filename suffix':

    -- 'filename suffix':
    insert into answer (id, question_id, word_id, answer)
    values (9, 4, 1, '');


-- for 'const':
insert into answer (id, question_id, word_id, answer)
values (10, 1, 2, 'value');             -- 'question'
    insert into answer (id, question_id, parent, word_id, answer)
    values (11, 3, 10, 2, 'False');     -- 'repeatable'
insert into answer (id, question_id, word_id, answer)
values (12, 4, 2, '');                  -- 'filename suffix'


-- for 'var':
insert into answer (id, question_id, word_id, answer)
values (13, 1, 3, 'initial value');     -- 'question'
    insert into answer (id, question_id, parent, word_id, answer)
    values (14, 3, 13, 3, 'False');     -- 'repeatable'
insert into answer (id, question_id, word_id, answer)
values (15, 4, 3, '');                  -- 'filename suffix'


-- for 'to':
insert into answer (id, question_id, word_id, answer)
values (16, 4, 4, 'cpl');               -- 'filename suffix'


-- for 'task':
insert into answer (id, question_id, word_id, answer)
values (17, 4, 5, 'cpl');               -- 'filename suffix'
