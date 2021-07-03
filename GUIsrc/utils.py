import platform

CONFIGURATION_FILES = {
    "Windows": {
        "styleSheet": "styleWin.qss"
    },
    "Linux": {
        "styleSheet": "styleLinux.qss"
    },
    "Darwin": {
        "styleSheet": "styleLinux.qss"
    }
}


def set_style_sheet(window, error_message=None):
    """
    set style from configuration
    """
    try:
        window.setStyleSheet(open(CONFIGURATION_FILES[platform.system()]["styleSheet"], "r").read())
    except:
        print(error_message)