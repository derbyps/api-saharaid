create table if not exists public.schedule_participant (
  id uuid primary key default gen_random_uuid(),
  schedule_id uuid not null references public.schedule (id),
  participant_id uuid not null references public.participants (id),
  is_deleted boolean not null default false,
  created_by uuid not null references public.users (id),
  created_at timestamptz not null default now(),
  updated_at timestamptz,
  updated_by uuid references public.users (id),
  deleted_at timestamptz,
  deleted_by uuid references public.users (id)
);

create unique index schedule_participant_active_key
  on public.schedule_participant (schedule_id, participant_id)
  where not is_deleted;

create index schedule_participant_participant_idx
  on public.schedule_participant (participant_id, created_at desc)
  where not is_deleted;
