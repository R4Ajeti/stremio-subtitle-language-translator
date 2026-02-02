
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import random
import json

from core.proxy.basic_remote_proxy import BasicRemoteProxy
from core.constant import (
	CHROME_BUILD_SAMPLE_COUNT_INT,
	CHROME_BUILD_SAMPLE_MAX_RANGE_INT,
	CHROME_LAST_KNOWN_GOOD_VERSIONS_URL_STR,
	CHROME_LATEST_PATCH_VERSIONS_URL_STR,
	USER_AGENT_MACHINE_LIST,
	USER_AGENT_RANDOM_OUTPUT_PATH_STR,
)
from core import logger


@dataclass
class ChromeForTestingResult:
	stableVersionStr: str
	stableBuildKeyStr: str
	stablePatchVersionStr: str
	sampledBuildKeysList: List[str]
	sampledPatchVersionsList: List[str]
	userAgentList: List[str]
	outputFilePathStr: str


class ChromeForTestingUserAgentWrapper(BasicRemoteProxy):
	def __init__(
		self,
		remoteProxyObj: Optional[BasicRemoteProxy] = None,
		sampleCountInt: int = CHROME_BUILD_SAMPLE_COUNT_INT,
		sampleRangeMaxInt: int = CHROME_BUILD_SAMPLE_MAX_RANGE_INT,
		outputFilePathStr: str = USER_AGENT_RANDOM_OUTPUT_PATH_STR,
		verboseBool: bool = False,
		requestTimeoutSecondsInt: Optional[int] = None,
	):
		self.remoteProxyObj = remoteProxyObj or BasicRemoteProxy(
			verboseBool=verboseBool,
			requestTimeoutSecondsInt=requestTimeoutSecondsInt,
		)
		self.sampleCountInt = max(1, int(sampleCountInt))
		self.sampleRangeMaxInt = max(1, int(sampleRangeMaxInt))
		self.outputFilePathStr = outputFilePathStr

	def _fetchJson(self, urlStr: str) -> Dict:
		responseObj = self.remoteProxyObj.get(urlStr)
		if responseObj is None:
			raise ConnectionError(f"Request failed: {urlStr}")
		if not responseObj.ok:
			raise ConnectionError(f"Request failed ({responseObj.status_code}): {urlStr}")
		try:
			return json.loads(responseObj.text)
		except json.JSONDecodeError as jsonErrorObj:
			raise ValueError(f"Invalid JSON response: {urlStr}") from jsonErrorObj

	def _parseVersionTuple(self, versionStr: str) -> Tuple[int, int, int]:
		partsList = [int(part) for part in versionStr.split(".") if part.isdigit()]
		while len(partsList) < 3:
			partsList.append(0)
		return (partsList[0], partsList[1], partsList[2])

	def _buildUserAgent(self, templateStr: str, versionStr: str) -> str:
		placeholderCountInt = templateStr.count("{}")
		if placeholderCountInt == 0:
			return templateStr
		return templateStr.format(*([versionStr] * placeholderCountInt))

	def _buildUserAgentList(self, versionList: List[str]) -> List[str]:
		userAgentList: List[str] = []
		for versionStr in versionList:
			templateStr = random.choice(USER_AGENT_MACHINE_LIST)
			userAgentList.append(self._buildUserAgent(templateStr, versionStr))
		return userAgentList

	def _chooseSample(self, buildKeyList: List[str], stableBuildKeyStr: str) -> List[str]:
		if not buildKeyList:
			return []
		sortedBuildKeyList = sorted(
			buildKeyList,
			key=self._parseVersionTuple,
			reverse=True,
		)
		try:
			startIndexInt = sortedBuildKeyList.index(stableBuildKeyStr)
		except ValueError:
			startIndexInt = 0
		poolList = sortedBuildKeyList[
			startIndexInt : startIndexInt + self.sampleRangeMaxInt
		]
		return poolList[: self.sampleCountInt]

	def _writeOutput(self, payloadDict: Dict) -> str:
		outputPathObj = Path(self.outputFilePathStr)
		outputPathObj.parent.mkdir(parents=True, exist_ok=True)
		outputPathObj.write_text(json.dumps(payloadDict, indent=2, ensure_ascii=False))
		return str(outputPathObj)

	def request(
        self,
        methodStr: str,
        urlStr: str,
        **kwargsDict: Any,
    ):
		return super().request(methodStr, urlStr, headersDict={"User-Agent": self.getRandomUserAgent()}, **kwargsDict)

	def getRandomUserAgent(self) -> str:
		"""Returns a random user agent from the list."""
		randomUserAgentListPath = USER_AGENT_RANDOM_OUTPUT_PATH_STR
		with open(randomUserAgentListPath, "r", encoding="utf-8") as file:
			userAgentData = json.load(file)
		randomUserAgent = random.choice(userAgentData['userAgents'])
		logger.info(f"Random User Agent: {randomUserAgent}")
		return randomUserAgent

	def generate(self) -> ChromeForTestingResult:
		versionsDict = self._fetchJson(CHROME_LAST_KNOWN_GOOD_VERSIONS_URL_STR)
		stableChannelDict = (versionsDict.get("channels") or {}).get("Stable") or {}
		stableVersionStr = stableChannelDict.get("version") or ""
		if not stableVersionStr:
			raise ValueError("Stable version not found in last-known-good response.")

		stableBuildKeyStr = ".".join(stableVersionStr.split(".")[:3])

		latestPatchDict = self._fetchJson(CHROME_LATEST_PATCH_VERSIONS_URL_STR)
		buildsDict = latestPatchDict.get("builds") or {}

		stableBuildDict = buildsDict.get(stableBuildKeyStr) or {}
		stablePatchVersionStr = stableBuildDict.get("version") or stableVersionStr

		buildKeyList = list(buildsDict.keys())
		sampledBuildKeysList = self._chooseSample(buildKeyList, stableBuildKeyStr)
		sampledPatchVersionsList = [
			(buildsDict.get(buildKeyStr) or {}).get("version") or buildKeyStr
			for buildKeyStr in sampledBuildKeysList
		]

		userAgentList = self._buildUserAgentList(sampledPatchVersionsList)
		payloadDict = {
			"stable": {
				"version": stableVersionStr,
				"build": stableBuildKeyStr,
				"patchVersion": stablePatchVersionStr,
			},
			"sample": {
				"count": self.sampleCountInt,
				"rangeMax": self.sampleRangeMaxInt,
				"buildKeys": sampledBuildKeysList,
				"patchVersions": sampledPatchVersionsList,
			},
			"userAgents": userAgentList,
		}

		outputFilePathStr = self._writeOutput(payloadDict)

		return ChromeForTestingResult(
			stableVersionStr=stableVersionStr,
			stableBuildKeyStr=stableBuildKeyStr,
			stablePatchVersionStr=stablePatchVersionStr,
			sampledBuildKeysList=sampledBuildKeysList,
			sampledPatchVersionsList=sampledPatchVersionsList,
			userAgentList=userAgentList,
			outputFilePathStr=outputFilePathStr,
		)
