import os
import sys
import json

from tf.app import use
from tf.convert.recorder import Recorder
from tf.core.helpers import specFromRanges, rangesFromSet

from defs import OUTPUT


A = use("nena:clone", checkout="clone")
C = A.api.C
F = A.api.F
Fs = A.api.Fs
L = A.api.L


PH_ABSENT = "z"
CH_ABSENT = "¿"

BASE_LEVEL = "word"
# BASE_LEVEL = "letter"

SETTINGS = {}
SIMPLE_BASE = dict(letter=True, word=False)

NAME = "nena"
URLS = dict(
    corpus=(
        "https://nena.ames.cam.ac.uk",
        "North-Eastern Neo-Aramaic Data Project website",
    ),
    maker=(
        "https://dans.knaw.nl/en/front-page?set_language=en",
        "DANS = Data Archiving and Networked Services",
    ),
    tf=(
        "https://annotation.github.io/text-fabric/tf/",
        "Text-Fabric documentation website",
    ),
)

CAPTIONS = dict(
    title="NENA phono search",
)

DESCRIPTION = """
<p>Phonetic search interface for the
   <a href="https://nena.ames.cam.ac.uk/" target="_blank">Northeastern Neo-Aramaic Database</a>.
</p>
<p>Based on <a href="https://github.com/CambridgeSemiticsLab/nena_tf" target="_blank">NENA data in Text-Fabric format</a>.</p>
<p>See the
<a href="https://github.com/CambridgeSemiticsLab/nena_tf/blob/master/docs/features.md" target="_blank">data documentation</a>.</p>
<p>This is a standalone app. You download it to your computer, and then it works without
connection to the internet.</p>
<p>This web app is by:</p>
<ul>
<li> <a href="https://www.ames.cam.ac.uk/people/professor-geoffrey-khan" target="_blank">Geoffrey Khan</a> (initiator)
<li> <a href="https://www.linkedin.com/in/cody-kingham-1135018a" target="_blank">Cody Kingham</a> (corpus developer)
<li> <a href="https://pure.knaw.nl/portal/en/persons/dirk-roorda" target="_blank">Dirk Roorda</a> (software developer)
</ul>
"""

DESC_TEXT = "text precise, complete, uses non-ascii: <code>maqəlbə̀nna</code>"
DESC_FULL = "text representation: <code>maq9lb9`nna</code>"
DESC_FUZZY = "text representation: <code>maqilbinna</code>"
DESC_LITE = "text representation: <code>maq9lb9nna</code>"
DESC_POS = "part-of-speech"
DESC_CLS = "phonetic class: <code>CVCVCCVCCV</code>"
DESC_VOICE = "phonation: <code>PzzzPVzPPz</code>"
DESC_PLACE = "phonation: <code>BzXzDBzDDz</code>"
DESC_MANNER = "phonation: <code>NzAzLAzNNz</code>"

DESC_LANG = "language, indicated by a number"
DESC_SPEAKER = "speaker, indicated by a number"

DESC_NUMBER = "line number"

DESC_TITLE = "title of a text"
DESC_DIALECT = "dialect of a text <code>Barwar Urmi_C</code>"
DESC_TID = "id of a text"
DESC_TPLACE = "place of a text"

DESC_L_LETTER = (
    "Some letters are expressed by multiple characters in some representations."
)
DESC_L_WORD = "Some words are affixed to others without intervening space."
DESC_L_SENTENCE = "Sentences are delimited by full stops."
DESC_L_LINE = "Lines are really paragraphs."
DESC_L_TEXT = "Texts are stories, having some metadata, consisting of lines."


