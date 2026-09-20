create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  participant_id uuid not null references public.participants (id),
  document_type text not null check (document_type in (
    'passport_photo',
    'identity_card',
    'tax_number',
    'curiculum_vitae',
    'employment_certificate',
    'medical_certificate',
    'integrity_pact',
    'degree_certificate'
  )),
  s3_key text not null unique,
  original_filename text not null,
  content_type text not null,
  file_size bigint not null check (file_size between 1 and 1048576),
  last_modified_at timestamptz not null,
  uploaded_at timestamptz not null default now(),
  created_by uuid not null references public.users (id),

  constraint documents_content_type_check check (
    (document_type = 'passport_photo' and content_type in ('image/jpeg', 'image/png'))
    or
    (document_type = 'curiculum_vitae' and content_type = 'application/pdf')
    or
    (document_type not in ('passport_photo', 'curiculum_vitae')
      and content_type in ('image/jpeg', 'image/png', 'application/pdf'))
  ),
  constraint documents_participant_type_key unique (participant_id, document_type)
);
