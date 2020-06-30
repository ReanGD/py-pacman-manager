# global x86_64, hostname_id, distro, network_type, virtualization, gui, develop, monitoring, roles

def system_pkgs():
    system_pkgs = ["base",
                   "polkit",
                   "gnupg",
                   "wget",
                   "curl",
                   "git",
                   "rsync",
                   "logrotate",
                   "nano",
                   "vim",
                   "pacutils",
                   "pkgfile",  # pkgfile makepkg (get package for makepkg)
                   "dialog",
                   "libnewt",  # external dialog
                   "ansible",
                   "mlocate",
                   "man-db"]

    # terminal
    system_pkgs += ["urxvt-perls",
                    "zsh",
                    "oh-my-zsh-git",
                    "zsh-syntax-highlighting",
                    "fzf"]

    # archivers
    system_pkgs += ["p7zip", "unzip", "unrar"]

    if x86_64:
        system_pkgs += ["yay",  # AUR package manager
                        "refind",  # UEFI boot manager
                        "pkgcacheclean"]  # clean the pacman cache

    return system_pkgs

def driver_pkgs():
    driver_pkgs = []

    if gui != "none":
        driver_pkgs = ["mesa"]

    if hostname_id == "archhost":
        driver_pkgs += ["nvidia"]
    elif hostname_id == "archnote":
        driver_pkgs += ["bbswitch",
                        # "bumblebee",
                        # "nvidia",
                        "xf86-video-intel",
                        "xf86-input-libinput"]  # touchpad

    return driver_pkgs

def network_pkgs():
    network_pkgs = ["netctl",  # arch specific network manager
                    "net-tools",
                    "bind-tools",  # dig and etc
                    "smbclient",
                    "httpie",
                    "openvpn",
                    "openssh"]  # ssh server

    if "wifi" in network_type.split(","):
        network_pkgs += ["connman", "wpa_supplicant"]

    return network_pkgs

def virtualization_pkgs():
    if virtualization == "kvm_qemu":
        return ["qemu",
                "virt-viewer",  # for SPICE
                "edk2-ovmf"]  # for UEFI
    elif virtualization == "kvm_libvirt":
        return ["qemu",
                "libvirt",  # additional interface
                "virt-viewer",  # for SPICE
                "virt-manager",  # GUI for libvirt
                "edk2-ovmf",  # for UEFI
                "ebtables",  # for network
                "dnsmasq",  # for network
                "python-lxml"]  # for ansible
    else:
        return []

def gui_pkgs():
    if gui == "none":
        return []

    gui_pkgs = ["xorg-server",
                "xorg-xinit",
                "xorg-xfontsel",  # font select
                "xorg-xprop",  # window info (xprop | grep WM_CLASS)
                "xorg-xev",  # keypress info
                "xorg-xwininfo",  # select window
                "xcursor-ize-vision",  # a couple of X cursor that similar to Windows 7 cursor
                "perwindowlayoutd",  # daemon to make per window layout (also exists "kbdd-git")
                "libnotify",  # create notifications message
                "xrectsel"]  # get select region

    guis = gui.split(",")
    if "lightdm" in guis:
        gui_pkgs += ["lightdm", "lightdm-gtk-greeter"]

    if "awesome" in guis:
        gui_pkgs += ["awesome",
                     "vicious",
                     "rofi"]  # run app menu

    if "cinnamon" in guis:
        gui_pkgs += ["cinnamon"]

    if "notebook" in guis:
        gui_pkgs += ["xorg-xbacklight"]  # backlight control application (xbacklight -set 40)

    return gui_pkgs

def develop_pkgs():
    if develop == "none":
        return []

    develop_pkgs = []
    develops = develop.split(",")
    if "std" in develops:
        # "pycharm-community-edition", "pycharm-professional", "clion", "clion-cmake"
        develop_pkgs += ["git",
                         "icdiff",  # console diff
                         "meld",
                         "emacs",
                         "sublime-text-dev",
                         "visual-studio-code-bin"]

    if "cpp" in develops:
        develop_pkgs += ["clang",
                         "cmake",
                         "ninja",
                         "gdb",
                         "cpp-dependencies",
                         "python-dateutil", # for include-what-you-use
                         "include-what-you-use"]

    if "python" in develops:
        develop_pkgs += ["python",
                         "python-pip",
                         "python-nose",
                         "python-jedi",
                         "python-pylint",
                         "flake8",
                         "python-pytest",
                         "python-termcolor",
                         "python-virtualenv",
                         "tk",
                         "swig",
                         "portaudio"]  # for pyaudio and my audio-lib

    if "go" in develops:
        develop_pkgs += ["go"]

    if "rust" in develops:
        develop_pkgs += ["rust", "cargo", "rust-src", "rust-racer"]

    if "rust3D" in develops:
        develop_pkgs += ["sdl2", "sdl2_image"]

    if "protobuf" in develops:
        develop_pkgs += ["protobuf"]

    if "sqlite" in develops:
        develop_pkgs += ["sqlite-analyzer"]

    if "android" in develops:
        develop_pkgs += ["adb"]

    return develop_pkgs

