# Create an SQLite database from the Google ngrams database.

[![PyPI][pypi-badge]][pypi-link]
[![Python 3.6][python36-badge]][python36-link]

Creates an SQLite database of the one million [n-gram] datasets from Google.
This code downloads the [n-gram data sets] corpus and then creates an [SQLite]
database file with the contents.  It also provides a simple API for [n-gram]
look ups.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
## Table of Contents

- [Installation](#installation)
    - [Data Size](#data-size)
- [Usage](#usage)
    - [Command Line](#command-line)
    - [Programmatic Interface](#programmatic-interface)
    - [Data Analysis with Pandas](#data-analysis-with-pandas)
- [Obtaining](#obtaining)
- [Changelog](#changelog)
- [License](#license)

<!-- markdown-toc end -->


## Installation

1. To make life easier, install [GNU Make].  If you do not, you'll need to
   follow the steps given in the [makefile](./makefile).
2. Download the 1 million [n-gram data sets]: `make download`.  This should
   take a few minutes with a good Internet connection.
3. Un-compress the load files: `make uncompress`.
4. Create and load the [SQLite] database from the downloaded corpus: `make
   load`.  Depending on the processor speed, this should take about an hour and
   creates a file in `data/eng-1gram.db` that takes 18G on disk.
5. Install from the command line either from source (`make install`) or from
   [pip](#obtaining).

If you want to use the program on the command line (as opposed to an API),
create a the following file in `~/.ngramdbrc` with the contents:
```ini
[default]
[ngram_db]
data_dir=${HOME}/path/to/eng-1gram.db
```

### Data Size

As mentioned, the [SQLite] database file take 18G on disk.  This is because it
keeps occurrences over several decades.  In many cases, older n-grams are not
needed and queries can take a while given the size of the data.  The data can
be minimized with the following SQL in any [SQLite] interface (i.e. MacOS has
`sqlite3` on the command line):
```sql
delete from ngram where yr < 1990;
```
In this example, all n-grams recorded from publications before the year 1990
are expunged.


## Usage

This project can be used either from the command line or as an API.


### Command Line

To use from the command line:
```bash
% ngramdb query -g the -y 2005
631362690 0.56880%
```
This gives the number of unigrams (assuming unigrams were built) found since
2005 and the percentage of that unigram to all words in the corpus.


### Programmatic Interface

As in the [installation](#installation) section, create the `~/.ngramdbrc`
configuration file.  Also note that the API is configured to easily work with
other Python projects that use the [zensols.actioncli] configuration API.

```python
from zensols.ngramdb import AppConfig, Query
conf = AppConfig.instance().app_config
query = Query(conf)
stash = query.stash
n_occurs = stash['The']
print(f'{n_occurs} {100 * n_occurs / len(stash):.5f}%')

=> 631362690 0.56880%
```


### Data Analysis with Pandas

The [stash access](#programmatic-interface) is nice for specific use cases
where a subset of the corpus counts are necessary.  However, the intention of
creating a selectable data format was to allow for data analysis as well.
Here's an example of how [Pandas] can be used directly against the created
[SQLite] file learn about the corpus:
```python
from zensols.actioncli.time import time
import pandas as pd
import sqlite3 as s

# "connect" to the SQLite database file
db = '/path/to/data/directory/eng-1gram.db'
conn = s.connect(db)

# create a dataframe with all entries on or after 1990
sql = 'select grams, match_count as cnt from ngram where yr >= 1990'
with time('{rc} rows read'):
    df = pd.read_sql_query(sql, conn)
    rc = len(df)
#=> 28150989 rows read finished in 60.8s

# create a data frame with a ngram text and number of match counts per row
with time('groupby of {rc} rows'):
    dfg = df.groupby(['grams'], as_index=False).agg({'cnt': 'sum'})
    rc = len(df)
#=> group of 28150989 rows finished in 7.6s

# get the number of counts on 'the'
dfg[dfg['grams'] == 'the']
#=>         grams        cnt
#=> 2819462   the  621594750

# all token occurrences
all_cnt = df['cnt'].sum()
all_cnt
#=> 13269089201

# calculate at the poulation of a few words
for word in 'the The . cat dog phone iPhone'.split():
	occ = dfg[dfg['grams'] == word].cnt.item()
	pop = occ / all_cnt
	print(f'word \'{word}\' found {occ} times, which is {pop * 100:.5f}% of the corpus')

#=> word 'the' found 621594750 times, which is 4.68453% of the corpus
#=> word 'The' found 77576794 times, which is 0.58464% of the corpus
#=> word '.' found 641792317 times, which is 4.83675% of the corpus
#=> word 'cat' found 247075 times, which is 0.00186% of the corpus
#=> word 'dog' found 453789 times, which is 0.00342% of the corpus
#=> word 'phone' found 522190 times, which is 0.00394% of the corpus
#=> word 'iPhone' found 178 times, which is 0.00000% of the corpus

with time('pickled data frame'):
    df.to_pickle('df.dat')
#=> pickled data frame finished in 8.0s

with time('write to csv'):
    df.to_csv('df.csv')
#=> write to csv finished in 44.3s

with time('read data from'):
    df = pd.read_pickle('df.dat')
#=> read data from finished in 2.4s
```


## Obtaining

The easist way to install the command line program is via the `pip` installer:
```bash
pip3 install zensols.ngramdb
```

Binaries are also available on [pypi].


## Changelog

An extensive changelog is available [here](CHANGELOG.md).


## License

Copyright (c) 2019 Paul Landes

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


<!-- links -->
[pypi]: https://pypi.org/project/zensols.ngramdb/
[pypi-link]: https://pypi.python.org/pypi/zensols.ngramdb
[pypi-badge]: https://img.shields.io/pypi/v/zensols.ngramdb.svg
[python36-link]: https://www.python.org/downloads/release/python-360
[python36-badge]: https://img.shields.io/badge/python-3.6-blue.svg

[n-gram data sets]: http://storage.googleapis.com/books/ngrams/books/datasetsv2.html
[n-gram]: https://en.wikipedia.org/wiki/N-gram
[GNU Make]: https://www.gnu.org/software/make/
[zensols.actioncli]: https://github.com/plandes/actioncli
[Pandas]: https://pandas.pydata.org
[SQLite]:https://www.sqlite.org/index.html
