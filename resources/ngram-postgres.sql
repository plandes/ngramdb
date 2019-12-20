-- meta=init_sections=ngram_create_tables

-- name=ngram_create_tables
create table ngram (
    uid bigserial primary key,
    grams text not null,
    yr int not null,
    match_count int not null,
    page_count int not null,
    volume_count int not null);

-- name=ngram_create_idx; add after load to speed things up
create index ngram_grams on ngram (grams);
create index ngram_yr on ngram (yr);
create index ngram_match_count on ngram (match_count);

-- name=ngram_insert_entry
insert into ngram (grams, yr, match_count, page_count, volume_count) values (%s, %s, %s, %s, %s);

-- name=ngram_select_entries
select grams, yr, match_count, page_count, volume_count, uid as id from ngram;

-- name=ngram_select_entry_by_id
select grams, yr, match_count, page_count, volume_count, uid as id
       from ngram
       where id = %s;

-- name=ngram_select_entry_exists_by_id
select count(*) from ngram where grams = %s;

-- name=ngram_select_entry_count
select count(*) from ngram;

-- name=ngram_select_id
select uid from ngram;

-- name=ngram_select_entry_by_ngram_id
select grams, yr, match_count, page_count, volume_count, uid as id
       from ngram
       where grams = %s;

-- name=ngram_select_by_ngram
select grams, yr, match_count, page_count, volume_count, uid as id
       from ngram
       where grams = %s;

-- name=ngram_select_aggregate_match_count
select sum(match_count) from ngram;

-- name=ngram_select_aggregate_match_count_by_grams
select sum(match_count) from ngram where grams = %s;

-- name=ngram_select_aggregate_match_count_by_year
select sum(match_count) from ngram where yr = %s;

-- name=ngram_select_aggregate_match_count_by_grams_by_year
select sum(match_count) from ngram where grams = %s and yr = %s;

-- name=ngram_select_aggregate_match_count_by_ngram_by_year
select sum(match_count)
       from ngram
       where grams = %s and yr > %s;

-- name=ngram_select_distinct_grams
select distinct grams from ngram;
