from pathlib import Path
import importlib
import sys


from google_translate_automation import GoogleTranslateAutomation
from subtitle_compliance_manager import SubtitleComplianceManager
from subtitle_remote_fetcher import SubtitleRemoteFetcher
from subtitle_file_manager import SubtitleFileManager

from constants import (
    DEFAULT_CHECK_FRAME_STR,
    DEFAULT_SAMPLE_INPUT_FILE_PATH_STR,
    REMOTE_SUBTITLE_FORMAT_DEFAULT_STR,
    REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR,
)

AFFIRMATIVE_RESPONSE_LIST = ["y", "yes"]
REMOTE_DOWNLOAD_PROMPT_STR = "Download subtitle via IMDb search? (y/n): "
REMOTE_IMDB_PROMPT_STR = "Enter IMDb identifier (e.g., tt2085059): "
REMOTE_SERIES_PROMPT_STR = "Is this a series episode? (y/n): "
REMOTE_SEASON_PROMPT_STR = "Enter season number (leave blank for movie content): "
REMOTE_EPISODE_PROMPT_STR = "Enter episode number (leave blank for movie content): "
REMOTE_LANGUAGE_PROMPT_STR = "Enter subtitle language code (default en): "
REMOTE_FORMAT_PROMPT_STR = "Enter subtitle format (default srt): "
REMOTE_LOCAL_PATH_PROMPT_STR = "Provide a local subtitle path or press Enter to use the default sample: "

def buildUsageMessage():
    return "Usage: python run.py \"input.srt\" [output_folder] [char_limit]"


# def parseCharLimit(charLimitArgStr):
#     if not charLimitArgStr:
#         return DEFAULT_CHAR_LIMIT_INT
#     return int(charLimitArgStr)


def shouldDownloadSubtitleRemotely():
    userChoiceStr = input(REMOTE_DOWNLOAD_PROMPT_STR).strip().lower()
    return userChoiceStr in AFFIRMATIVE_RESPONSE_LIST


def parseOptionalIntegerValue(rawValueStr, fieldNameStr):
    strippedValueStr = rawValueStr.strip()
    if not strippedValueStr:
        return None
    try:
        return int(strippedValueStr)
    except ValueError as valueErrorObj:
        raise ValueError(f"{fieldNameStr} must be an integer.") from valueErrorObj


def collectRemoteSubtitleCriteriaDict():
    imdbIdStr = input(REMOTE_IMDB_PROMPT_STR).strip()
    if not imdbIdStr:
        raise ValueError("IMDb identifier is required to download subtitles.")
    # seriesChoiceStr = input(REMOTE_SERIES_PROMPT_STR).strip().lower()
    # isSeriesBool = seriesChoiceStr in AFFIRMATIVE_RESPONSE_LIST
    seasonNumberInt = None
    episodeNumberInt = None
    
    seasonInputStr = input(REMOTE_SEASON_PROMPT_STR)
    if seasonInputStr:
        episodeInputStr = input(REMOTE_EPISODE_PROMPT_STR)
        seasonNumberInt = parseOptionalIntegerValue(seasonInputStr, "Season number")
        episodeNumberInt = parseOptionalIntegerValue(episodeInputStr, "Episode number")
    isSeriesBool = True if episodeNumberInt else False
    
    languageInputStr = input(REMOTE_LANGUAGE_PROMPT_STR).strip()
    formatInputStr = input(REMOTE_FORMAT_PROMPT_STR).strip()
    languageCodeStr = languageInputStr or REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR
    formatTypeStr = formatInputStr or REMOTE_SUBTITLE_FORMAT_DEFAULT_STR
    criteriaDict = {
        "imdbIdStr": imdbIdStr,
        "seasonNumberInt": seasonNumberInt,
        "episodeNumberInt": episodeNumberInt,
        "languageCodeStr": languageCodeStr,
        "formatTypeStr": formatTypeStr,
    }
    return criteriaDict


def downloadSubtitleViaRemoteSearch():
    criteriaDict = collectRemoteSubtitleCriteriaDict()
    subtitleRemoteFetcherObj = SubtitleRemoteFetcher()
    downloadedFilePathStr = subtitleRemoteFetcherObj.downloadFirstAvailableSubtitle(
        criteriaDict["imdbIdStr"],
        seasonNumberInt=criteriaDict["seasonNumberInt"],
        episodeNumberInt=criteriaDict["episodeNumberInt"],
        languageCodeStr=criteriaDict["languageCodeStr"],
        formatTypeStr=criteriaDict["formatTypeStr"],
    )
    print(f"Subtitle downloaded to {downloadedFilePathStr}")
    return downloadedFilePathStr


def resolveInputFilePathStr():
    cliInputFilePathStr = sys.argv[1] if len(sys.argv) > 1 else ""
    if cliInputFilePathStr:
        return cliInputFilePathStr
    if True or shouldDownloadSubtitleRemotely():
        try:
            return downloadSubtitleViaRemoteSearch()
        except (ConnectionError, FileNotFoundError, ValueError) as remoteErrorObj:
            print(f"Remote subtitle download failed: {remoteErrorObj}")
    manualInputFilePathStr = input(REMOTE_LOCAL_PATH_PROMPT_STR).strip()
    if manualInputFilePathStr:
        return manualInputFilePathStr
    return DEFAULT_SAMPLE_INPUT_FILE_PATH_STR


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
    inputFilePathStr = resolveInputFilePathStr()
    print(f"Using input file: {inputFilePathStr}")
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