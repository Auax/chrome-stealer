import platform

if platform.system() == "Windows":
    from chrome_based import windows

elif platform.system() == "Linux":
    from chrome_based import linux
