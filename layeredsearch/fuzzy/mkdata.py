import sys

from tf.convert.recorder import Recorder


def makeLegends(maker):
    pass


def record(maker):
    A = maker.A
    api = A.api
    F = api.F
    Fs = api.Fs
    L = api.L

    C = maker.C
    layerSettings = C.layerSettings

    clientConfig = maker.clientConfig
    typesLower = clientConfig["typesLower"]

    A.indent(reset=True)
    A.info("preparing ... ")

    A.info("start recording")

    up = {}
    recorders = {}
    accumulators = {}
    maker.up = up
    maker.recorders = recorders
    maker.accumulators = accumulators

    for (level, typeInfo) in layerSettings.items():
        ti = typeInfo.get("layers", None)
        if ti is None:
            continue

        recorders[level] = {
            layer: Recorder(api) for layer in ti if ti[layer]["pos"] is None
        }
        accumulators[level] = {layer: [] for layer in ti if ti[layer]["pos"] is not None}

    def addValue(node):
        returnValue = None

        level = F.otype.v(node)
        typeInfo = layerSettings[level]
        theseLayers = typeInfo.get("layers", {})

        first = True

        for layer in theseLayers:
            info = theseLayers[layer]
            descend = info.get("descend", False)
            ascend = info.get("ascend", False)
            feature = info.get("feature", None)
            featureFunc = Fs(feature).v
            afterFeature = info.get("afterFeature", None)
            afterDefault = info.get("afterDefault", None)
            vMap = info.get("legend", None)
            default = info["default"]
            pos = info["pos"]
            if descend:
                value = ""
                for n in L.d(node, otype=descend):
                    val = featureFunc(n)
                    if vMap:
                        val = vMap.get(val, default)
                    else:
                        val = val or default

                    value += str(val)
            else:
                refNode = L.u(node, otype=ascend)[0] if ascend else node
                value = featureFunc(refNode)
                if vMap:
                    value = vMap.get(value, default)
                else:
                    value = value or default

            afterVal = ""
            if afterFeature is not None:
                afterVal = Fs(afterFeature).v(node)
                if not afterVal and afterDefault:
                    afterVal = afterDefault
            value = f"{value}{afterVal}"

            if pos is None:
                recorders[level][layer].add(value)
            else:
                accumulators[level][layer].append(value)

            if first:
                returnValue = value
                first = False

        return returnValue

    def addAfterValue(node):
        level = F.otype.v(node)
        typeInfo = layerSettings[level]
        afterFeature = typeInfo.get("afterFeature", None)
        afterDefault = typeInfo.get("afterDefault", None)
        value = ""
        if afterFeature is not None:
            value = Fs(afterFeature).v(node)
        if afterDefault is not None:
            if not value:
                value = afterDefault
        if value:
            addAll(level, value)

    def addAll(level, value):
        lowerTypes = typesLower[level]
        for lType in lowerTypes:
            if lType in recorders:
                for x in recorders[lType].values():
                    x.add(value)
            if lType in accumulators:
                for x in accumulators[lType].values():
                    x.append(value)

    def startNode(node):
        # we have organized recorders by node type
        # we only record nodes of matching type in recorders

        level = F.otype.v(node)

        if level in recorders:
            for rec in recorders[level].values():
                rec.start(node)

    def endNode(node):
        # we have organized recorders by node type
        # we only record nodes of matching type in recorders
        level = F.otype.v(node)

        if level in recorders:
            for rec in recorders[level].values():
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
                    addAfterValue(word)
                    endNode(word)
                addAfterValue(sent)
                endNode(sent)
            addAfterValue(line)
            endNode(line)
        addAfterValue(text)
        endNode(text)

    sys.stdout.write("\n")
    A.info("done")
