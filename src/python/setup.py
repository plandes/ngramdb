from pathlib import Path
from zensols.pybuild import SetupUtil

SetupUtil(
    setup_path=Path(__file__).parent.absolute(),
    name="zensols.ngramdb",
    package_names=['zensols', 'resources'],
    package_data={'': ['*.conf', '*.sql']},
    description='Creates an SQLite database ngrams.',
    user='plandes',
    project='ngramdb',
    keywords=['nlp'],
).setup()
