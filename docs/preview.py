from subprocess import call
from time import sleep
from selenium import webdriver
from pathlib import Path

DRIVER_PATH = 'C:/Users/y/AppData/Local/Google/Chrome/chromedriver.exe'
SOURCE_PATH = 'source'
BUILD_PATH = 'build'
INTERVAL = 1


class Updated(Exception):
    def __init__(self, path: Path):
        self.path = path

    def __str__(self):
        return f'Updated: {str(self.path)}'


def check_modified(rst_files, mtime_dict):
    for file in rst_files:
        current = file.stat().st_mtime
        stored = mtime_dict.setdefault(file, current)

        if current > stored:
            mtime_dict[file] = current
            raise Updated(file)


def build(input):
    call(f'sphinx-build -b html {SOURCE_PATH} {BUILD_PATH} {input}')

    output = str(input).replace(
        str(Path.cwd().joinpath(SOURCE_PATH)),
        str(Path.cwd().joinpath(BUILD_PATH))
    ).replace('rst', 'html')

    return output


def main():
    files = list(Path.cwd().glob('**/*.rst'))
    if not files:
        print('No files found to monitor')
        exit(1)

    print(f'Monitoring {len(files)} files...')
    driver = webdriver.Chrome(DRIVER_PATH)

    mtime_dict = {}
    while True:
        try:
            check_modified(files, mtime_dict)
        except Updated as u:
            print(u)
            driver.get(build(u.path))

        sleep(INTERVAL)


if __name__ == '__main__':
    main()
