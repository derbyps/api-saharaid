create table if not exists public.instructor (
  id uuid primary key default gen_random_uuid(),
  name text not null check (btrim(name) <> ''),
  phone_number text not null,
  email text not null,
  course_theme_id uuid not null references public.course_theme (id),
  expertise text not null,
  is_deleted boolean not null default false,
  deleted_at timestamptz,
  deleted_by uuid references public.users (id),
  created_at timestamptz not null default now(),
  created_by uuid not null references public.users (id),
  updated_at timestamptz,
  updated_by uuid references public.users (id)
);

create index instructor_theme_idx
  on public.instructor (course_theme_id)
  where not is_deleted;

create index instructor_name_idx
  on public.instructor (lower(name))
  where not is_deleted;