MAP_LANG = {x[0]: i + 1 for (i, x) in enumerate(F.lang.freqList())}
MAP_SPEAKER = {x[0]: i + 1 for (i, x) in enumerate(F.speaker.freqList())}
MAP_CLS = {
    "vowel": "V",
    "consonant": "C",
}
MAP_VOICE = {
    "plain": "P",
    "unvoiced_aspirated": "H",
    "voiced": "V",
    "unvoiced": "F",
    "unvoiced_unaspirated": "G",
    "emphatic": "X",
}
MAP_PLACE = map = {
    "dental-alveolar": "D",
    "labial": "B",
    "palatal-alveolar": "C",
    "palatal": "J",
    "velar": "G",
    "uvular": "X",
    "pharyngeal": "Q",
    "laryngeal": "H",
}
MAP_MANNER = {
    "affricative": "A",
    "nasal": "N",
    "other": "X",
    "fricative": "F",
    "lateral": "L",
    "sibilant": "S",
}
MAP_POS = {
    "NOUN": "n",
    "PART": "pt",
    "PRON": "pn",
    "NUMR": "nr",
    "ADJV": "aj",
    "ADVB": "ab",
    "MODI": "m",
    "INTJ": "i",
    "PREP": "pp",
    "VERB": "v",
    "NOUN|PART": "n|pt",
    "NOUN|NOUN": "n|n",
    "PRON|PART": "pn|pt",
    "PART|PRON": "pt|pn",
    "MODI|NOUN": "m|n",
    "MODI|PRON": "m|pn",
    "PART|NOUN": "pt|n",
    "ADVB|NOUN": "ab|n",
    "NOUN|ADVB": "n|ab",
    "NOUN|ADJV": "n|aj",
    "ADJV|ADJV": "aj|aj",
    "ADJV|NOUN": "aj|n",
    "NUMR|NUMR": "nr|nr",
    "ADJV|ADVB": "aj|ab",
    "NOUN|INTJ": "n|intj",
    "NOUN|NOUN|NOUN": "n|n|n",
    "PART|PART|PART": "pt|pt|pt",
    "ADJV|NOUN|NOUN": "aj|n|n",
    "ADJV|NOUN|NOUN|NOUN": "aj|n|n|n",
    "NOUN|NOUN|NOUN|NOUN": "n|n|n|n",
}


