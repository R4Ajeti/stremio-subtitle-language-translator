import json
import random
from pathlib import Path
from urllib import error, parse, request

from constants import (
    DEFAULT_INPUT_FOLDER_PATH_STR,
    REMOTE_REQUEST_TIMEOUT_SECONDS_INT,
    REMOTE_SUBTITLE_FORMAT_DEFAULT_STR,
    REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR,
    SUBTITLE_SEARCH_ENDPOINT_STR,
    USER_AGENT_LIST,
)


class SubtitleRemoteFetcher:
    def __init__(self, inputFolderPathStr=DEFAULT_INPUT_FOLDER_PATH_STR):
        self.inputFolderPathObj = Path(inputFolderPathStr)
        self.inputFolderPathObj.mkdir(parents=True, exist_ok=True)

    def downloadFirstAvailableSubtitle(self, imdbIdStr, seasonNumberInt=None, episodeNumberInt=None, languageCodeStr=REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR, formatTypeStr=REMOTE_SUBTITLE_FORMAT_DEFAULT_STR):
        subtitleDictList = self.fetchSubtitleDictList(imdbIdStr, seasonNumberInt, episodeNumberInt, languageCodeStr, formatTypeStr)
        if not subtitleDictList:
            raise FileNotFoundError("No subtitles available for the provided criteria.")
        firstSubtitleDict = subtitleDictList[0]
        fileUrlStr = firstSubtitleDict.get("url") or ""
        fileNameStr = firstSubtitleDict.get("fileName") or self.buildDefaultFileNameStr(imdbIdStr, formatTypeStr)
        return self.downloadSubtitleAsset(fileUrlStr, fileNameStr)

    def fetchSubtitleDictList(self, imdbIdStr, seasonNumberInt=None, episodeNumberInt=None, languageCodeStr=REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR, formatTypeStr=REMOTE_SUBTITLE_FORMAT_DEFAULT_STR):
        requestUrlStr = self.buildSearchUrlStr(imdbIdStr, seasonNumberInt, episodeNumberInt, languageCodeStr, formatTypeStr)
        requestHeadersDict = {"User-Agent": self.buildRandomUserAgentStr()}
        requestObj = request.Request(requestUrlStr, headers=requestHeadersDict)
        try:
            with request.urlopen(requestObj, timeout=REMOTE_REQUEST_TIMEOUT_SECONDS_INT) as responseObj:
                responseBodyBytes = responseObj.read()
        except error.URLError as errorObj:
            raise ConnectionError("Unable to complete subtitle search request.") from errorObj
        try:
            subtitleDictList = json.loads(responseBodyBytes.decode("utf-8"))
        except json.JSONDecodeError as jsonErrorObj:
            raise ValueError("Subtitle search response could not be parsed.") from jsonErrorObj
        if not isinstance(subtitleDictList, list):
            raise ValueError("Subtitle search response was not a list.")
        return subtitleDictList

    def buildSearchUrlStr(self, imdbIdStr, seasonNumberInt=None, episodeNumberInt=None, languageCodeStr=REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR, formatTypeStr=REMOTE_SUBTITLE_FORMAT_DEFAULT_STR):
        imdbIdentifierStr = imdbIdStr.strip()
        if not imdbIdentifierStr:
            raise ValueError("IMDb identifier is required for subtitle search.")
        normalizedLanguageCodeStr = self.normalizeLanguageCodeStr(languageCodeStr)
        normalizedFormatTypeStr = self.normalizeFormatTypeStr(formatTypeStr)
        searchQueryDict = {
            "id": imdbIdentifierStr,
            "language": normalizedLanguageCodeStr,
            "format": normalizedFormatTypeStr,
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
        destinationPathObj = self.inputFolderPathObj / sanitizedFileNameStr
        assetRequestHeadersDict = {"User-Agent": self.buildRandomUserAgentStr()}
        assetRequestObj = request.Request(fileUrlStr, headers=assetRequestHeadersDict)
        try:
            with request.urlopen(assetRequestObj, timeout=REMOTE_REQUEST_TIMEOUT_SECONDS_INT) as responseObj:
                destinationPathObj.write_bytes(responseObj.read())
        except error.URLError as errorObj:
            raise ConnectionError("Unable to download subtitle asset.") from errorObj
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

    def buildRandomUserAgentStr(self):
        return random.choice(USER_AGENT_LIST)
