create table if not exists public.schedule_batch_counter (
  batch_year smallint primary key,
  last_value bigint not null check (last_value > 0)
);

create table if not exists public.schedule (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.course (id),
  class text not null check (btrim(class) <> ''),
  course_mode text not null check (course_mode in ('online', 'offline')),
  start_date date not null,
  end_date date not null,
  location text not null check (btrim(location) <> ''),
  batch bigint not null,
  batch_year smallint generated always as
    (extract(year from start_date)::smallint) stored,
  is_deleted boolean not null default false,
  created_by uuid not null references public.users (id),
  created_at timestamptz not null default now(),
  updated_at timestamptz,
  updated_by uuid references public.users (id),
  deleted_at timestamptz,
  deleted_by uuid references public.users (id),

  constraint schedule_date_range_check check (end_date >= start_date),
  constraint schedule_year_batch_key unique (batch_year, batch)
);

create or replace function public.assign_schedule_batch()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  target_year smallint := extract(year from new.start_date)::smallint;
begin
  if tg_op = 'UPDATE'
    and target_year = extract(year from old.start_date)::smallint then
    new.batch := old.batch;
    return new;
  end if;

  insert into public.schedule_batch_counter (batch_year, last_value)
  values (target_year, 1)
  on conflict (batch_year) do update
    set last_value = public.schedule_batch_counter.last_value + 1
  returning last_value into new.batch;

  return new;
end;
$$;

create trigger schedule_assign_batch
before insert or update of start_date on public.schedule
for each row execute function public.assign_schedule_batch();

create index schedule_start_date_idx
  on public.schedule (start_date desc)
  where not is_deleted;

create index schedule_course_idx
  on public.schedule (course_id)
  where not is_deleted;
