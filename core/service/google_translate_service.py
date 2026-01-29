

import random
import json
import re

from core.constant import DEFAULT_TRANSLATE_URL_STR, SOURCE_TEXT_AREA_SELECTOR_STR, TARGET_TEXT_SELECTOR_STR, DEFAULT_CHECK_FRAME_STR, USER_AGENT_LIST, SUBTITLE_CHARACTER_PER_LINE_MIN_INT, SUBTITLE_CHARACTER_PER_LINE_MAX_INT
from core import logger


def getRandomUserAgent():
    """Returns a random user agent from the list."""
    randomUserAgentListPath = "random-user-agent-list.json"
    with open(randomUserAgentListPath, "r", encoding="utf-8") as file:
        userAgentData = json.load(file)
    randomUserAgent = random.choice(userAgentData['userAgents'])
    logger.info(f"Random User Agent: {randomUserAgent}")
    return randomUserAgent


noDriverInitParamDict = {
    'sandbox': False,
    'user_data_dir': "./profile_cache",
    'browser_args': [f"--user-agent={getRandomUserAgent()}"],   
}

class GoogleTranslateService:
    def __init__(self, noDriverModuleObj, translateUrlStr: str = DEFAULT_TRANSLATE_URL_STR):
        self.noDriverModuleObj = noDriverModuleObj
        self.translateUrlStr = translateUrlStr
        self.browserObj = None
        self.pageObj = None
        self.previousTranslatedTextStr = ""

    async def start(self):
        await self.open()
    
    async def open(self):
        maxTriesInt = 10

        for attemptInt in range(maxTriesInt):
            try:
                # Ensure previous instance is fully stopped
                if self.browserObj:
                    try:
                        await self.browserObj.stop()
                    except Exception:
                        pass
                    self.browserObj = None
                    self.pageObj = None

                # Create a fresh copy of init params
                currNoDriverInitParamDict = dict(noDriverInitParamDict)
                currNoDriverInitParamDict["browser_args"] = [
                    f"--user-agent={getRandomUserAgent()}"
                ]

                # Start nodriver
                self.browserObj = await self.noDriverModuleObj.start(
                    **currNoDriverInitParamDict
                )

                self.pageObj = await self.browserObj.get(self.translateUrlStr)

                # Validate Google Translate model (REAL check)
                googleTranslateFlag = await self.translateChunk(DEFAULT_CHECK_FRAME_STR)

                if googleTranslateFlag is not None:
                    print(
                        f"Success - Using user agent: "
                        f"{currNoDriverInitParamDict['browser_args'][0]}"
                    )
                    return

                raise RuntimeError("Invalid Google Translate DOM detected")

            except Exception as errorObj:
                print(
                    f"Wrong google translate model detected. "
                    f"Attempt {attemptInt + 1}/{maxTriesInt}. Restarting..."
                )

                try:
                    if self.browserObj:
                        await self.browserObj.stop()
                except Exception:
                    pass

                self.browserObj = None
                self.pageObj = None

                if attemptInt + 1 >= maxTriesInt:
                    raise RuntimeError("Max retries reached. Exiting...") from errorObj

    async def setSourceText(self, chunkStr):
            textAreaElement = await self.pageObj.find(SOURCE_TEXT_AREA_SELECTOR_STR, best_match=True, timeout=3)
            await textAreaElement.clear_input()
            chunkStr = chunkStr.replace("\n", "\r\n")
            await textAreaElement.send_keys(
                chunkStr,
            )
            
            a = 2
    
    async def lineConstructSentence(self, lineStr):
        # if lineStr contain ['.', '!', '?'], we assume it's the end of a sentence and add a space after it.
        # in case it's already there, we don't add another space.
        ellipsisTokenStr = "__ELLIPSIS__"
        lineStr = lineStr.replace("...", ellipsisTokenStr)
        lineStr = re.sub(r'([.!?])(?!\s)', r'\1 ', lineStr)
        lineStr = lineStr.replace(ellipsisTokenStr, "...")
        lineStr = re.sub(r'\.\.\.(?!\s)', '... ', lineStr)
        lineStr = ' '.join(lineStr.split())
        return lineStr
    
    async def subFrameBodyLineProcess(self, lineStr):
        lineStr = await self.lineConstructSentence(lineStr)
        return lineStr
    
    async def subFrameBodyProcess(self, currSubFrameBodyList):
        subFrameBodyList = []
        
        for lineStr in currSubFrameBodyList:
            subFrameBodyList.append(await self.subFrameBodyLineProcess(lineStr))
        
        return '\n'.join(subFrameBodyList)
            
    async def subTimeCodeProcess(self, timeCodeStr):
        return timeCodeStr

    async def subFrameProcess(self, spanBlockStr):
        lineList = spanBlockStr.splitlines()
        
        lastLineTCFlag = False
        lastLineSFBFlag = False
        
        subFrameStr = ""
        subFrameBodyList = []
        currSubFrameBodyList = []
        for lineSubIndexInt, lineStr in enumerate(lineList):
            subFrameLineStr = ""
            if lastLineTCFlag or lastLineSFBFlag:
                currSubFrameBodyList.append(lineStr)
                if lineSubIndexInt + 1 >= len(lineList) or len(lineList[lineSubIndexInt + 1].strip()) < 3:
                    subFrameLineStr = await self.subFrameBodyProcess(currSubFrameBodyList)
                lastLineSFBFlag = True
            elif "-->" in lineStr:
                subFrameLineStr = await self.subTimeCodeProcess(lineStr)
                lastLineTCFlag = True
            else:
                subFrameLineStr = lineStr
                lastLineTCFlag = False
                lastLineSFBFlag = False
            if subFrameLineStr:
                subFrameBodyList.append(subFrameLineStr)
        subFrameStr = '\n'.join(subFrameBodyList)
        return subFrameStr
        

    async def readTranslatedText(self):
        translatedSpanList = await self.pageObj.find_all(TARGET_TEXT_SELECTOR_STR)
        translatedSpanStr = '\n'.join(span.text for span in translatedSpanList).strip()
        
        translatedBlockList = translatedSpanStr.split("\n\n")
        
        subChunkStr = ""
        subChunkList = []
        
        constCheckParityStr ="Nëse do të isha, do të ishe lakuriq."
        # <i>Nëse unë</i>\n<i>ishte, do të ishe lakuriq.</i>
        # <i>Nëse</i>\n<i>do të isha, do të ishe lakuriq.</i>
        
        for spanIndexInt, spanBlockStr in enumerate(translatedBlockList):
            subFrameStr = await self.subFrameProcess(spanBlockStr)
            currCheckSubFrameStr = subFrameStr.replace("\n", " ").replace("<i>", "").replace("</i>", "").strip()
            if spanIndexInt == 0:
                if not constCheckParityStr in currCheckSubFrameStr:
                    print(f"Warning: Parity check failed for span index {spanIndexInt}. Expected '{constCheckParityStr}', got '{currCheckSubFrameStr}'")
                    return None
            else:
                subChunkList.append(subFrameStr)
        
        subChunkStr = f"\n\n".join(subChunkList)
            
        return subChunkStr
    
    async def readTranslatedTextNew(self):
        translatedSpanList = await self.pageObj.find_all(TARGET_TEXT_SELECTOR_STR)
        translatedSpanStr = "".join(span.text for span in translatedSpanList).strip()
        
        translatedBlockList = translatedSpanStr.split("\n\n")
        
        subChunkStr = ""
        subChunkList = []
        
        for spanIndexInt, spanBlockStr in enumerate(translatedBlockList):
            subFrameStr = await self.subFrameProcess(spanBlockStr)
            subChunkList.append(subFrameStr)
        
        subChunkStr = "\n\n".join(subChunkList)
            
        return subChunkStr

    async def translateChunk(self, chunkStr):
        if not self.pageObj:
            return ""

        await self.setSourceText(chunkStr)
        await self.pageObj.wait(2)
        translatedTextStr = await self.readTranslatedText()
        return translatedTextStr
    
    async def translate(self, chunkStr):
        if not self.pageObj:
            return ""

        await self.setSourceText(chunkStr)
        await self.pageObj.wait(2)
        translatedTextStr = await self.readTranslatedTextNew()
        return translatedTextStr
    

    async def stop(self):
        if self.browserObj:
            await self.browserObj.stop()
