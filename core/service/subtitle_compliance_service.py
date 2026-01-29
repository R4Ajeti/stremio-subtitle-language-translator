import re

import pandas as pd


NETFLIX_MIN_DURATION_SECONDS = 5.0 / 6.0
NETFLIX_MAX_DURATION_SECONDS = 7.0
NETFLIX_MIN_GAP_FRAMES_INT = 2
NETFLIX_SYNC_TOLERANCE_FRAMES_INT = 3
NETFLIX_FRAMES_PER_SECOND_INT = 24
NETFLIX_READING_SPEED_ADULT_CPS_INT = 20
NETFLIX_READING_SPEED_CHILD_CPS_INT = 17
NETFLIX_MAX_LINE_COUNT_INT = 2
NETFLIX_MAX_CHAR_PER_LINE_INT = 42
NETFLIX_KOREAN_MAX_CHAR_PER_LINE_INT = 23
NETFLIX_NUMBER_WORD_MAP_DICT = {
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
    "10": "ten",
}


class SubtitleComplianceService:
    """Enforces Netflix subtitle timing and formatting standards."""

    def __init__(self, isChildProgramObj=False, framesPerSecondInt=NETFLIX_FRAMES_PER_SECOND_INT):
        self.isChildProgramObj = isChildProgramObj
        self.framesPerSecondInt = framesPerSecondInt
        self.minimumGapSecondsObj = NETFLIX_MIN_GAP_FRAMES_INT / max(1, framesPerSecondInt)
        self.readingSpeedCpsInt = NETFLIX_READING_SPEED_CHILD_CPS_INT if isChildProgramObj else NETFLIX_READING_SPEED_ADULT_CPS_INT
        self.syncToleranceSecondsObj = NETFLIX_SYNC_TOLERANCE_FRAMES_INT / max(1, framesPerSecondInt)

    def applyComplianceToSrtText(self, subtitleContentStr):
        subtitleBlockList = self.splitSubtitleBlockList(subtitleContentStr)
        subtitleDataFrameObj = self.buildSubtitleDataFrameObj(subtitleBlockList)
        if subtitleDataFrameObj.empty:
            return ""
        compliantBlockDictList = []
        previousEndSecondsObj = 0.0
        for subtitleBlockDict in subtitleDataFrameObj["subtitleBlockDict"]:
            compliantSegmentDictList = self.transformBlockIntoCompliantBlockList(
                subtitleBlockDict,
                previousEndSecondsObj,
            )
            for compliantBlockDict in compliantSegmentDictList:
                compliantBlockDictList.append(compliantBlockDict)
                previousEndSecondsObj = compliantBlockDict["endSecondsObj"]
        if not compliantBlockDictList:
            return ""
        compliantDataFrameObj = pd.DataFrame(compliantBlockDictList)
        compliantDataFrameObj["indexInt"] = range(1, len(compliantDataFrameObj) + 1)
        compliantDataFrameObj["subtitleBlockStr"] = compliantDataFrameObj.apply(self.renderSubtitleBlockStr, axis=1)
        compliantSubtitleList = compliantDataFrameObj["subtitleBlockStr"].tolist()
        return "\n\n".join(compliantSubtitleList)

    def splitSubtitleBlockList(self, subtitleContentStr):
        normalizedSubtitleStr = subtitleContentStr.replace("\r\n", "\n").strip()
        if not normalizedSubtitleStr:
            return []
        subtitleBlockList = [blockStr.strip() for blockStr in normalizedSubtitleStr.split("\n\n") if blockStr.strip()]
        return subtitleBlockList

    def buildSubtitleDataFrameObj(self, subtitleBlockList):
        subtitleDataFrameObj = pd.DataFrame({"subtitleBlockStr": subtitleBlockList})
        if subtitleDataFrameObj.empty:
            return subtitleDataFrameObj
        subtitleDataFrameObj["subtitleBlockDict"] = subtitleDataFrameObj["subtitleBlockStr"].apply(self.parseSubtitleBlockDict)
        subtitleDataFrameObj = subtitleDataFrameObj[subtitleDataFrameObj["subtitleBlockDict"].notnull()].reset_index(drop=True)
        return subtitleDataFrameObj

    def parseSubtitleBlockDict(self, subtitleBlockStr):
        subtitleLineList = subtitleBlockStr.split("\n")
        if len(subtitleLineList) < 3:
            return None
        indexLineStr = subtitleLineList[0].strip()
        timingLineStr = subtitleLineList[1].strip()
        subtitleTextLineList = [lineStr.strip() for lineStr in subtitleLineList[2:] if lineStr.strip()]
        if not timingLineStr:
            return None
        timingPartList = [timingPartStr.strip() for timingPartStr in timingLineStr.split("-->")]
        if len(timingPartList) != 2:
            return None
        try:
            startSecondsObj = self.convertTimestampStrToSecondsObj(timingPartList[0])
            endSecondsObj = self.convertTimestampStrToSecondsObj(timingPartList[1])
        except ValueError:
            return None
        if endSecondsObj <= startSecondsObj:
            endSecondsObj = startSecondsObj + NETFLIX_MIN_DURATION_SECONDS
        try:
            originalIndexInt = int(indexLineStr)
        except ValueError:
            originalIndexInt = 0
        subtitleBlockDict = {
            "indexInt": originalIndexInt,
            "startSecondsObj": startSecondsObj,
            "endSecondsObj": endSecondsObj,
            "textLineList": subtitleTextLineList,
        }
        return subtitleBlockDict

    def transformBlockIntoCompliantBlockList(self, subtitleBlockDict, previousEndSecondsObj):
        normalizedBodyStr = self.normalizeSubtitleBodyStr(subtitleBlockDict["textLineList"])
        normalizedBodyStr = self.applyNumberWritingRule(normalizedBodyStr)
        wrappedLineList = self.wrapTextIntoCompliantLineList(normalizedBodyStr)
        compliantSegmentLineListList = self.groupLinesIntoSegmentLineListList(wrappedLineList)
        compliantBlockDictList = self.allocateTimingsToSegmentLineList(
            subtitleBlockDict,
            compliantSegmentLineListList,
            previousEndSecondsObj,
        )
        return compliantBlockDictList

    def normalizeSubtitleBodyStr(self, subtitleTextLineList):
        normalizedTextList = [lineStr.strip() for lineStr in subtitleTextLineList if lineStr.strip()]
        normalizedBodyStr = " ".join(normalizedTextList)
        normalizedBodyStr = re.sub(r"\s+", " ", normalizedBodyStr)
        return normalizedBodyStr.strip()

    def applyNumberWritingRule(self, subtitleBodyStr):
        def replaceNumber(matchObj):
            matchedNumberStr = matchObj.group(0)
            return NETFLIX_NUMBER_WORD_MAP_DICT.get(matchedNumberStr, matchedNumberStr)

        rewrittenSubtitleBodyStr = re.sub(r"\b(10|[1-9])\b", replaceNumber, subtitleBodyStr)
        return rewrittenSubtitleBodyStr

    def wrapTextIntoCompliantLineList(self, subtitleBodyStr):
        if not subtitleBodyStr:
            return []
        activeLineLimitInt = self.determineLineCharacterLimitInt(subtitleBodyStr)
        wrappedLineList = []
        activeLineWordList = []
        for wordStr in subtitleBodyStr.split(" "):
            if len(wordStr) > activeLineLimitInt:
                overlongWordSegmentList = self.splitOverlongWordSegmentList(wordStr, activeLineLimitInt)
            else:
                overlongWordSegmentList = [wordStr]
            for segmentStr in overlongWordSegmentList:
                candidateLineStr = " ".join(activeLineWordList + [segmentStr]) if activeLineWordList else segmentStr
                if activeLineWordList and len(candidateLineStr) > activeLineLimitInt:
                    wrappedLineList.append(" ".join(activeLineWordList))
                    activeLineWordList = [segmentStr]
                else:
                    if activeLineWordList:
                        activeLineWordList.append(segmentStr)
                    else:
                        activeLineWordList = [segmentStr]
        if activeLineWordList:
            wrappedLineList.append(" ".join(activeLineWordList))
        return wrappedLineList

    def splitOverlongWordSegmentList(self, wordStr, lineLimitInt):
        segmentList = []
        remainingWordStr = wordStr
        effectiveLimitInt = max(2, lineLimitInt)
        while len(remainingWordStr) > effectiveLimitInt:
            splitSegmentStr = f"{remainingWordStr[:effectiveLimitInt - 1]}-"
            segmentList.append(splitSegmentStr)
            remainingWordStr = remainingWordStr[effectiveLimitInt - 1 :]
        segmentList.append(remainingWordStr)
        return segmentList

    def determineLineCharacterLimitInt(self, subtitleBodyStr):
        for characterStr in subtitleBodyStr:
            characterCodeInt = ord(characterStr)
            if 0xAC00 <= characterCodeInt <= 0xD7AF:
                return NETFLIX_KOREAN_MAX_CHAR_PER_LINE_INT
        return NETFLIX_MAX_CHAR_PER_LINE_INT

    def groupLinesIntoSegmentLineListList(self, wrappedLineList):
        if not wrappedLineList:
            return []
        compliantSegmentLineListList = []
        for lineIndexInt in range(0, len(wrappedLineList), NETFLIX_MAX_LINE_COUNT_INT):
            segmentLineList = wrappedLineList[lineIndexInt : lineIndexInt + NETFLIX_MAX_LINE_COUNT_INT]
            formattedSegmentLineList = self.applyDualSpeakerFormattingList(segmentLineList)
            compliantSegmentLineListList.append(formattedSegmentLineList)
        return compliantSegmentLineListList

    def applyDualSpeakerFormattingList(self, segmentLineList):
        formattedLineList = []
        for lineStr in segmentLineList:
            strippedLineStr = lineStr.strip()
            if strippedLineStr.startswith("-") and not strippedLineStr.startswith("- "):
                formattedLineList.append(f"- {strippedLineStr[1:].lstrip()}")
            else:
                formattedLineList.append(strippedLineStr)
        return formattedLineList

    def allocateTimingsToSegmentLineList(self, subtitleBlockDict, segmentLineListList, previousEndSecondsObj):
        compliantBlockDictList = []
        if not segmentLineListList:
            return compliantBlockDictList
        currentStartSecondsObj = max(
            subtitleBlockDict["startSecondsObj"],
            previousEndSecondsObj + self.minimumGapSecondsObj,
        )
        for segmentLineList in segmentLineListList:
            segmentCharCountInt = len(" ".join(segmentLineList))
            if segmentCharCountInt <= 0:
                segmentCharCountInt = NETFLIX_MAX_LINE_COUNT_INT
            requiredDurationSecondsObj = max(
                NETFLIX_MIN_DURATION_SECONDS,
                segmentCharCountInt / max(1, self.readingSpeedCpsInt),
            )
            requiredDurationSecondsObj += self.syncToleranceSecondsObj
            requiredDurationSecondsObj = min(requiredDurationSecondsObj, NETFLIX_MAX_DURATION_SECONDS)
            segmentEndSecondsObj = currentStartSecondsObj + requiredDurationSecondsObj
            compliantBlockDictList.append(
                {
                    "indexInt": subtitleBlockDict["indexInt"],
                    "startSecondsObj": currentStartSecondsObj,
                    "endSecondsObj": segmentEndSecondsObj,
                    "textLineList": segmentLineList,
                }
            )
            currentStartSecondsObj = segmentEndSecondsObj + self.minimumGapSecondsObj
        return compliantBlockDictList

    def renderSubtitleBlockStr(self, subtitleBlockSeriesObj):
        startTimestampStr = self.convertSecondsObjToTimestampStr(subtitleBlockSeriesObj["startSecondsObj"])
        endTimestampStr = self.convertSecondsObjToTimestampStr(subtitleBlockSeriesObj["endSecondsObj"])
        subtitleTextStr = "\n".join(subtitleBlockSeriesObj["textLineList"])
        return f"{subtitleBlockSeriesObj['indexInt']}\n{startTimestampStr} --> {endTimestampStr}\n{subtitleTextStr}"

    def convertTimestampStrToSecondsObj(self, timestampStr):
        timestampStr = timestampStr.strip()
        if not timestampStr:
            raise ValueError("Invalid timestamp")
        hourPartStr, minutePartStr, secondPartStr = timestampStr.split(":")
        secondStr, millisecondStr = secondPartStr.split(",")
        hoursInt = int(hourPartStr)
        minutesInt = int(minutePartStr)
        secondsInt = int(secondStr)
        millisecondsInt = int(millisecondStr)
        totalMillisecondsInt = (
            hoursInt * 3600000
            + minutesInt * 60000
            + secondsInt * 1000
            + millisecondsInt
        )
        return totalMillisecondsInt / 1000.0

    def convertSecondsObjToTimestampStr(self, secondsObj):
        totalMillisecondsInt = max(0, int(round(secondsObj * 1000)))
        hoursInt, remainingMillisecondsInt = divmod(totalMillisecondsInt, 3600000)
        minutesInt, remainingMillisecondsInt = divmod(remainingMillisecondsInt, 60000)
        secondsInt, millisecondsInt = divmod(remainingMillisecondsInt, 1000)
        return f"{hoursInt:02d}:{minutesInt:02d}:{secondsInt:02d},{millisecondsInt:03d}"

