import os
import json
from subprocess import run
from traceback import format_exc
from urllib.error import HTTPError
from ansible.module_utils.urls import open_url
from ansible.module_utils.basic import AnsibleModule


class StrError(RuntimeError):
    pass


class Pacman:
    def run(self, params):
        res = run(["/usr/bin/pacman"] + params, capture_output=True)
        res.check_returncode()
        return {it.strip() for it in res.stdout.decode("utf-8").split('\n') if it.strip() != ""}

    def is_run_success(self, params):
        res = run(["/usr/bin/pacman"] + params, capture_output=True)
        return not res.returncode

    def get_db_groups(self):
        return self.run(["-Sg"])

    def get_db_packages(self):
        return self.run(["-Slq"])

    def get_local_packages(self):
        return self.run(["-Qq"])

    def get_local_explicit_packages(self):
        return self.run(["-Qeq"])

    def get_db_packages_for_groups(self, group_names):
        if len(group_names) == 0:
            return set()

        return { line.split()[1] for line in self.run(["-Sg"] + list(group_names)) }

    def get_local_packages_for_groups(self, group_names):
        if len(group_names) == 0:
            return set()

        return { line.split()[1] for line in self.run(["-Qg"] + list(group_names)) }


class Aur:
    def open_url(self, url):
        try:
            return open_url(url)
        except HTTPError as e:
            e.msg = "{} (url = {})".format(e.msg, url)
            raise e

    def get_db_packages(self):
        import zlib

        url = "https://aur.archlinux.org/packages.gz"
        text = zlib.decompress(self.open_url(url).read(), 16 + zlib.MAX_WBITS).decode("utf-8")
        return {it.strip() for it in text.split() if it.strip() != ""}

    def get_package_load_url(self, name):
        url = "https://aur.archlinux.org/rpc/?v=5&type=info&arg={}".format(name)
        result = json.loads(self.open_url(url).read().decode("utf-8"))
        if result["resultcount"] != 1:
            raise StrError("Package '{}' not found".format(name))
        return "https://aur.archlinux.org/{}".format(result["results"][0]["URLPath"])


class InstallManager:
    def __init__(self, aur, module):
        self._aur = aur
        self._module = module
        self._installed_packages = []

    @property
    def installed_packages(self):
        return self._installed_packages

    def install_by_makepkg(self, name):
        import tarfile
        import tempfile

        url = self._aur.get_package_load_url(name)
        f = self._aur.open_url(url)
        with tempfile.TemporaryDirectory() as tmpdir:
            install_dir = os.path.join(tmpdir, name)
            tar_file_path = os.path.join(tmpdir, "{}.tar.gz".format(name))
            with open(tar_file_path, 'wb') as out:
                out.write(f.read())
            tar = tarfile.open(tar_file_path)
            tar.extractall(tmpdir)
            tar.close()

            params = ["makepkg", "--syncdeps", "--install", "--noconfirm", "--skippgpcheck",
                      "--needed"]
            rc, stdout, stderr = self._module.run_command(params, cwd=install_dir)
            if rc != 0:
                msg = "Failed to install '{}', stdout: {}, stderr: {}".format(name, stdout, stderr)
                raise StrError(msg)

            self._installed_packages.append(name)

    def install_by_yay(self, name, as_explicitly):
        params = ["env", "LC_ALL=C", "yay", "-S", "--noconfirm"]
        if as_explicitly is not None:
            if as_explicitly:
                params += ["--asexplicit"]
            else:
                params += ["--asdeps"]

        rc, stdout, stderr = self._module.run_command(params + [name])
        if rc != 0:
            msg = "Failed to install '{}', stdout: {}, stderr: {}".format(name, stdout, stderr)
            raise StrError(msg)

        self._installed_packages.append(name)


