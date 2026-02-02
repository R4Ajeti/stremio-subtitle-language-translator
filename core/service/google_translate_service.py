

import random
import json
import re

from core.constant import DEFAULT_TRANSLATE_URL_STR, SOURCE_TEXT_AREA_SELECTOR_STR, TARGET_TEXT_SELECTOR_STR, DEFAULT_CHECK_FRAME_STR, USER_AGENT_RANDOM_OUTPUT_PATH_STR
from core.wrapper.user_agent_wrapper import ChromeForTestingUserAgentWrapper

class GoogleTranslateService:
    def __init__(self, noDriverModuleObj, translateUrlStr: str = DEFAULT_TRANSLATE_URL_STR):
        self.noDriverModuleObj = noDriverModuleObj
        self.translateUrlStr = translateUrlStr
        self.browserObj = None
        self.pageObj = None
        self.previousTranslatedTextStr = ""
        self.chromeForTestingUserAgentWrapper = ChromeForTestingUserAgentWrapper()

    def splitBySubTimeframe(self, translatedSpanStr: str):
        timecodePattern = re.compile(
            r"(?m)^(?:\d+\s*\n)?\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\s*$"
        )
        matches = list(timecodePattern.finditer(translatedSpanStr))
        if not matches:
            return translatedSpanStr.split("\n\n")

        blockList = []
        for matchIndexInt, matchObj in enumerate(matches):
            startInt = matchObj.start()
            endInt = matches[matchIndexInt + 1].start() if matchIndexInt + 1 < len(matches) else len(translatedSpanStr)
            blockStr = translatedSpanStr[startInt:endInt].strip()
            if blockStr:
                blockList.append(blockStr)
        return blockList

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
                
                

                noDriverInitParamDict = {
                    'sandbox': False,
                    'user_data_dir': "./profile_cache",
                    'browser_args': [f"--user-agent={self.chromeForTestingUserAgentWrapper.getRandomUserAgent()}"],   
                }
                
                # Create a fresh copy of init params
                currNoDriverInitParamDict = dict(noDriverInitParamDict)

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
            
    async def subIndexProcess(self, indexStr):
        """Process the subtitle index (e.g., '8')."""
        return indexStr.strip()

    async def subTimeCodeProcess(self, timeCodeStr):
        """Process the timecode line (e.g., '00:01:10,514 --> 00:01:13,290')."""
        return timeCodeStr.strip()
    
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
    
    def removeBracketedContent(self, textStr):
        """
        Remove content inside square brackets including the brackets.
        Example: "- [burrë] Hej, Lacie!" -> "- Hej, Lacie!"
        Example: "[qeshje]" -> ""
        """
        # Remove all [...] patterns and clean up extra spaces
        resultStr = re.sub(r'\s*\[[^\]]*\]\s*', ' ', textStr)
        return resultStr.strip()
    
    async def subFrameBodyProcess(self, subFrameBodyStr):
        subFrameBodyList = []
        # Remove bracketed content first
        currSubFrameBodyStr = self.removeBracketedContent(subFrameBodyStr)
        
        for lineStr in currSubFrameBodyStr.splitlines():
            
            if not lineStr:
                continue
            currentSubFrameBodyLine = await self.subFrameBodyLineProcess(lineStr)
            if currentSubFrameBodyLine:
                subFrameBodyList.append(currentSubFrameBodyLine)
        
        return '\n'.join(subFrameBodyList)
    
    async def subFrameProcess(self, spanBlockStr):
        """
        Process a single subtitle frame block.
        
        Input example:
            "8\n00:01:10,514 --> 00:01:13,290\n- [burrë] Hej, Lacie!\n\n- Hej!\n[qeshje]"
        Output example:
            "8\n00:01:10,514 --> 00:01:13,290\n- [burrë] Hej, Lacie!\n- Hej![qeshje]"
        """
        lineList = spanBlockStr.splitlines()
        
        subFrameIndexStr = None
        subFrameTimeCodeStr = None
        subFrameBodyLineStr = ''
        
        for lineStr in lineList:
            strippedLineStr = lineStr.strip()
            
            # Skip empty lines
            if not strippedLineStr:
                continue
            
            # Check if it's a timecode line
            if "-->" in strippedLineStr:
                subFrameTimeCodeStr = await self.subTimeCodeProcess(strippedLineStr)
            # Check if it's a numeric index (before timecode is found)
            elif subFrameTimeCodeStr is None and strippedLineStr.isdigit():
                subFrameIndexStr = await self.subIndexProcess(strippedLineStr)
            # Otherwise it's part of the subtitle body
            else:
                subFrameBodyLineStr = f"{subFrameBodyLineStr}{strippedLineStr}\n"
        
        # Build the result
        resultPartList = []
        
        if subFrameIndexStr:
            resultPartList.append(subFrameIndexStr)
        
        if subFrameTimeCodeStr:
            resultPartList.append(subFrameTimeCodeStr)
        
        if subFrameBodyLineStr:
            processedBodyStr = await self.subFrameBodyProcess(subFrameBodyLineStr)
            if processedBodyStr:
                processedBodyList = processedBodyStr.splitlines()
                resultPartList = [ *resultPartList, *processedBodyList ]
        
        return '\n'.join(resultPartList)

    async def readTranslatedText(self):
        translatedSpanList = await self.pageObj.find_all(TARGET_TEXT_SELECTOR_STR)
        translatedSpanStr = '\n'.join(span.text for span in translatedSpanList).strip()

        translatedBlockList = self.splitBySubTimeframe(translatedSpanStr)
        
        subChunkStr = ""
        subChunkList = []
        
        constCheckParityStr ="Nëse do të isha, do të ishe lakuriq."
        # <i>Nëse unë</i>\n<i>ishte, do të ishe lakuriq.</i>
        # <i>Nëse</i>\n<i>do të isha, do të ishe lakuriq.</i>
        
        for spanIndexInt, spanBlockStr in enumerate(translatedBlockList):
            if spanIndexInt == 7:
                a=2
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

    async def translateChunk(self, chunkStr):
        if not self.pageObj:
            return ""

        await self.setSourceText(chunkStr)
        await self.pageObj.wait(2)
        translatedTextStr = await self.readTranslatedText()
        return translatedTextStr
    

    async def stop(self):
        if self.browserObj:
            await self.browserObj.stop()
