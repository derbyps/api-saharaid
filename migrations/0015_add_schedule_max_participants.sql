-- MySQL. Capacity shown as an indicator only (not enforced); existing rows stay NULL.
alter table schedule
  add column max_participants int null after location;