SETTINGS = dict(
    word=dict(
        word=dict(
            description=DESC_L_WORD,
            layers=dict(
                lang=dict(
                    feature="lang",
                    description=DESC_LANG,
                    map=MAP_LANG,
                    default=0,
                    pos=None,
                    visible=False,
                ),
                speaker=dict(
                    feature="speaker",
                    description=DESC_SPEAKER,
                    map=MAP_SPEAKER,
                    default=0,
                    pos=None,
                    visible=False,
                ),
                text=dict(
                    feature="text",
                    description=DESC_TEXT,
                    map=None,
                    default=CH_ABSENT,
                    pos=None,
                    visible=True,
                ),
                full=dict(
                    feature="full",
                    description=DESC_FULL,
                    map=None,
                    default=CH_ABSENT,
                    pos=None,
                    visible=False,
                ),
                fuzzy=dict(
                    feature="fuzzy",
                    description=DESC_FUZZY,
                    map=None,
                    default=CH_ABSENT,
                    pos=None,
                    visible=True,
                    example="mute",
                ),
                lite=dict(
                    feature="lite",
                    description=DESC_LITE,
                    map=None,
                    default=CH_ABSENT,
                    pos=None,
                    visible=False,
                ),
                pos=dict(
                    feature="pos",
                    description=DESC_POS,
                    map=MAP_POS,
                    default=PH_ABSENT,
                    visible=False,
                    pos=None,
                ),
                cls=dict(
                    feature="phonetic_class",
                    description=DESC_CLS,
                    descend="letter",
                    map=MAP_CLS,
                    default=PH_ABSENT,
                    visible=False,
                    pos=None,
                ),
                voice=dict(
                    feature="phonation",
                    description=DESC_VOICE,
                    descend="letter",
                    map=MAP_VOICE,
                    default=PH_ABSENT,
                    pos="cls",
                    visible=False,
                ),
                place=dict(
                    feature="phonetic_place",
                    description=DESC_PLACE,
                    descend="letter",
                    map=MAP_PLACE,
                    default=PH_ABSENT,
                    pos="cls",
                    visible=False,
                ),
                manner=dict(
                    feature="phonetic_manner",
                    description=DESC_MANNER,
                    descend="letter",
                    map=MAP_MANNER,
                    default=PH_ABSENT,
                    pos="cls",
                    visible=False,
                ),
            ),
            afterFeature="full_end",
            afterDefault="/",
        ),
        sentence=dict(
            description=DESC_L_SENTENCE,
            afterDefault="\n",
            by=True,
        ),
        line=dict(
            description=DESC_L_LINE,
            layers=dict(
                number=dict(
                    feature="line_number",
                    description=DESC_NUMBER,
                    map=None,
                    default=-1,
                    pos=None,
                    visible=False,
                ),
            ),
            afterDefault="\n",
        ),
        text=dict(
            description=DESC_L_TEXT,
            layers=dict(
                title=dict(
                    feature="title",
                    description=DESC_TITLE,
                    map=None,
                    default="¿",
                    pos=None,
                    visible=False,
                    example="A",
                ),
                dialect=dict(
                    feature="dialect",
                    description=DESC_DIALECT,
                    ascend="dialect",
                    map=None,
                    default="¿",
                    pos=None,
                    visible=False,
                ),
                tid=dict(
                    feature="text_id",
                    description=DESC_TID,
                    map=None,
                    default="¿",
                    pos=None,
                    visible=False,
                ),
                place=dict(
                    feature="place",
                    description=DESC_TPLACE,
                    map=None,
                    default="¿",
                    pos=None,
                    visible=False,
                    example="Dure",
                ),
            ),
            afterDefault="\n",
        ),
    ),
    letter=dict(
        letter=dict(
            description=DESC_L_LETTER,
            layers=dict(
                text=dict(
                    feature="text",
                    description=DESC_TEXT,
                    map=None,
                    default=CH_ABSENT,
                    pos=None,
                    visible=True,
                ),
                full=dict(
                    feature="full",
                    description=DESC_FULL,
                    map=None,
                    default=CH_ABSENT,
                    pos=None,
                    visible=False,
                ),
                fuzzy=dict(
                    feature="fuzzy",
                    description=DESC_FUZZY,
                    map=None,
                    default=CH_ABSENT,
                    pos=None,
                    visible=True,
                    example="mute",
                ),
                lite=dict(
                    feature="lite",
                    description=DESC_LITE,
                    map=None,
                    default=CH_ABSENT,
                    pos=None,
                    visible=False,
                ),
                pos=dict(
                    feature="pos",
                    description=DESC_POS,
                    map=MAP_POS,
                    default=PH_ABSENT,
                    visible=False,
                    pos=None,
                ),
                cls=dict(
                    feature="phonetic_class",
                    description=DESC_CLS,
                    map=MAP_CLS,
                    default=PH_ABSENT,
                    visible=False,
                    pos=None,
                ),
                voice=dict(
                    feature="phonation",
                    description=DESC_VOICE,
                    map=MAP_VOICE,
                    default=PH_ABSENT,
                    pos="cls",
                    visible=False,
                ),
                place=dict(
                    feature="phonetic_place",
                    description=DESC_PLACE,
                    map=MAP_PLACE,
                    default=PH_ABSENT,
                    pos="cls",
                    visible=False,
                ),
                manner=dict(
                    feature="phonetic_manner",
                    description=DESC_MANNER,
                    map=MAP_MANNER,
                    default=PH_ABSENT,
                    pos="cls",
                    visible=False,
                ),
            ),
        ),
        word=dict(
            description=DESC_L_WORD,
            layers=dict(
                lang=dict(
                    feature="lang",
                    description=DESC_LANG,
                    map=MAP_LANG,
                    default=0,
                    pos=None,
                    visible=False,
                ),
                speaker=dict(
                    feature="speaker",
                    description=DESC_SPEAKER,
                    map=MAP_SPEAKER,
                    default=0,
                    pos=None,
                    visible=False,
                ),
            ),
            afterFeature="full_end",
            afterDefault="/",
        ),
        sentence=dict(
            description=DESC_L_SENTENCE,
            afterDefault="\n",
            by=True,
        ),
        line=dict(
            description=DESC_L_LINE,
            layers=dict(
                number=dict(
                    description=DESC_NUMBER,
                    feature="line_number",
                    map=None,
                    default=-1,
                    pos=None,
                    visible=False,
                ),
            ),
            afterDefault="\n",
        ),
        text=dict(
            description=DESC_L_TEXT,
            layers=dict(
                title=dict(
                    feature="title",
                    description=DESC_TITLE,
                    map=None,
                    default="¿",
                    pos=None,
                    visible=False,
                    example="A",
                ),
                dialect=dict(
                    feature="dialect",
                    description=DESC_DIALECT,
                    ascend="dialect",
                    map=None,
                    default="¿",
                    pos=None,
                    visible=False,
                ),
                tid=dict(
                    feature="text_id",
                    description=DESC_TID,
                    map=None,
                    default="¿",
                    pos=None,
                    visible=False,
                ),
                place=dict(
                    feature="place",
                    description=DESC_TPLACE,
                    map=None,
                    default="¿",
                    pos=None,
                    visible=False,
                    example="Dure",
                ),
            ),
            afterDefault="\n",
        ),
    ),
)


