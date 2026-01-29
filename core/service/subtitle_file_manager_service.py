from datetime import datetime
from pathlib import Path
import re

from core.constant import DEFAULT_CHAR_LIMIT_INT, DEFAULT_OUTPUT_FOLDER_PATH_STR


class SubtitleFileManagerService:
    emptyStr = ""
    newlineStr = "\n"
    newlineDosStr = "\r\n"
    
    def __init__(self, inputFilePathStr):
        self.inputFilePathStr = inputFilePathStr
        self.subtitleTextStr = ""
        self.subtitleFrameList = []
        self.currentFrameIndexInt = 0
        
        self.emptyStr = SubtitleFileManagerService.emptyStr
        self.newlineStr = SubtitleFileManagerService.newlineStr
        self.newlineDosStr = SubtitleFileManagerService.newlineDosStr
        self.inputFilePathObj = Path(self.inputFilePathStr)
        self.inputFolderParentNameStr = self.inputFilePathObj.parent
        if self.inputFilePathObj.is_file():
            self.inputFolderPathObj = self.inputFilePathObj.parent
        else:
            self.inputFolderPathObj = self.inputFilePathObj
            self.inputFolderPathObj.mkdir(parents=True, exist_ok=True)
        self.inputFileNameStr = self.inputFilePathObj.name
        self.inputBaseNameStr = self.inputFilePathObj.stem

    def readSrtByFilename(self):
        if not self.inputFilePathObj.is_file():
            raise FileNotFoundError(f"Subtitle file not found: {self.inputFilePathObj}")
        self.subtitleTextStr = self.inputFilePathObj.read_text(encoding="utf-8")
        if "\r\n" in self.subtitleTextStr:
            self.newlineStr = "\r\n"
        self.subtitleFrameList = self.splitIntoFrame(self.subtitleTextStr)
        self.currentFrameIndexInt = 0
        return self.subtitleTextStr

    def getChunkGenerator(self, charLimitInt=DEFAULT_CHAR_LIMIT_INT):
        if not self.subtitleFrameList:
            self.readSrtByFilename()

        self.currentFrameIndexInt = 0

        while self.currentFrameIndexInt < len(self.subtitleFrameList):
            chunkFrameList = []
            currentCharCountInt = 0

            while self.currentFrameIndexInt < len(self.subtitleFrameList):
                subtitleFrameStr = self.subtitleFrameList[self.currentFrameIndexInt]
                projectedLengthInt = currentCharCountInt + len(subtitleFrameStr)

                if projectedLengthInt > charLimitInt and chunkFrameList:
                    break

                chunkFrameList.append(subtitleFrameStr)
                currentCharCountInt = projectedLengthInt
                self.currentFrameIndexInt += 1

                if currentCharCountInt >= charLimitInt:
                    break

            yield "".join(chunkFrameList)

    def splitIntoFrame(self, subtitleTextStr):
        if not subtitleTextStr.strip():
            return []
        subtitleFrameList = re.findall(r".*?(?:\r?\n\r?\n+|$)", subtitleTextStr, flags=re.DOTALL)
        subtitleFrameList = [frameStr for frameStr in subtitleFrameList if frameStr.strip()]
        return subtitleFrameList

    def writeSubtitleTextToFile(self, subtitleTextStr, outputFolderPathStr=DEFAULT_OUTPUT_FOLDER_PATH_STR, preFixStr="", postFixStr=""):
        outputFolderPathObj = Path(outputFolderPathStr)
        outputFolderPathObj.mkdir(parents=True, exist_ok=True)
        timestampStr = datetime.now().strftime("%Y-%m-%d--%H-%M")
        if postFixStr:
            postFixStr = f"-{postFixStr}"
        if preFixStr:
            preFixStr = f"{preFixStr}-"
        outputFileNameStr = f"{preFixStr}{self.inputBaseNameStr}{postFixStr}-{timestampStr}.srt"
        outputFilePathObj = outputFolderPathObj / outputFileNameStr
        outputFilePathObj.write_text(f"{subtitleTextStr}", encoding="utf-8")
        return str(outputFilePathObj)
    
    def write(self, *args, **kwargs):
        return self.writeSubtitleTextToFile(*args, **kwargs)



