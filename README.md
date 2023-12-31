<a href="https://choosealicense.com/licenses/agpl-3.0/"><img src="https://img.shields.io/github/license/AlbertUnruh/SSD-roster?label=License"  alt="[License]"></a></br>
<img src="https://img.shields.io/github/checks-status/AlbertUnruh/SSD-roster/develop?label=Checks&logo=GitHub" alt="[Checks]">
<a href="https://results.pre-commit.ci/latest/github/AlbertUnruh/SSD-roster/develop"><img src="https://results.pre-commit.ci/badge/github/AlbertUnruh/SSD-roster/develop.svg" alt="[precommit.ci]"></a>
</br>
<a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/Code%20Style-black-000000.svg" alt="[Code Style: black]"></a>
<img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FAlbertUnruh%2FSSD-roster%2Fdevelop%2FPipfile.lock&query=%24._meta.requires.python_full_version&logo=python&label=Python%20Version" alt="[Python Version]">
<a href="https://www.python.org"><img src="https://img.shields.io/github/languages/top/AlbertUnruh/SSD-roster?label=Python&logo=Python" alt="[Top Language: Python]"></a>
</br>
<img src="https://img.shields.io/github/issues-pr-raw/AlbertUnruh/SSD-roster?label=Open%20PRss" alt="[Open PRs]">
<img src="https://img.shields.io/github/issues-pr-closed-raw/AlbertUnruh/SSD-roster?label=Closed%20PRs" alt="[Closed PRs]">
<img src="https://img.shields.io/github/issues-raw/AlbertUnruh/SSD-roster?label=Open%20Issues" alt="[Open Issues]">
<img src="https://img.shields.io/github/issues-closed-raw/AlbertUnruh/SSD-roster?label=Closed%20Issues" alt="[Closed Issues]">
</br>
<img src="https://img.shields.io/github/directory-file-count/AlbertUnruh/SSD-roster?label=Files" alt="[Files]">
<img src="https://img.shields.io/tokei/lines/github/AlbertUnruh/SSD-roster?label=Lines" alt="[Lines]">
<img src="https://img.shields.io/github/commit-activity/m/AlbertUnruh/SSD-roster?label=Commit%20Activity" alt="[Commit Activity]">


# SSD Roster
A project by AlbertUnruh.


---

## ToDo
A list of ToDo's can be found here: https://github.com/AlbertUnruh/SSD-roster/issues/1


---

## How To: Run The Code
The entrypoint is `SSD_Roster/app.py`. You can execute the file directly and the uvicorn server will start.

If you just want to *copy pasta* something, you can try this:
</br>*\*`git` and `pipenv` required*
```sh
git clone https://github.com/AlbertUnruh/SSD-roster.git
cd SSD-roster
pipenv install
cd SSD_Roster
python app.py
```

### Environment Variables
To change environment variables you can either change them in `.env` (⚠️`.env` is versioned, so the content of the file is "public"⚠️).

The recommended way to change environment variables is to create `.env.prod` in the same directory as `.env`.
Every variable set there will override the one set in `.env`.