def checkSettings(baseLevel):
    sys.stdout.write(f"Making data based on {baseLevel}-settings")

    layerSettings = SETTINGS[baseLevel]
    typeSeq = list(layerSettings)
    typesLower = {}

    for (i, tp) in enumerate(typeSeq):
        typesLower[tp] = typeSeq[0 : i + 1]

    settings = dict(
        name=NAME,
        urls=URLS,
        captions=CAPTIONS,
        description=DESCRIPTION,
        layerSettings=layerSettings,
        typeSeq=typeSeq,
        typesLower=typesLower,
        simpleBase=SIMPLE_BASE[baseLevel],
    )

    # check visible and by attributes

    theBys = []
    theVisibles = []

    for (nType, typeInfo) in layerSettings.items():
        if typeInfo.get("by", False):
            theBys.append(nType)

        for (name, layerInfo) in layerSettings[nType].get("layers", {}).items():
            if layerInfo.get("visible", False):
                theVisibles.append((nType, name))
            theMap = layerInfo.get("map", None)
            if theMap is not None:
                default = layerInfo.get("default", None)
                if default is not None:
                    theMap[""] = default

    if len(theBys) == 0:
        containerType = None
        sys.stderr.write("No node type is declared as result container ('by')\n")
    else:
        containerType = theBys[0]
        if len(theBys) > 1:
            sys.stderr.write(
                "Multiple node types declared as result container ('by'):\n"
            )
            sys.stderr.write("\t" + (", ".join(theBys)) + "\n")
        else:
            sys.stdout.write("Node type declared as result container ('by'):\n")
            sys.stdout.write(f"\t{containerType}\n")

    settings["containerType"] = containerType

    sys.stderr.flush()
    sys.stdout.flush()

    if len(theVisibles) == 0:
        sys.stderr.write(
            "No layer type is declared as visible in the result ('visible')\n"
        )
    else:
        sys.stdout.write("Layers declared as visible in the result ('visible'):\n")
        sys.stdout.write("\t" + (", ".join("/".join(s) for s in theVisibles)) + "\n")

    sys.stderr.flush()
    sys.stdout.flush()
    return settings


def compress(data):
    sets = {}

    compressed = []

    for n in sorted(data):
        sets.setdefault(data[n], []).append(n)

    for (value, nset) in sorted(sets.items(), key=lambda x: (x[1][0], x[1][-1])):
        nSpec = list(nset)[0] if len(nset) == 1 else specFromRanges(rangesFromSet(nset))
        compressed.append(f"{nSpec}\t{value}")

    return compressed


def invert(data):
    return {v: k for (k, v) in data.items()}


def invertMap(map):
    return None if map is None else {v: k for (k, v) in map.items()}


