# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/LightWave2D/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                      |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| LightWave2D/components.py |      151 |       48 |        2 |        0 |     67% |81-91, 97-104, 115, 126, 137-140, 168-172, 178-184, 243, 268-275, 347-354, 383-385, 414-420 |
| LightWave2D/detector.py   |       67 |       25 |        2 |        0 |     61% |51-53, 59-61, 79-89, 96-108, 151-154, 161-168, 179 |
| LightWave2D/experiment.py |      181 |       75 |       28 |        4 |     54% |64, 78-85, 121, 143, 150, 157, 164, 171, 185, 199, 216, 221-222, 237, 280-310, 336-358, 397-496 |
| LightWave2D/grid.py       |       83 |        3 |       30 |        7 |     91% |21, 108->113, 113->118, 151, 184 |
| LightWave2D/helper.py     |       19 |       12 |        6 |        0 |     28% |     36-57 |
| LightWave2D/physics.py    |       11 |        0 |        0 |        0 |    100% |           |
| LightWave2D/pml.py        |       46 |       12 |        0 |        0 |     74% |74-78, 94-103 |
| LightWave2D/source.py     |      121 |       22 |        4 |        2 |     81% |27-33, 51-52, 70-72, 111, 143, 188, 245, 294-298, 343-347 |
| LightWave2D/utils.py      |       29 |        2 |       10 |        1 |     92% |     52-53 |
|                 **TOTAL** |  **708** |  **199** |   **82** |   **14** | **69%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/MartinPdeS/LightWave2D/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/MartinPdeS/LightWave2D/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/MartinPdeS/LightWave2D/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/MartinPdeS/LightWave2D/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FMartinPdeS%2FLightWave2D%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/MartinPdeS/LightWave2D/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.