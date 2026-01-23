DEFAULT_CHAR_LIMIT_INT = 4300
DEFAULT_OUTPUT_FOLDER_PATH_STR = "output"
DEFAULT_TRANSLATE_URL_STR = "https://translate.google.com/?sl=en&tl=sq&op=translate"
DEFAULT_CHECK_FRAME_STR = "0\n00:01:21,068 --> 00:01:23,103\n<i>If I</i>\n<i>was, you'd be naked.</i>\n\n"
SOURCE_TEXT_AREA_SELECTOR_STR = "textarea[aria-label='Source text']"
TARGET_TEXT_CONTAINER_SELECTOR_STR = 'div[jsname="r5xl4"]'
TARGET_TEXT_SELECTOR_STR = 'div[jsname="r5xl4"] span.ryNqvb'
TRANSLATION_POLL_SECONDS_FLOAT = 0.2
TRANSLATION_WAIT_TIMEOUT_SECONDS_INT = 1
SUBTITLE_CHARACTER_PER_LINE_MIN_INT = 37
SUBTITLE_CHARACTER_PER_LINE_MAX_INT = 42


# List of realistic user agents to rotate through
USER_AGENT_LIST = [
    # Chrome on macOS (Ventura / Sonoma)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",

    # Chrome on Windows 10 / 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",

    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.6; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.2; rv:132.0) Gecko/20100101 Firefox/132.0",

    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",

    # Safari on macOS (Sonoma)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",

    # Edge on Windows (Chromium-based)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
]

