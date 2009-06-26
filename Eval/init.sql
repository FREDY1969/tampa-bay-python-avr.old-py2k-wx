-- init.sql

-- words:
insert into word (id, name, kind, defining_word)
values (1, 'defining', 1, 1);

insert into word (id, name, kind, defining_word)
values (2, 'const', 1, 1);

insert into word (id, name, kind, defining_word)
values (3, 'var', 1, 1);

insert into word (id, name, kind, defining_word, file_suffix)
values (4, 'to', 1, 1, 'cpl');

insert into word (id, name, kind, defining_word, file_suffix)
values (5, 'task', 1, 1, 'cpl');


-- answers:

-- for 'defining':

-- answers to: 'question':

    -- 'question'
    insert into answer (id, question_id, word_id, answer)
    values (1, 1, 1, 'question');

        -- subquestions:

        -- 'subquestion'
        insert into answer (id, parent, position, question_id, word_id, answer)
        values (2, 1, 2, 2, 1, '1');

        -- 'repeatable'
        insert into answer (id, parent, position, question_id, word_id, answer)
        values (3, 1, 1, 2, 1, 'repeatable');

-- answers to: 'repeatable':

    -- 'question':
    insert into answer (id, parent, question_id, word_id, answer)
    values (4, 1, 3, 1, 'true');

    -- 'repeatable':
    insert into answer (id, parent, question_id, word_id, answer)
    values (5, 3, 3, 1, 'false');

    -- 'subquestion':
    insert into answer (id, parent, question_id, word_id, answer)
    values (6, 2, 3, 1, 'true');


-- for 'const':
insert into answer (id, question_id, word_id, answer)
values (8, 1, 2, 'value');
insert into answer (id, question_id, parent, word_id, answer)
values (9, 3, 8, 2, 'false');


-- for 'var':
insert into answer (id, question_id, word_id, answer)
values (10, 1, 3, 'initial value');
insert into answer (id, question_id, parent, word_id, answer)
values (11, 3, 10, 3, 'false');