def record(baseLevel):
    A.indent(reset=True)
    A.info("preparing ... ")
    settings = checkSettings(baseLevel)
    layerSettings = settings["layerSettings"]
    typeSeq = settings["typeSeq"]
    typesLower = settings["typesLower"]
    letterLevel = baseLevel == "letter"

    A.info("start recording")

    up = {}
    visible = {}
    layers = {}
    levels = {}
    texts = {}
    positions = {}
    recorders = {}
    accumulators = {}

    for (nType, typeInfo) in layerSettings.items():
        levels[nType] = typeInfo.get("description", "")
        ti = typeInfo.get("layers", None)
        if ti is None:
            continue

        visible[nType] = {name: ti[name].get("visible", False) for name in ti}
        layers[nType] = {
            name: dict(
                valueMap=invertMap(ti[name]["map"]),
                pos=ti[name]["pos"] or name,
                pattern=ti[name].get("example", ""),
                description=ti[name].get("description", ""),
            )
            for name in ti
        }
        texts[nType] = {name: None for name in ti}
        positions[nType] = {name: None for name in ti if ti[name]["pos"] is None}
        recorders[nType] = {
            name: Recorder(A.api) for name in ti if ti[name]["pos"] is None
        }
        accumulators[nType] = {name: [] for name in ti if ti[name]["pos"] is not None}

    nChAbsent = 0

    def addValue(node):
        returnValue = None

        nType = F.otype.v(node)
        typeInfo = layerSettings[nType]
        theseLayers = typeInfo.get("layers", {})

        first = True

        for name in theseLayers:
            info = theseLayers[name]
            descend = info.get("descend", False)
            ascend = info.get("ascend", False)
            vMap = info["map"]
            default = info["default"]
            pos = info["pos"]
            if descend:
                value = ""
                for n in L.d(node, otype=descend):
                    val = Fs(info["feature"]).v(n)
                    if vMap:
                        val = vMap.get(val, default)
                    else:
                        val = val or default
                    value += str(val)
            else:
                refNode = L.u(node, otype=ascend)[0] if ascend else node
                value = Fs(info["feature"]).v(refNode)
                if vMap:
                    value = vMap.get(value, default)
                else:
                    value = value or default
                value = str(value)

            if pos is None:
                recorders[nType][name].add(value)
            else:
                accumulators[nType][name].append(value)

            if first:
                returnValue = value
                first = False

        return returnValue

    def addAfterValue(node):
        nType = F.otype.v(node)
        typeInfo = layerSettings[nType]
        afterFeature = typeInfo.get("afterFeature", None)
        afterDefault = typeInfo.get("afterDefault", None)
        value = ""
        if afterFeature is not None:
            value = Fs(afterFeature).v(node)
        if afterDefault is not None:
            if not value:
                value = afterDefault
        if value:
            addAll(nType, value)

    def addAll(nType, value):
        lowerTypes = typesLower[nType]
        for nType in lowerTypes:
            if nType in recorders:
                for x in recorders[nType].values():
                    x.add(value)
            if nType in accumulators:
                for x in accumulators[nType].values():
                    x.append(value)

    def deliverAll():
        for (nType, typeInfo) in recorders.items():
            for (name, x) in typeInfo.items():
                texts[nType][name] = x.text()
                # here we are going to use that there is at most one node per node type
                # that corresponds to a character position
                positions[nType][name] = [
                    tuple(nodes)[0] if nodes else None for nodes in x.positions()
                ]

        for (nType, typeInfo) in accumulators.items():
            for (name, x) in typeInfo.items():
                texts[nType][name] = "".join(x)

    def startNode(node):
        # we have organized recorders by node type
        # we only record nodes of matching type in recorders

        nType = F.otype.v(node)

        if nType in recorders:
            for rec in recorders[nType].values():
                rec.start(node)

    def endNode(node):
        # we have organized recorders by node type
        # we only record nodes of matching type in recorders
        nType = F.otype.v(node)

        if nType in recorders:
            for rec in recorders[nType].values():
                rec.end(node)

    # note the `up[n] = m` statements below:
    # we only let `up` connect nodes from one level to one level higher

    for (i, text) in enumerate(F.otype.s("text")):
        startNode(text)
        title = addValue(text)
        sys.stdout.write("\r" + f"{i + 1:>3} {title:<80}")

        for line in L.d(text, otype="line"):
            up[line] = text
            startNode(line)
            addValue(line)

            for sent in L.d(line, otype="sentence"):
                up[sent] = line
                startNode(sent)
                addValue(sent)

                for word in L.d(sent, otype="word"):
                    up[word] = sent
                    startNode(word)
                    addValue(word)

                    if letterLevel:
                        for letter in L.d(word, otype="letter"):
                            up[letter] = word
                            startNode(letter)

                            ch = addValue(letter)
                            if ch == CH_ABSENT:
                                nChAbsent += 1

                            addAfterValue(letter)
                            endNode(letter)

                    addAfterValue(word)
                    endNode(word)

                addAfterValue(sent)
                endNode(sent)

            addAfterValue(line)
            endNode(line)

        addAfterValue(text)
        endNode(text)

    deliverAll()

    sys.stdout.write("\n")

    if letterLevel:
        A.info(f"{nChAbsent} letter nodes with empty full text")

    config = dict(
        name=settings["name"],
        urls=settings["urls"],
        captions=settings["captions"],
        description=settings["description"],
        containerType=settings["containerType"],
        simpleBase=settings["simpleBase"],
        ntypes=typeSeq,
        ntypesinit={level[0]: level[2] for level in C.levels.data},
        ntypessize={level[0]: level[3] - level[2] + 1 for level in C.levels.data},
        dtypeOf={typeSeq[i + 1]: tp for (i, tp) in enumerate(typeSeq[0:-1])},
        utypeOf={tp: typeSeq[i + 1] for (i, tp) in enumerate(typeSeq[0:-1])},
        visible=visible,
        levels=levels,
        layers=layers,
    )
    data = dict(
        texts=texts,
        positions=positions,
        up=compress(up),
    )

    return (config, data)


def dumpData(config, data):
    A.indent(reset=True)
    A.info("Dumping data to a single compact json file")

    destData = f"{OUTPUT}/data"
    if not os.path.exists(destData):
        os.makedirs(destData, exist_ok=True)

    fileNameConfig = f"{destData}/configdata.js"
    fileNameData = f"{destData}/corpusdata.js"

    with open(fileNameConfig, "w") as fh:
        fh.write("const configData = ")
        json.dump(config, fh, ensure_ascii=False, indent=1)
    A.info(f"Config written to file {fileNameConfig}")

    with open(fileNameData, "w") as fh:
        fh.write("const corpusData = ")
        json.dump(data, fh, ensure_ascii=False, indent=None, separators=(",", ":"))
    A.info(f"Data written to file {fileNameData}")


A.info("Recording ...")
(config, data) = record(BASE_LEVEL)

A.info("Dumping ...")
dumpData(config, data)
