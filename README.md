# openwebui-knowledge
This script will add/remove file(s) to Open WebUI knowledge.

Replace these variables with your settings:
```
- WEBUI_URL  : Open WebUI URL/IP address
- TOKEN      : Open WebUI account's API Key / JWT Token from Settings/Account tab
- LOG_FILE   : Filename for saving records
```
Usage:
```
knowledge.py [-h] [--add FULL_PATH] [--remove FULL_PATH] --id ID

FULL_PATH : a file or a folder contains files
ID        : knowledge id from "http://your-open-webui-instance:port/workspace/knowledge/id"

```
To add/remove a file, use this format:
```
--add ~/knowledge/my-knowledge-file.txt --id ID
--remove ~/knowledge/my-knowledge-file.txt --id ID
```
To add/remove files in a folder, use this format:
```
--add /path-to-knowledges/my-knowledge-folder --id ID
--remove /path-to-knowledges/my-knowledge-folder --id ID
```
Added file paths will be recorded with it's file id from Open WebUI vector database.
