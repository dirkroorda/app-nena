from os.path import dirname, abspath

PROTOCOL = 'http://'
HOST = 'localhost'
PORT = {'kernel':18982,
        'web':8102}

OPTIONS = (
    ('showMicro', False, 'checkbox', 'subwordc', 'show char and morpheme boundaries'),
          )

ORG = 'CambridgeSemiticsLab'
REPO = 'nena_corpus'
CORPUS = 'Northeastern Neo-Aramaic Text Corpus'
VERSION = ''
RELATIVE = 'tf'

DOI_TEXT = '10.5281/zenodo.3250721'
DOI_URL = 'https://doi.org/10.5281/zenodo.3250721'

DOC_URL = f'https://github.com/{ORG}/{REPO}/blob/master/docs'
DOC_INTRO = 'features.md'
CHAR_URL = f'https://github.com/{ORG}/{REPO}/blob/master/docs/transcription.md'
CHAR_TEXT = 'NENA transcription script',

FEATURE_URL = f'{DOC_URL}/features.md#{{feature}}'

MODULE_SPECS = ()

ZIP = [REPO]

CONDENSE_TYPE = 'line'

NONE_VALUES = {None, 'NA', 'none', 'unknown'} # TO REVISIT 

STANDARD_FEATURES = '''

    dialect title utf8 trailer
    
'''.strip().split()

EXCLUDED_FEATURES = set()

NO_DESCEND_TYPES = {}

EXAMPLE_SECTION = (
    f'<code>Genesis 1:1</code> (use'
    f' <a href="https://github.com/{ORG}/{REPO}'
    f'/blob/master/tf/{VERSION}/book%40en.tf" target="_blank">'
    f'English book names</a>)'
)
EXAMPLE_SECTION_TEXT = 'Barwar, The Monk and the Angel, 1'

SECTION_SEP1 = ', '
SECTION_SEP2 = ', '

DEFAULT_CLS = 'trb'
DEFAULT_CLS_ORIG = 'ara'

FORMAT_CSS = {'orig':DEFAULT_CLS_ORIG,
              'trans':DEFAULT_CLS
             }

CLASS_NAMES = {'char':'micro',
               'morpheme':'micro',
               'word':'word',
               'subsentence':'macro',
               'prosa':'prosa',
               'sentence':'macro',
               'line':'line'}

# fonts are from 
FONT_NAME = 'CharisSIL-R'
FONT = 'CharisSIL-R.otf'
FONTW = 'CharisSIL-R.woff'

TEXT_FORMATS = {}

BROWSE_NAV_LEVEL = 2
BROWSE_CONTENT_PRETTY = False


def deliver():
    return (globals(), dirname(abspath(__file__)))