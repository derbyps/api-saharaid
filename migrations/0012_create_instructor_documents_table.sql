create table if not exists public.instructor_documents (
  id uuid primary key default gen_random_uuid(),
  instructor_id uuid not null unique references public.instructor (id),
  document_type text not null default 'curiculum_vitae'
    check (document_type = 'curiculum_vitae'),
  s3_key text not null unique,
  original_filename text not null,
  content_type text not null check (content_type = 'application/pdf'),
  file_size bigint not null check (file_size between 1 and 1048576),
  last_modified_at timestamptz not null,
  uploaded_at timestamptz not null default now(),
  created_by uuid not null references public.users (id)
);
