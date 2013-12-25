create table nodes (
    id integer primary key autoincrement,
    url text not null,
    is_visited text
);
create index url_index on nodes (url);

create table edges (
    tail_id integer not null,
    head_id integer not null,
    primary key (tail_id, head_id),
    foreign key(tail_id) references nodes(id),
    foreign key(head_id) references nodes(id)
);
