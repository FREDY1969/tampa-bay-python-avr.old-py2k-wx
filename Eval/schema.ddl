-- schema.ddl

create table word (
    -- This is where the action is!  See Word page in google code project wiki.

    id int not null primary key,
    name varchar(255) not null,
    kind int not null references word(id),
    defining_word bool not null default false,
    file_suffix varchar(10),    -- only for defining words, null if no file req
    unique (name)
);


create table answer (
    -- Answers go here.

    id int not null primary key,
    question_id int not null references answer(id),
    parent int references answer(id),
    position int not null default 1,
    word_id int not null references word(id),

    answer varchar(2000) not null
);