def monitoring_pkgs():
    if monitoring == "none":
        return []

    monitoring_pkgs = []
    if "std" in monitoring.split(","):
        monitoring_pkgs += ["iftop",  # network monitor
                            "htop",  # process monitor
                            "iotop",  # disk monitor
                            "hwinfo"]  # info about hardware

        if x86_64:
            monitoring_pkgs+=["hw-probe"]  # check hardware and find drivers

    if "notebook" in monitoring.split(","):
        monitoring_pkgs+=["powertop"]

    if "hddtemp" in monitoring.split(","):
        monitoring_pkgs+=["hddtemp",  # disk temperature
                          "smartmontools"]

    if "ups" in monitoring.split(","):
        monitoring_pkgs+=["apcupsd"]

    return monitoring_pkgs

def font_pkgs():
    if "font" not in roles.split(","):
        return []
    return ["font-manager",  # viewer for fonts
            "ttf-ms-fonts",
            "ttf-tahoma",
            # "ttf-vista-fonts",
            "ttf-fixedsys-excelsior-linux",
            "ttf-droid",
            "ttf-dejavu",
            "ttf-ubuntu-font-family",
            "noto-fonts-emoji",  # emoji for chrome
            "adobe-source-code-pro-fonts"]

def docker_pkgs():
    if "docker" not in roles.split(","):
        return []
    return ["docker", "docker-compose"]

def automount_pkgs():
    if "automount" not in roles.split(","):
        return []
    return ["nfs-utils"]

def web_pkgs():
    if "web" not in roles.split(","):
        return []
    return ["firefox", "firefox-i18n-ru", "google-chrome"]

def game_pkgs():
    if "game" not in roles.split(","):
        return []
    return ["playonlinux",
            "steam",
            "lib32-nvidia-utils",  # for steam
            "lib32-libldap",  # for WOT ?
            "minecraft"]

def messengers_pkgs():
    if "game" not in roles.split(","):
        return []
    return ["telegram-desktop", "slack-desktop"]

def audio_pkgs():
    if "audio" not in roles.split(","):
        return []

    audio_pkgs = ["pulseaudio"]

    if gui != "none":
        audio_pkgs += ["pavucontrol", "volumeicon"]

    return audio_pkgs

def media_pkgs():
    if "media" not in roles.split(","):
        return []

    return ["viewnior",  # image viewer
            "gimp",
            "blender",
            "smplayer",
            "deadbeef"]

def pdf_pkgs():
    if "pdf" not in roles.split(","):
        return []

    return ["mupdf"]  # pdf viewer (analog: llpp-git)

def office_pkgs():
    if "office" not in roles.split(","):
        return []

    return ["libreoffice-fresh-ru"]

def file_managers_pkgs():
    if "file_managers" not in roles.split(","):
        return []

    file_managers_pkgs = ["doublecmd-gtk2",
                          "fsearch-git",
                          "yandex-disk",  # yandex-disk setup/start
                          "dropbox"]

    if hostname_id == "archhost":
        file_managers_pkgs += ["transmission-remote-gui"]  # transmission-remote-gui-bin - not work now

    return file_managers_pkgs

def spell_checkers_pkgs():
    if "spell_checkers" not in roles.split(","):
        return []

    return ["enchant", "hunspell-en_US", "hunspell-ru-aot", "languagetool"]

def plex_pkgs():
    if "plex" not in roles.split(","):
        return []

    return ["plex-media-server"]

def work_pkgs():
    if "work" not in roles.split(","):
        return []

    return ["openconnect"] # for vpn to work

grps = ["base-devel"]

pkgs = []
pkgs += system_pkgs()
pkgs += driver_pkgs()
pkgs += network_pkgs()
pkgs += virtualization_pkgs()
pkgs += gui_pkgs()
pkgs += develop_pkgs()
pkgs += monitoring_pkgs()
pkgs += font_pkgs()
pkgs += docker_pkgs()
pkgs += automount_pkgs()
pkgs += web_pkgs()
pkgs += game_pkgs()
pkgs += messengers_pkgs()
pkgs += audio_pkgs()
pkgs += media_pkgs()
pkgs += pdf_pkgs()
pkgs += office_pkgs()
pkgs += spell_checkers_pkgs()
pkgs += file_managers_pkgs()
pkgs += plex_pkgs()
pkgs += work_pkgs()

packages = pkgs
groups = grps
