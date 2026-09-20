create table if not exists public.course (
  id uuid primary key default gen_random_uuid(),
  sanity_id text not null unique,
  title text not null check (btrim(title) <> ''),
  course_type_id uuid not null references public.course_type (id),
  course_class_type_id uuid not null references public.course_class_type (id),
  course_certificate_validity_id uuid not null references public.course_certificate_validity (id),
  asset_status text not null default 'pending'
    check (asset_status in ('pending', 'ready')),
  is_deleted boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz,
  deleted_at timestamptz
);

create table if not exists public.course_course_theme (
  course_id uuid not null references public.course (id) on delete cascade,
  course_theme_id uuid not null references public.course_theme (id),
  primary key (course_id, course_theme_id)
);

create index course_course_theme_theme_idx
  on public.course_course_theme (course_theme_id, course_id);

create index course_title_idx
  on public.course (lower(title))
  where not is_deleted;
