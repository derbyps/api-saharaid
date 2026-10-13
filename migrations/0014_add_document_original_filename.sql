-- MySQL. Stores the user's original file name; existing rows stay NULL (not backfilled).
alter table document
  add column original_filename varchar(255) null after content_type;
