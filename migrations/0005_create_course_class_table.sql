create table if not exists public.course_class_type (
  id uuid primary key default gen_random_uuid(),
  sanity_id text not null unique,
  title text not null check (btrim(title) <> ''),
  synced_at timestamptz not null default now()
);
