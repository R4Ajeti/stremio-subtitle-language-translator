import importlib
import sys
import os

from core.service.subtitle_remote_fetcher_service import SubtitleRemoteFetcherService
from core.service.subtitle_file_manager_service import SubtitleFileManagerService
from core.service.subtitle_compliance_service import SubtitleComplianceService
from core.wrapper.user_agent_wrapper import ChromeForTestingUserAgentWrapper
from core.service.google_translate_service import GoogleTranslateService
from core import levelOneHelper, levelTwoHelper, sayHiHelper
from core import CORE_LOGGER_NAME, logger
from core.constant import (
    DEFAULT_CHECK_FRAME_STR,
)


levelOneHelper()
levelTwoHelper()
sayHiHelper()
logger.info(CORE_LOGGER_NAME)


def formatProgressBar(processedCountInt, totalCountInt, barWidthInt=30):
    if totalCountInt <= 0:
        return "[{}] 0/0".format(" " * barWidthInt)
    filledLengthInt = int(barWidthInt * processedCountInt / totalCountInt)
    filledLengthInt = min(barWidthInt, max(0, filledLengthInt))
    barStr = "#" * filledLengthInt + "-" * (barWidthInt - filledLengthInt)
    return f"[{barStr}] {processedCountInt}/{totalCountInt}"

async def main(noDriverModuleObj):
    
    testFlag = False

    criteriaDict = {
        "imdbIdStr": "tt2085059",
        "seasonNumberInt": 3,
        "episodeNumberInt": 1,
        "languageCodeStr": "en",
        "formatTypeStr": "srt",
    }

    downloadedFilePathStr = None

    if testFlag:
        testInputFolderPathStr = "test-input"
        if os.path.isdir(testInputFolderPathStr):
            testSrtFileList = sorted(
                fileNameStr
                for fileNameStr in os.listdir(testInputFolderPathStr)
                if fileNameStr.lower().endswith(".srt")
            )
            if testSrtFileList:
                downloadedFilePathStr = os.path.join(
                    testInputFolderPathStr, testSrtFileList[0]
                )

    if not downloadedFilePathStr:
        subtitleRemoteFetcherServiceObj = SubtitleRemoteFetcherService(
            inputFolderPathStr="subtitle",
            verboseBool=True,
        )

        downloadedFilePathStr = subtitleRemoteFetcherServiceObj.downloadFirstAvailableSubtitle(
            criteriaDict["imdbIdStr"],
            seasonNumberInt=criteriaDict["seasonNumberInt"],
            episodeNumberInt=criteriaDict["episodeNumberInt"],
            indexInt=3,
        )
        print(f"Subtitle downloaded to {downloadedFilePathStr}")

    # ChromeForTestingUserAgentWrapper().generate()

    subtitleFileManagerObj = SubtitleFileManagerService(downloadedFilePathStr)
        
    chunkSubList = list(subtitleFileManagerObj.getChunkGenerator())
    chunkSubStr = subtitleFileManagerObj.emptyStr.join(chunkSubList)
    # subtitleFileManagerObj.write(chunkData)

    only = None


    translateAutomationObj = GoogleTranslateService(noDriverModuleObj)
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
    processedChunkList = [chunkStr for chunkStr in processedChunkList if chunkStr is not None]
    processedSubtitleTextStr = f"{subtitleFileManagerObj.newlineStr}{subtitleFileManagerObj.newlineStr}".join(processedChunkList)
    processedSubtitleTextStr = processedSubtitleTextStr.replace(": ", ":")
    subtitleComplianceServiceObj = SubtitleComplianceService()
    processedSubtitleTextStr = subtitleComplianceServiceObj.applyComplianceToSrtText(processedSubtitleTextStr)
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