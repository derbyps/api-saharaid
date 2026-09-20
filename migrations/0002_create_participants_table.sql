create table if not exists public.participants (
  id uuid primary key default gen_random_uuid(),
  name text not null check (btrim(name) <> ''),
  identity_number text not null,
  gender text not null,
  phone_number text not null check (btrim(phone_number) <> ''),
  email text not null,
  date_of_birth date not null,
  religion text not null,
  address text not null,
  job_position text not null,
  job_company text not null,
  education text not null,
  cr_number text not null,
  tax_number text not null,
  serial_number bigint generated always as identity unique,
  is_deleted boolean not null default false,
  deleted_at timestamptz,
  deleted_by uuid references public.users (id),
  created_at timestamptz not null default now(),
  created_by uuid not null references public.users (id),
  updated_at timestamptz,
  updated_by uuid references public.users (id)
);

create unique index participants_active_name_key
  on public.participants (lower(btrim(name)))
  where not is_deleted;

create unique index participants_active_phone_key
  on public.participants (btrim(phone_number))
  where not is_deleted;

create index participants_created_at_idx
  on public.participants (created_at desc)
  where not is_deleted;
