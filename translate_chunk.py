from pathlib import Path
import importlib
import asyncio
import random
import sys


from google_translate_automation import GoogleTranslateAutomation
from subtitle_file_manager import SubtitleFileManager

from constants import USER_AGENT_LIST, DEFAULT_CHECK_FRAME_STR

def getRandomUserAgent():
    """Returns a random user agent from the list."""
    return random.choice(USER_AGENT_LIST)

def buildUsageMessage():
    return "Usage: python run.py \"input.srt\" [output_folder] [char_limit]"


# def parseCharLimit(charLimitArgStr):
#     if not charLimitArgStr:
#         return DEFAULT_CHAR_LIMIT_INT
#     return int(charLimitArgStr)


def formatProgressBar(processedCountInt, totalCountInt, barWidthInt=30):
    if totalCountInt <= 0:
        return "[{}] 0/0".format(" " * barWidthInt)
    filledLengthInt = int(barWidthInt * processedCountInt / totalCountInt)
    filledLengthInt = min(barWidthInt, max(0, filledLengthInt))
    barStr = "#" * filledLengthInt + "-" * (barWidthInt - filledLengthInt)
    return f"[{barStr}] {processedCountInt}/{totalCountInt}"


async def main(noDriverModuleObj):
    inputFilePathStr = sys.argv[1] if len(sys.argv) > 1 else ""
    outputPathArgStr = sys.argv[2] if len(sys.argv) > 2 else ""
    charLimitArgStr = sys.argv[3] if len(sys.argv) > 3 else ""
    inputFilePathStr = "Predators 2025 1080p AMZN WEB-DL DDP5 1 H 264-BiOMA.srt"
    if not inputFilePathStr:
        print(buildUsageMessage())
        return
    inputPathObj = Path(inputFilePathStr)
    if not inputPathObj.exists() or inputPathObj.is_dir():
        print("Input file path must be a valid .srt file.")
        print(buildUsageMessage())
        return
    
    subtitleFileManagerObj = SubtitleFileManager(inputFilePathStr)
    
    chunkSubList = list(subtitleFileManagerObj.getChunkGenerator())
    chunkSubStr = subtitleFileManagerObj.emptyStr.join(chunkSubList)
    # subtitleFileManagerObj.write(chunkData)
    
    
    translateAutomationObj = GoogleTranslateAutomation(noDriverModuleObj)
    await translateAutomationObj.start()
    subtitleFileManagerObj.readSrtByFilename()
    totalChunkCountInt = len(chunkSubList[:3])
    processedChunkList = []
    
    for chunkIndexInt, chunkStr in enumerate(chunkSubList[:3]):
        translatedChunkStr = await translateAutomationObj.translateChunk(DEFAULT_CHECK_FRAME_STR+chunkStr)
        processedChunkList.append(translatedChunkStr)
        progressBarStr = formatProgressBar(chunkIndexInt + 1, totalChunkCountInt)
        sys.stdout.write(f"\rProcessed {progressBarStr}")
        sys.stdout.flush()
    if totalChunkCountInt:
        sys.stdout.write("\n")
        sys.stdout.flush()
    newlineStr = subtitleFileManagerObj.newlineStr
    processedSubtitleTextStr = subtitleFileManagerObj.emptyStr.join(processedChunkList)
    processedSubtitleTextStr.replace(": ", ":")
    subtitleFileManagerObj.write(processedSubtitleTextStr, postFixStr="test")
    await translateAutomationObj.stop()
    
    

def runMain():
    try:
        noDriverModuleObj = importlib.import_module("nodriver")
    except ModuleNotFoundError:
        print("nodriver is required. Install with: pip install nodriver")
        return
    noDriverModuleObj.loop().run_until_complete(main(noDriverModuleObj))


if __name__ == "__main__":
    runMain()