from __future__ import annotations
from pathlib import Path
from platform import system as platform_system

if platform_system() == "Windows":
    from winreg import HKEY_LOCAL_MACHINE, OpenKey as winreg_OpenKey, QueryValueEx as winreg_QueryValueEx

from .library import Library
from .login_users import LoginUser, LoginUsers

WIN_STEAM_PATH = r"c:\Program Files (x86)\Steam"


class Steam:
    """Represents the Steam client."""

    KNOWN_LINUX_PATHS = [
        Path('~/.steam/steam'),
        Path('~/.local/share/Steam'),
        Path('~/.var/app/com.valvesoftware.Steam/.steam'),
        Path('~/snap/steam/common/.local/share/Steam'),
    ]
    MACOS_PATH = Path('~/Library/Application Support/Steam')
    WINDOWS_REGISTRY_SUBKEY = r'SOFTWARE\WOW6432Node\Valve\Steam'

    def __init__(self, base_path: str|Path|None = None):
        """Magic initialization
        Base path autodetection logic, in case it's not provided."""
        self._base_path_param = base_path
        current_platform_system = platform_system()
        if base_path is not None:
            self.base_path = Path(base_path)
        elif current_platform_system == "Windows":
            with winreg_OpenKey(HKEY_LOCAL_MACHINE, self.WINDOWS_REGISTRY_SUBKEY) as hkey:
                self.base_path = Path(winreg_QueryValueEx(hkey, "InstallPath")[0])
        elif current_platform_system == "Darwin":
            macos_path = self.MACOS_PATH.expanduser().resolve()
            if macos_path.is_dir():
                self.base_path = macos_path
            else:
                raise RuntimeError('Steam client not found on this macOS system.')
        elif current_platform_system == "Linux":
            for known_path in self.KNOWN_LINUX_PATHS:
                known_path = known_path.expanduser().resolve()
                if known_path.exists():
                    self.base_path = known_path
            if not hasattr(self, 'base_path'):
                raise RuntimeError('Steam client not found on this Linux system.')
        else:
            raise NotImplementedError(f'Automatic Steam client detection in {current_platform_system} is not supported.')

    def __repr__(self) -> str:
        """Returns an eval ready python string to rebuild the current instance."""
        return f'{type(self).__name__}(base_path={repr(self._base_path_param)})'

    @property
    def app_cache(self) -> Path:
        """Returns the path to the appcache folder."""
        return self.base_path / 'appcache'

    @property
    def user_data(self) -> Path:
        """Returns the path to the userdata folder."""
        return self.base_path / 'userdata'

    @property
    def library_folders_file(self) -> Path:
        """Returns the path to the libraryfolders.vdf file."""
        return self.base_path / 'config' / 'libraryfolders.vdf'

    @property
    def library_cache(self) -> Path:
        """Returns the path to the librarycache folder."""
        return self.app_cache / 'librarycache'

    @property
    def users(self) -> list[LoginUser]:
        """Returns the current and previously logged in Steam users."""
        return LoginUsers(self.base_path).users()

    @property
    def library(self) -> Library:
        """Returns the Steam library."""
        return Library(self)
