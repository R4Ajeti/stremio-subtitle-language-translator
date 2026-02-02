import json
import time
from pathlib import Path
from urllib import parse

from core.constant import (
    DEFAULT_INPUT_FOLDER_PATH_STR,
    REMOTE_SUBTITLE_FORMAT_DEFAULT_STR,
    REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR,
    SUBTITLE_SEARCH_ENDPOINT_STR,
)

from core.service.subtitle_file_manager_service import SubtitleFileManagerService
from core.wrapper.user_agent_wrapper import ChromeForTestingUserAgentWrapper

class SubtitleRemoteFetcherService:
    def __init__(
        self,
        inputFolderPathStr=DEFAULT_INPUT_FOLDER_PATH_STR,
        verboseBool=False,
        requestTimeoutSecondsInt=None,
    ):
        self.subtitleFileManager = SubtitleFileManagerService(inputFolderPathStr)
        self.remoteProxyObj = ChromeForTestingUserAgentWrapper(
            verboseBool=verboseBool,
            requestTimeoutSecondsInt=requestTimeoutSecondsInt,
        )

    def downloadFirstAvailableSubtitle(self, imdbIdStr, seasonNumberInt=None, episodeNumberInt=None, languageCodeStr=REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR, formatTypeStr=REMOTE_SUBTITLE_FORMAT_DEFAULT_STR, indexInt=0):
        subtitleDictList = self.fetchSubtitleDictList(imdbIdStr, seasonNumberInt, episodeNumberInt, languageCodeStr, formatTypeStr)
        if not subtitleDictList:
            raise FileNotFoundError("No subtitles available for the provided criteria.")
        firstSubtitleDict = subtitleDictList[indexInt]
        fileUrlStr = firstSubtitleDict.get("url") or ""
        fileNameStr = firstSubtitleDict.get("fileName") or self.buildDefaultFileNameStr(imdbIdStr, formatTypeStr)
        return self.downloadSubtitleAsset(fileUrlStr, fileNameStr)

    def fetchSubtitleDictList(self, imdbIdStr, seasonNumberInt=None, episodeNumberInt=None, languageCodeStr=REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR, formatTypeStr=REMOTE_SUBTITLE_FORMAT_DEFAULT_STR, retryLimitInt=3, intervalSecFloat=2.0):
        requestUrlStr = self.buildSearchUrlStr(imdbIdStr, seasonNumberInt, episodeNumberInt, languageCodeStr, formatTypeStr)
        
        intervalSecFloat = 1
        retryLimitInt = 3
        attemptInt = 0
        while attemptInt < retryLimitInt:
            attemptInt += 1
            responseObj = self.remoteProxyObj.get(requestUrlStr)
            if responseObj is None:
                raise ConnectionError("Unable to complete subtitle search request.")
            if not responseObj.ok:
                raise ConnectionError("Subtitle search request failed.")
            
            responseTextStr = responseObj.text.strip()
            
            # Retry if response is empty or just "{}"
            if not responseTextStr or responseTextStr == "{}":
                if attemptInt < retryLimitInt:
                    print(f"Empty response, retrying ({attemptInt}/{retryLimitInt})...")
                    time.sleep(intervalSecFloat)
                    continue
                else:
                    raise ValueError("Subtitle search response was empty after all retries.")
            
            try:
                subtitleDictList = json.loads(responseTextStr)
            except json.JSONDecodeError as jsonErrorObj:
                raise ValueError("Subtitle search response could not be parsed.") from jsonErrorObj
            
            if not isinstance(subtitleDictList, list):
                raise ValueError("Subtitle search response was not a list.")
            
            if not subtitleDictList:
                if attemptInt < retryLimitInt:
                    print(f"Empty list response, retrying ({attemptInt}/{retryLimitInt})...")
                    time.sleep(intervalSecFloat)
                    continue
                else:
                    raise ValueError("Subtitle search returned empty list after all retries.")
            
            return subtitleDictList
        
        raise ValueError("Subtitle search failed after all retries.")

    def buildSearchUrlStr(self, imdbIdStr, seasonNumberInt=None, episodeNumberInt=None, languageCodeStr=REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR, formatTypeStr=REMOTE_SUBTITLE_FORMAT_DEFAULT_STR):
        imdbIdentifierStr = imdbIdStr.strip()
        if not imdbIdentifierStr:
            raise ValueError("IMDb identifier is required for subtitle search.")
        normalizedLanguageCodeStr = self.normalizeLanguageCodeStr(languageCodeStr)
        normalizedFormatTypeStr = self.normalizeFormatTypeStr(formatTypeStr)
        searchQueryDict = {
            "id": imdbIdentifierStr,
            # "language": normalizedLanguageCodeStr,
            # "format": normalizedFormatTypeStr,
        }
        if seasonNumberInt is not None:
            searchQueryDict["season"] = seasonNumberInt
        if episodeNumberInt is not None:
            searchQueryDict["episode"] = episodeNumberInt
        encodedQueryStr = parse.urlencode(searchQueryDict)
        return f"{SUBTITLE_SEARCH_ENDPOINT_STR}?{encodedQueryStr}"

    def downloadSubtitleAsset(self, fileUrlStr, destinationFileNameStr):
        if not fileUrlStr:
            raise ValueError("Subtitle entry does not include a download url.")
        sanitizedFileNameStr = Path(destinationFileNameStr).name or self.buildDefaultFileNameStr("subtitle", REMOTE_SUBTITLE_FORMAT_DEFAULT_STR)
        destinationPathObj = self.subtitleFileManager.inputFolderPathObj / sanitizedFileNameStr
        responseObj = self.remoteProxyObj.get(fileUrlStr)
        if responseObj is None:
            raise ConnectionError("Unable to download subtitle asset.")
        if not responseObj.ok:
            raise ConnectionError("Subtitle asset download failed.")
        destinationPathObj.write_bytes(responseObj.content)
        return str(destinationPathObj)

    def buildDefaultFileNameStr(self, imdbIdStr, formatTypeStr):
        normalizedFormatTypeStr = self.normalizeFormatTypeStr(formatTypeStr)
        sanitizedIdentifierStr = imdbIdStr.replace(" ", "_") or "subtitle"
        return f"{sanitizedIdentifierStr}.{normalizedFormatTypeStr}"

    def normalizeLanguageCodeStr(self, languageCodeStr):
        sanitizedLanguageCodeStr = (languageCodeStr or "").strip()
        return sanitizedLanguageCodeStr or REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR

    def normalizeFormatTypeStr(self, formatTypeStr):
        sanitizedFormatTypeStr = (formatTypeStr or "").strip()
        return sanitizedFormatTypeStr or REMOTE_SUBTITLE_FORMAT_DEFAULT_STR
