from typing import Any, Dict, List, Optional
import logging
import random
import time

import requests

from core.constant import (
    REMOTE_REQUEST_TIMEOUT_SECONDS_INT,
    REMOTE_SUBTITLE_FORMAT_DEFAULT_STR,
    REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR,
    USER_AGENT_LIST,
)
from core import logger


class BasicRemoteProxy:
    requestsHistoryList: List[Dict[str, Any]] = []
    verboseBool: bool = False
    requestTimeoutSecondsInt: int = REMOTE_REQUEST_TIMEOUT_SECONDS_INT
    defaultSubtitleFormatStr: str = REMOTE_SUBTITLE_FORMAT_DEFAULT_STR
    defaultSubtitleLanguageStr: str = REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR
    userAgentListList: List[str] = USER_AGENT_LIST

    def __init__(
        self,
        verboseBool: Optional[bool] = None,
        requestTimeoutSecondsInt: Optional[int] = None,
        defaultSubtitleFormatStr: Optional[str] = None,
        defaultSubtitleLanguageStr: Optional[str] = None,
        userAgentListList: Optional[List[str]] = None,
    ):
        if verboseBool is not None:
            self.verboseBool = verboseBool
        if requestTimeoutSecondsInt is not None:
            self.requestTimeoutSecondsInt = requestTimeoutSecondsInt
        if defaultSubtitleFormatStr is not None:
            self.defaultSubtitleFormatStr = defaultSubtitleFormatStr
        if defaultSubtitleLanguageStr is not None:
            self.defaultSubtitleLanguageStr = defaultSubtitleLanguageStr
        if userAgentListList is not None:
            self.userAgentListList = userAgentListList


    def log(self, messageStr: str) -> None:
        if self.verboseBool:
            logger.info(messageStr)

    def buildHeaders(self, headersDict: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        mergedHeadersDict: Dict[str, str] = {}
        if self.userAgentListList:
            mergedHeadersDict["User-Agent"] = random.choice(self.userAgentListList)
        if headersDict:
            mergedHeadersDict.update(headersDict)
        return mergedHeadersDict

    def recordHistory(
        self,
        methodStr: str,
        urlStr: str,
        successBool: bool,
        elapsedSecondFloat: float,
        statusCodeInt: Optional[int] = None,
        errorStr: Optional[str] = None,
    ) -> None:
        self.__class__.requestsHistoryList.append(
            {
                "method": methodStr,
                "url": urlStr,
                "success": successBool,
                "statusCodeInt": statusCodeInt,
                "elapsedSecondFloat": elapsedSecondFloat,
                "error": errorStr,
            }
        )

    def request(
        self,
        methodStr: str,
        urlStr: str,
        *,
        paramsDict: Optional[Dict[str, Any]] = None,
        dataObj: Optional[Any] = None,
        jsonObj: Optional[Any] = None,
        headersDict: Optional[Dict[str, str]] = None,
        timeoutInt: Optional[int] = None,
        **kwargsDict: Any,
    ) -> Optional[requests.Response]:
        if not urlStr or not isinstance(urlStr, str) or not urlStr.strip():
            self.log("Request failed: empty URL")
            self.recordHistory(
                methodStr=(methodStr or ""),
                urlStr=str(urlStr),
                successBool=False,
                elapsedSecondFloat=0.0,
                errorStr="Empty URL",
            )
            return None

        methodCleanStr = (methodStr or "").strip().upper()
        if not methodCleanStr:
            self.log(f"Request failed: empty method for URL {urlStr}")
            self.recordHistory(
                methodStr=(methodStr or ""),
                urlStr=urlStr,
                successBool=False,
                elapsedSecondFloat=0.0,
                errorStr="Empty method",
            )
            return None

        chosenTimeoutInt = timeoutInt if timeoutInt is not None else self.requestTimeoutSecondsInt
        startTimeFloat = time.perf_counter()
        fullUrlStr = urlStr

        try:
            with requests.Session() as sessionObj:
                preparedObj = sessionObj.prepare_request(
                    requests.Request(
                        method=methodCleanStr,
                        url=urlStr,
                        params=paramsDict,
                        data=dataObj,
                        json=jsonObj,
                        headers=self.buildHeaders(headersDict),
                    )
                )
                fullUrlStr = preparedObj.url or urlStr
                responseObj = sessionObj.send(preparedObj, timeout=chosenTimeoutInt, **kwargsDict)
            elapsedSecondFloat = time.perf_counter() - startTimeFloat
            self.recordHistory(
                methodStr=methodCleanStr,
                urlStr=fullUrlStr,
                successBool=responseObj.ok,
                statusCodeInt=responseObj.status_code,
                elapsedSecondFloat=elapsedSecondFloat,
            )
            if responseObj.ok:
                self.log(f"Request succeeded: {fullUrlStr} ({elapsedSecondFloat:.3f}s)")
            else:
                self.log(
                    f"Request failed: {fullUrlStr} (status {responseObj.status_code}, {elapsedSecondFloat:.3f}s)"
                )
            return responseObj
        except Exception as excObj:
            elapsedSecondFloat = time.perf_counter() - startTimeFloat
            self.recordHistory(
                methodStr=methodCleanStr,
                urlStr=fullUrlStr,
                successBool=False,
                elapsedSecondFloat=elapsedSecondFloat,
                errorStr=str(excObj),
            )
            self.log(f"Request failed: {fullUrlStr} ({elapsedSecondFloat:.3f}s) {excObj}")
            return None

    def get(self, urlStr: str, **kwargsDict: Any) -> Optional[requests.Response]:
        return self.request("GET", urlStr, **kwargsDict)

    def post(self, urlStr: str, **kwargsDict: Any) -> Optional[requests.Response]:
        return self.request("POST", urlStr, **kwargsDict)

    def put(self, urlStr: str, **kwargsDict: Any) -> Optional[requests.Response]:
        return self.request("PUT", urlStr, **kwargsDict)

    def delete(self, urlStr: str, **kwargsDict: Any) -> Optional[requests.Response]:
        return self.request("DELETE", urlStr, **kwargsDict)