def install(module, packages):
    aur = Aur()
    pacman = Pacman()
    mng = InstallManager(aur, module)

    packages = {it.strip() for it in packages}
    packages.difference_update(pacman.get_local_explicit_packages())

    if "yay" in packages:
        mng.install_by_makepkg("yay")
        packages.discard("yay")

    for name in packages:
        mng.install_by_yay(name, True)

    cnt = len(mng.installed_packages)
    if cnt != 0:
        msg = "Installed {} package(s): {}".format(cnt, ",".join(mng.installed_packages))
        changed = True
    else:
        msg = "Package(s) already installed"
        changed = False

    return msg, changed


def get_info(packages, groups):
    # ошибочные названия среди groups (groups_name_wrong)
    # ошибочные названия среди packages (packages_name_wrong)
    # неустановленные среди packages (packages_not_installed)
    # установленные как не explicit среди packages (packages_not_explicit)
    # новые explicit пакеты, которых нет среди packages и пакетов groups (packages_new)
    # пакеты среди packages, которые находятся в aur (packages_aur)
    # пакеты среди packages, которые относятся к пакетам в groups (packages_in_group)
    # пакеты входящие в groups, но не установленные (packages_not_installed_in_group)

    packages = {it.strip() for it in packages}
    groups = {it.strip() for it in groups}
    pacman = Pacman()
    aur = Aur()

    db_groups = pacman.get_db_groups()
    db_packages = pacman.get_db_packages()
    aur_packages = aur.get_db_packages()
    local_packages = pacman.get_local_packages()
    local_explicit_packages = pacman.get_local_explicit_packages()
    db_packages_for_groups = pacman.get_db_packages_for_groups(groups)
    local_packages_for_groups = pacman.get_local_packages_for_groups(groups)

    groups_name_wrong = groups.difference(db_groups)
    packages_name_wrong = packages.difference(db_packages, aur_packages)
    packages_not_installed = packages.difference(local_packages)
    packages_not_explicit = packages.difference(local_explicit_packages)
    packages_new = local_explicit_packages.difference(packages, local_packages_for_groups)
    packages_aur = aur_packages.intersection(packages)
    packages_in_group = local_packages_for_groups.intersection(packages)
    packages_not_installed_in_group = db_packages_for_groups.difference(local_packages_for_groups)

    return {
        "groups_name_wrong": list(groups_name_wrong),
        "packages_name_wrong": list(packages_name_wrong),
        "packages_not_installed": list(packages_not_installed),
        "packages_not_explicit": list(packages_not_explicit),
        "packages_new": list(packages_new),
        "packages_aur": list(packages_aur),
        "packages_in_group": list(packages_in_group),
        "packages_not_installed_in_group": list(packages_not_installed_in_group),
        "changed": False
    }


def run_module(module):
    command = module.params["command"].strip()

    if command == "install":
        name = module.params.get("name", None)
        if name is None:
            raise StrError("Not found required param 'name' for command 'install'")
        else:
            msg, changed = install(module, name)
            return {
                "msg": msg,
                "changed": changed,
            }
    elif command == "get_info":
        packages = module.params.get("packages", None)
        groups = module.params.get("groups", None)
        if packages is None:
            raise StrError("Not found required param 'packages' for command '{}'".format(command))
        elif groups is None:
            raise StrError("Not found required param 'groups' for command '{}'".format(command))
        else:
            return get_info(packages, groups)
    else:
        raise StrError("Param 'command' has unexpected value '{}'".format(command))


# pkg_manager: command=install name=dropbox
# pkg_manager: command=install name=yay, python
# pkg_manager: command=get_info packages=python2,python groups=base
def main():
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(default=None, choices=["install", "get_info"], required=True, type="str"),
            name=dict(default=None, required=False, type="list"),
            packages=dict(default=None, required=False, type="list"),
            groups=dict(default=None, required=False, type="list")
            ),
        supports_check_mode=False)

    result = {}
    try:
        result = run_module(module)
    except StrError as e:
        module.fail_json(msg="Error in library/pkg_manager: " + str(e))
    except Exception:
        module.fail_json(msg="Exception in library/pkg_manager", exception=format_exc())

    module.exit_json(**result)


if __name__ == '__main__':
    main()
