# project structure

quick overview of what files do what

```
project/
├── main.py              # main bot file - starts everything
├── scheduler.py         # handles daily sending stuff
├── reader.py            # pdf processing
├── database.json        # user data storage
├── tmp/                 # some helper stuff i wrote
│   ├── utils.py         # random utility functions
│   └── debug_helpers.py # debugging tools
└── book.pdf             # your book file
```

## main files

- **main.py** - telegram bot logic, handles all the commands and user interactions
- **scheduler.py** - background job that sends pages on schedule
- **database_manager.py** - manages user data in json file
- **pdf_reader.py** - converts pdf pages to images
- **config.py** - configuration stuff using pydantic

## other stuff

- **keyboards.py** - telegram inline keyboards  
- **user_settings.py** - per-user settings management
- **file_validator.py** - validates uploaded pdfs
- **cleanup_manager.py** - cleans up old image files

## test files

bunch of test files in tests/ folder - most of them work but some might be broken

## notes

- database is just a json file - not the most efficient but simple
- images are stored temporarily and cleaned up automatically 
- logs go to console and files
- everything is async because telegram bot framework requires it