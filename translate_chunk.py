import importlib
import random
import sys
from pathlib import Path


from google_translate_automation import GoogleTranslateAutomation
from subtitle_compliance_manager import SubtitleComplianceManager
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
    inputFilePathStr = inputFilePathStr if inputFilePathStr else "input/Black-Mirror-season-2/Black Mirror - 2x01 - Be Right Back.WEB-DL.FoV.en.srt"
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
    
    only = None
    
    
    translateAutomationObj = GoogleTranslateAutomation(noDriverModuleObj)
    await translateAutomationObj.start()
    subtitleFileManagerObj.readSrtByFilename()
    totalChunkCountInt = len(chunkSubList[:only])
    processedChunkList = []
    
    for chunkIndexInt, chunkStr in enumerate(chunkSubList[:only]):
        translatedChunkStr = await translateAutomationObj.translateChunk(DEFAULT_CHECK_FRAME_STR+chunkStr)
        processedChunkList.append(translatedChunkStr)
        progressBarStr = formatProgressBar(chunkIndexInt + 1, totalChunkCountInt)
        sys.stdout.write(f"\rProcessed {progressBarStr}")
        sys.stdout.flush()
    if totalChunkCountInt:
        sys.stdout.write("\n")
        sys.stdout.flush()
    processedSubtitleTextStr = f"{subtitleFileManagerObj.newlineStr}{subtitleFileManagerObj.newlineStr}".join(processedChunkList)
    processedSubtitleTextStr = processedSubtitleTextStr.replace(": ", ":")
    subtitleComplianceManagerObj = SubtitleComplianceManager()
    processedSubtitleTextStr = subtitleComplianceManagerObj.applyComplianceToSrtText(processedSubtitleTextStr)
    subtitleFileManagerObj.write(processedSubtitleTextStr, postFixStr="al")
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