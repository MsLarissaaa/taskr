drop table if exists tasks;
create table tasks (
  id integer primary key autoincrement,
  description text not null,
  complete boolean not null
);