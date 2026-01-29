import logging

import core

logger = logging.getLogger(core.constant.CORE_LOGGER_NAME)
logging.basicConfig(level=logging.NOTSET)

def sayHiHelper():
    logger.info("Hey From Helper")

def safeImportSingle(importLine, globalScope):
    importLineList = importLine.split(' ')
    importName = importLineList[-1].split('.')[0]
    try:
        # if len(importLineList) > 2:
        #     importLine = f"import {importLineList[1]}.{importName} as {importName}"
        exec(importLine, globalScope)
        globalScope[f"{importName}Flag"] = True
        print(f"We successfully imported {importName}Flag")
    except Exception as e:
        print(f"We couldn't import {importName}: {e}")
        globalScope[f"{importName}Flag"] = False

def safeImport(importLineList, globalScope = globals()):
    if isinstance(importLineList, str):
        importLineList = [importLineList]
    for importLine in importLineList:
        safeImportSingle(importLine, globalScope)