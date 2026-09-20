create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  name text not null check (btrim(name) <> ''),
  email text not null check (btrim(email) <> ''),
  created_at timestamptz not null default now()
);

create unique index users_email_key on public.users (lower(btrim(email)));
