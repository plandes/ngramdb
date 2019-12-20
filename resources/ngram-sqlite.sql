-- meta=init_sections=ngram_create_tables,ngram_create_idx

-- name=ngram_create_idx
create index ngram_grams on ngram(grams);
create index ngram_yr on ngram(yr);
create index ngram_match_count on ngram(match_count);

-- name=ngram_create_tables
create table ngram (
    grams text not null,
    yr int not null,
    match_count int not null,
    page_count int not null,
    volume_count int not null);

-- name=ngram_insert_entry
insert into ngram (grams, yr, match_count, page_count, volume_count) values (?, ?, ?, ?, ?);

-- name=ngram_select_entries
select grams, yr, match_count, page_count, volume_count, rowid as id from ngram;

-- name=ngram_select_entry_by_id
select grams, yr, match_count, page_count, volume_count, rowid as id
       from ngram
       where id = ?;

-- name=ngram_select_entry_exists_by_id
select count(*) from ngram where grams = ?;

-- name=ngram_select_entry_count
select count(*) from ngram;

-- name=ngram_select_id
select rowid from ngram;

-- name=ngram_select_entry_by_ngram_id
select grams, yr, match_count, page_count, volume_count, rowid as id
       from ngram
       where grams = ?;

-- name=ngram_select_by_ngram
select grams, yr, match_count, page_count, volume_count, rowid as id
       from ngram
       where grams = ?;

-- name=ngram_select_aggregate_match_count
select sum(match_count) from ngram;

-- name=ngram_select_aggregate_match_count_by_grams
select sum(match_count) from ngram where grams = ?;

-- name=ngram_select_aggregate_match_count_by_year
select sum(match_count) from ngram where yr = ?;

-- name=ngram_select_aggregate_match_count_by_grams_by_year
select sum(match_count) from ngram where grams = ? and yr = ?;

-- name=ngram_select_aggregate_match_count_by_ngram_by_year
select sum(match_count)
       from ngram
       where grams = ? and yr > ?;

-- name=ngram_select_distinct_grams
select distinct grams from ngram;


-- create summary information for analysis of corpus (useful for unigrams)
-- name=ngram_agg_create_tables
create table ngram_agg (
    grams text not null,
    cnt int not null);

-- name=ngram_agg_create_idx
create index ngram_agg_grams on ngram_agg(grams);
create index ngram_agg_cnt on ngram_agg(cnt);

-- name=ngram_agg_insert
insert into ngram_agg (cnt, grams)
    select sum(match_count), grams
    from ngram
    group by grams;

-- name=ngram_agg_clean; the double quote token dominates the distribution
delete from ngram_agg where grams = '"';
delete from ngram_agg where grams = '.';

-- name=ngram_agg_high_freq_unigrams
select grams, cnt as freq, 1.0*cnt / (select sum(cnt) from ngram_agg) as population
       from ngram_agg
       order by cnt desc;

-- name=ngram_agg_top_dist
select na.grams, na.cnt,
       1.0 * na.cnt / (select cnt from ngram_agg as t order by t.cnt desc limit 1) as per
       from ngram_agg na
       order by cnt desc limit 100;
