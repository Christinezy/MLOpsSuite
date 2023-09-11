# BT4301 Project Backend

## Table of Contents

- [BT4301 Project Backend](#BT4301-Project-Backend)

  - [Table of Contents](#table-of-contents)

  <!-- - [Project Overview](#project-overview) -->

  - [Requirements](#requirements)
  - [Project Structure](#project-structure)
  - [Notes](#notes)

  <!-- - [Installation / Usage](#installation-&-usage) -->

  - [Usage](#usage)

## Requirements

1. Docker-compose installed in your system
2. Docker installed in your system

## Project Structure

```
.
├── data
│   ├── raw
│   ├── intermediate
│   ├── processed
│   └── temp
├── data_pipeline
│   ├── xxx
│   └── xxx
├── env                     <- python virtual environment files
│   ├── bin
│   ├── include
│   └── lib
├── env.py                  <- connectors to database and other infrastructure
├── notebooks               <- notebooks for explorations / prototyping
│   ├── xxx
│   └── xxx
├── results
│   ├── outputs
│   ├── models
│   └── weights
├── sql                     <- contains sql scripts
│   ├── init
│   ├── query
│   └── xxx
├── schema                  <- SQLAlchemy schema
└── main.py                  <- main Flask application
```

## Notes

## Usage

1. Activate the virutal environment

   ```bash
   source env/bin/activate
   ```
2. Run the Flask application

   ```bash
   ENV='DEV' python main.py
   ```
3. Backend API available at `localhost:5050`
