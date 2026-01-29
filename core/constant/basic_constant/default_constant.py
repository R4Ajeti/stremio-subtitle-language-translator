CORE_LOGGER_NAME="StremioGoogleTranslateAddonLogger"

DEFAULT_CHAR_LIMIT_INT = 4300
DEFAULT_INPUT_FOLDER_PATH_STR = "input"
DEFAULT_OUTPUT_FOLDER_PATH_STR = "output"
DEFAULT_SAMPLE_INPUT_FILE_PATH_STR = "input/Black-Mirror-season-2/Black Mirror - 2x01 - Be Right Back.WEB-DL.FoV.en.srt"
DEFAULT_TRANSLATE_URL_STR = "https://translate.google.com/?sl=en&tl=sq&op=translate"
DEFAULT_CHECK_FRAME_STR = "0\n00:01:21,068 --> 00:01:23,103\n<i>If I</i>\n<i>was, you'd be naked.</i>\n\n"
SUBTITLE_SEARCH_ENDPOINT_STR = "https://sub.wyzie.ru/search"
REMOTE_REQUEST_TIMEOUT_SECONDS_INT = 30
REMOTE_SUBTITLE_LANGUAGE_DEFAULT_STR = "en"
REMOTE_SUBTITLE_FORMAT_DEFAULT_STR = "srt"
SOURCE_TEXT_AREA_SELECTOR_STR = "textarea[aria-label='Source text']"
TARGET_TEXT_CONTAINER_SELECTOR_STR = 'div[jsname="r5xl4"]'
TARGET_TEXT_SELECTOR_STR = 'div[jsname="r5xl4"] span.ryNqvb'
TRANSLATION_POLL_SECONDS_FLOAT = 0.2
TRANSLATION_WAIT_TIMEOUT_SECONDS_INT = 1
SUBTITLE_CHARACTER_PER_LINE_MIN_INT = 37
SUBTITLE_CHARACTER_PER_LINE_MAX_INT = 42

CHROME_LAST_KNOWN_GOOD_VERSIONS_URL_STR = (
    "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json"
)
CHROME_LATEST_PATCH_VERSIONS_URL_STR = (
    "https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json"
)
CHROME_BUILD_SAMPLE_COUNT_INT = 10
CHROME_BUILD_SAMPLE_MAX_RANGE_INT = 100
USER_AGENT_RANDOM_OUTPUT_PATH_STR = "random-user-agent-list.json"


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

# USER_AGENT_LIST_NEW = [
#     # macOS (Tahoe, Sequoia, Sonoma, Ventura)
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 26_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.109 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 26_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.96 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_5_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.60 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.59 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.31 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.20 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_7_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.12 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.4 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 26_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.3 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.2 Safari/537.36",

#     # Windows (11 & 10)
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.109 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.96 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.60 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.59 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.31 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.20 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.12 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; ARM64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.4 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.3 Safari/537.36 Edg/144.0.7559.3",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.2 Safari/537.36",

#     # Linux (Ubuntu, Debian, Fedora, Arch, ChromeOS)
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.109 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.96 Safari/537.36",
#     "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.60 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.59 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.31 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.20 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.12 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.4 Safari/537.36",
#     "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.3 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.2 Safari/537.36"
# ]

USER_AGENT_MACHINE_LIST = [
    # macOS (Tahoe, Sequoia, Sonoma, Ventura)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 26_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 26_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 26_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_5_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_7_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",

    # Windows (11 & 10)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; ARM64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36 Edg/{}",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",

    # Linux (Ubuntu, Debian, Fedora, Arch, ChromeOS)
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36"
    
]
