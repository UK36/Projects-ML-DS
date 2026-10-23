-- SnapClass database schema (inferred from the code in src/database/db.py)
-- Run in: Supabase Dashboard -> SQL Editor -> New query -> Run

create table if not exists teachers (
  teacher_id  bigint generated always as identity primary key,
  username    text unique not null,
  password    text not null,            -- bcrypt hash
  name        text not null,
  created_at  timestamptz default now()
);

create table if not exists students (
  student_id       bigint generated always as identity primary key,
  name             text not null,
  face_embedding   jsonb,               -- 128-d dlib vector
  voice_embedding  jsonb,               -- 256-d resemblyzer vector (optional)
  created_at       timestamptz default now()
);

create table if not exists subjects (
  subject_id    bigint generated always as identity primary key,
  subject_code  text unique not null,
  name          text not null,
  section       text not null,
  teacher_id    bigint not null references teachers(teacher_id) on delete cascade,
  created_at    timestamptz default now()
);

create table if not exists subject_students (
  student_id  bigint not null references students(student_id) on delete cascade,
  subject_id  bigint not null references subjects(subject_id) on delete cascade,
  primary key (student_id, subject_id)
);

create table if not exists attendance_logs (
  log_id      bigint generated always as identity primary key,
  student_id  bigint not null references students(student_id) on delete cascade,
  subject_id  bigint not null references subjects(subject_id) on delete cascade,
  timestamp   timestamp not null,
  is_present  boolean not null default false
);

create index if not exists idx_logs_subject on attendance_logs(subject_id);
create index if not exists idx_logs_student on attendance_logs(student_id);
