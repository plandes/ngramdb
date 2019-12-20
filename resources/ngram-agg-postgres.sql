---- To speed things up, create an aggregate table of the ngrams since we're
---- only interested in calculating probabilities and not given usage over
---- certain years.

-- meta=init_sections=ngram_agg_create_tables,ngram_create_idx

-- create summary information for analysis of corpus
-- name=ngram_agg_create_tables
create table ngram_agg (
    uid bigserial primary key,
    grams text not null,
    match_count int not null);

-- name=ngram_agg_create_idx
create index ngram_agg_grams on ngram_agg(grams);
create index ngram_agg_match_count on ngram_agg(match_count);

-- name=ngram_agg_insert
insert into ngram_agg (match_count, grams)
    select sum(match_count), grams
    from ngram
    group by grams;

--alter table ngram_agg  alter column old_uid type int;
create index ngram_agg_gram_gin_trgm_idx on ngram_agg using gin (grams gin_trgm_ops);

-- name=ngram_agg_select_aggregate_match_count_by_grams
select sum(match_count) from ngram_agg where grams like %s;

-- name=ngram_agg_select_aggregate_match_count
select sum(match_count) from ngram_agg;

-- name=ngram_agg_select_entry_exists_by_id
select count(*) from ngram_agg where grams like %s;

-- name=ngram_agg_select_distinct_grams
select distinct grams from ngram;

-- name=ngram_agg_top_n_count
select grams, match_count as count
    from ngram_agg
    order by count desc
    limit 1 offset %s;


---- exp
-- name=ngram_agg_high_freq_unigrams
select grams, match_count as freq, 1.0*match_count / (select sum(match_count) from ngram_agg) as population
       from ngram_agg
       order by match_count desc;

-- name=ngram_agg_top_dist
select na.grams, na.match_count,
       1.0 * na.match_count / (select match_count from ngram_agg as t order by t.match_count desc limit 1) as per
       from ngram_agg na
       order by match_count desc limit 100;
