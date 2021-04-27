const configData = {
 "defs": {
  "org": "annotation",
  "repo": "app-nena",
  "name": "nena",
  "urls": {
   "cheatsheet": [
    "cheatsheet",
    "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions/Cheatsheet",
    "cheatsheet of regular expressions"
   ],
   "license": [
    "license",
    "https://mit-license.org",
    "MIT license"
   ],
   "corpus": [
    null,
    "https://nena.ames.cam.ac.uk",
    "North-Eastern Neo-Aramaic Data Project website"
   ],
   "corpus2": [
    null,
    "https://nena.ames.cam.ac.uk",
    "North-Eastern Neo-Aramaic Data Project website"
   ],
   "maker": [
    null,
    "https://dans.knaw.nl/en/front-page?set_language=en",
    "DANS = Data Archiving and Networked Services"
   ],
   "author": [
    "Dirk Roorda",
    "https://pure.knaw.nl/portal/en/persons/dirk-roorda",
    "author"
   ],
   "author2": [
    "Cody Kingham",
    "https://www.linkedin.com/in/cody-kingham-1135018a",
    "author (second)"
   ],
   "author3": [
    "Geoffrey Khan",
    "https://www.ames.cam.ac.uk/people/professor-geoffrey-khan",
    "author (second)"
   ],
   "tf": [
    null,
    "https://annotation.github.io/text-fabric/tf/",
    "Text-Fabric documentation website"
   ],
   "appdoc": [
    "about layered search",
    "https://annotation.github.io/text-fabric/tf/about/layeredsearch.html",
    "Powered by Text-Fabric data"
   ],
   "datadoc": [
    "data (feature) documentation",
    "https://github.com/CambridgeSemiticsLab/nena_tf/blob/master/docs/features.md",
    "Powered by Text-Fabric data"
   ],
   "data": [
    "based on text-fabric data version alpha",
    "https://github.com/CambridgeSemiticsLab/nena_tf/tree/master/tf/alpha",
    "Powered by Text-Fabric data"
   ],
   "source": [
    null,
    "https://github.com/annotation/app-nena",
    "source code in Github repository"
   ],
   "issue": [
    "Feature requests, bugs, feedback",
    "https://github.com/annotation/app-nena/issues",
    "report issues"
   ],
   "issue2": [
    "Report an issue",
    "https://github.com/annotation/app-nena/issues",
    "report issues"
   ],
   "package": [
    "download",
    [
     "https://annotation.github.io/app-nena/nena.zip"
    ],
    "zip file for offline use"
   ],
   "writing": [
    "alphabet",
    "https://annotation.github.io/text-fabric/tf/writing/neoaramaic.html",
    "characters and transliteration"
   ],
   "related": [
    "text-fabric nena",
    "https://nbviewer.jupyter.org/github/annotation/tutorials/tree/master/nena/start.ipynb",
    "using Text-Fabric on the same corpus"
   ]
  },
  "captions": {
   "title": "NENA phono search"
  },
  "description": "\n<p>Phonetic search interface for the <a id=\"corpus2link\" href=\"#\"></a>.</p>\n<p>This is a standalone app. You download it to your computer, and then it works without\nconnection to the internet.</p>\n<p>This web app is by:</p>\n<ul>\n    <li><a id=\"author3link\" href=\"#\"></a> (initiator)\n    <li><a id=\"author2link\" href=\"#\"></a> (corpus developer)\n    <li><a id=\"authorlink\" href=\"#\"></a> (software developer)\n</ul>\n    ",
  "appVersion": "v37@2021-04-27T06:59:39"
 },
 "containerType": "sentence",
 "simpleBase": false,
 "ntypes": [
  "word",
  "sentence",
  "line",
  "text"
 ],
 "ntypesinit": {
  "dialect": 539379,
  "text": 713308,
  "paragraph": 578369,
  "line": 575825,
  "sentence": 578719,
  "subsentence": 688811,
  "inton": 539381,
  "stress": 595045,
  "word": 713434,
  "letter": 1
 },
 "ntypessize": {
  "dialect": 2,
  "text": 126,
  "paragraph": 350,
  "line": 2544,
  "sentence": 16326,
  "subsentence": 24497,
  "inton": 36444,
  "stress": 93766,
  "word": 120151,
  "letter": 539378
 },
 "dtypeOf": {
  "sentence": "word",
  "line": "sentence",
  "text": "line"
 },
 "utypeOf": {
  "word": "sentence",
  "sentence": "line",
  "line": "text"
 },
 "visible": {
  "word": {
   "lang": false,
   "speaker": false,
   "text": true,
   "full": false,
   "fuzzy": true,
   "lite": false,
   "pos": false,
   "cls": false,
   "voice": false,
   "place": false,
   "manner": false
  },
  "line": {
   "number": false
  },
  "text": {
   "title": false,
   "dialect": false,
   "tid": false,
   "place": false
  }
 },
 "levels": {
  "word": "Some words are affixed to others without intervening space.",
  "sentence": "Sentences are delimited by full stops.",
  "line": "Lines are really paragraphs.",
  "text": "Texts are stories, having some metadata, consisting of lines."
 },
 "layers": {
  "word": {
   "lang": {
    "valueMap": {
     "1": "NENA",
     "2": "K.",
     "3": "A.",
     "4": "K./A.",
     "5": "A.|A.|K.",
     "6": "A.|K.",
     "7": "K./T.",
     "8": "K.|K.",
     "9": "K.|K.|K.",
     "10": "A.|A.",
     "11": "Urm.",
     "12": "E.",
     "13": "K./A./E.",
     "14": "P.",
     "15": "A./K.",
     "16": "K./A.|K./A.",
     "17": "T.",
     "18": "Ṭiy.",
     "19": "A./E.",
     "20": "K./E.",
     "21": "K./T.|K./T.",
     "0": ""
    },
    "tip": true,
    "pos": "lang",
    "pattern": "",
    "description": "language, indicated by a number"
   },
   "speaker": {
    "valueMap": {
     "1": "Dawið ʾAdam",
     "2": "Yulia Davudi",
     "3": "Yuwarəš Xošăba Kena",
     "4": "Manya Givoyev",
     "5": "Yuwəl Yuḥanna",
     "6": "Nanəs Bənyamən",
     "7": "Yosəp bet Yosəp",
     "8": "Yonan Petrus",
     "9": "Natan Khoshaba",
     "10": "Arsen Mikhaylov",
     "11": "Xošebo ʾOdišo",
     "12": "Nancy George",
     "13": "Awiko Sulaqa",
     "14": "Maryam Gwirgis",
     "15": "Alice Bet-Yosəp",
     "16": "Bənyamən Bənyamən",
     "17": "MB",
     "18": "Mišayel Barčəm",
     "19": "Nadia Aloverdova",
     "20": "Frederic Ayyubkhan",
     "21": "Victor Orshan",
     "22": "Merab Badalov",
     "23": "Sophia Danielova",
     "24": "Blandina Barwari",
     "25": "YD",
     "26": "Dawið Gwərgəs",
     "27": "Gwərgəs Dawið",
     "28": "AB",
     "29": "Jacob Petrus",
     "30": "Dawid Adam",
     "31": "NK",
     "32": "YP",
     "33": "JP",
     "34": "Kena Kena",
     "35": "Nawiya ʾOdišo",
     "36": "GK",
     "37": "Leya ʾOraha",
     "0": ""
    },
    "tip": true,
    "pos": "speaker",
    "pattern": "",
    "description": "speaker, indicated by a number"
   },
   "text": {
    "valueMap": null,
    "tip": false,
    "pos": "text",
    "pattern": "",
    "description": "text precise, complete, uses non-ascii: <code>maqəlbə̀nna</code>"
   },
   "full": {
    "valueMap": null,
    "tip": false,
    "pos": "full",
    "pattern": "",
    "description": "text representation: <code>maq9lb9`nna</code>"
   },
   "fuzzy": {
    "valueMap": null,
    "tip": false,
    "pos": "fuzzy",
    "pattern": "mute",
    "description": "text representation: <code>maqilbinna</code>"
   },
   "lite": {
    "valueMap": null,
    "tip": false,
    "pos": "lite",
    "pattern": "",
    "description": "text representation: <code>maq9lb9nna</code>"
   },
   "pos": {
    "valueMap": {
     "n": "NOUN",
     "pt": "PART",
     "pn": "PRON",
     "nr": "NUMR",
     "aj": "ADJV",
     "ab": "ADVB",
     "m": "MODI",
     "i": "INTJ",
     "pp": "PREP",
     "v": "VERB",
     "n_pt": "NOUN|PART",
     "n_n": "NOUN|NOUN",
     "pn_pt": "PRON|PART",
     "pt_pn": "PART|PRON",
     "m_n": "MODI|NOUN",
     "m_pn": "MODI|PRON",
     "pt_n": "PART|NOUN",
     "ab_n": "ADVB|NOUN",
     "n_ab": "NOUN|ADVB",
     "n_aj": "NOUN|ADJV",
     "aj_aj": "ADJV|ADJV",
     "aj_n": "ADJV|NOUN",
     "nr_nr": "NUMR|NUMR",
     "aj_ab": "ADJV|ADVB",
     "n_intj": "NOUN|INTJ",
     "n_n_n": "NOUN|NOUN|NOUN",
     "pt_pt_pt": "PART|PART|PART",
     "aj_n_n": "ADJV|NOUN|NOUN",
     "aj_n_n_n": "ADJV|NOUN|NOUN|NOUN",
     "n_n_n_n": "NOUN|NOUN|NOUN|NOUN",
     "z": ""
    },
    "tip": false,
    "pos": "pos",
    "pattern": "",
    "description": "part-of-speech"
   },
   "cls": {
    "valueMap": {
     "V": "vowel",
     "C": "consonant",
     "z": ""
    },
    "tip": false,
    "pos": "cls",
    "pattern": "",
    "description": "phonetic class: <code>CVCVCCVCCV</code>"
   },
   "voice": {
    "valueMap": {
     "P": "plain",
     "H": "unvoiced_aspirated",
     "V": "voiced",
     "F": "unvoiced",
     "G": "unvoiced_unaspirated",
     "X": "emphatic",
     "z": ""
    },
    "tip": false,
    "pos": "cls",
    "pattern": "",
    "description": "phonation: <code>PzzzPVzPPz</code>"
   },
   "place": {
    "valueMap": {
     "D": "dental-alveolar",
     "B": "labial",
     "C": "palatal-alveolar",
     "J": "palatal",
     "G": "velar",
     "X": "uvular",
     "Q": "pharyngeal",
     "H": "laryngeal",
     "z": ""
    },
    "tip": false,
    "pos": "cls",
    "pattern": "",
    "description": "phonetic place: <code>BzXzDBzDDz</code>"
   },
   "manner": {
    "valueMap": {
     "A": "affricative",
     "N": "nasal",
     "X": "other",
     "F": "fricative",
     "L": "lateral",
     "S": "sibilant",
     "z": ""
    },
    "tip": false,
    "pos": "cls",
    "pattern": "",
    "description": "phonetic manner: <code>NzAzLAzNNz</code>"
   }
  },
  "line": {
   "number": {
    "valueMap": null,
    "tip": false,
    "pos": "number",
    "pattern": "",
    "description": "line number"
   }
  },
  "text": {
   "title": {
    "valueMap": null,
    "tip": false,
    "pos": "title",
    "pattern": "A",
    "description": "title of a text"
   },
   "dialect": {
    "valueMap": null,
    "tip": false,
    "pos": "dialect",
    "pattern": "",
    "description": "dialect of a text <code>Barwar Urmi_C</code>"
   },
   "tid": {
    "valueMap": null,
    "tip": false,
    "pos": "tid",
    "pattern": "",
    "description": "id of a text"
   },
   "place": {
    "valueMap": null,
    "tip": false,
    "pos": "place",
    "pattern": "Dure",
    "description": "place of a text"
   }
  }
 }
}