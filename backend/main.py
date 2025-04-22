# This is a sample Python script.
import sys

from cmd import PyCharmUI

# Press ⇧⌘F11 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


if __name__ == "__main__":
    try:
        app = PyCharmUI()
        app.run()
    except Exception as e:
        print(f"‼️ 致命错误: {str(e)}")
        sys.exit(1)
