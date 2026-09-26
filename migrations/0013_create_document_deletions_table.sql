create table if not exists public.document_deletions (
  document_id uuid primary key,
  participant_id uuid not null references public.participants (id),
  s3_key text not null,
  created_at timestamptz not null default now()
);
