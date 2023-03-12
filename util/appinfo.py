import os

class AppInfo:
    def __init__(self):
        self.project_name = "python-blog".upper()
        self.author = "Yiğit GÜMÜŞ <github:yigitoo>"
        self.contributors = self.get_contributors()

    def get_contributors(self):
        contributors_list = []
        if os.getcwd().find('/src'):
            self.contrib_file = '../CONTRIBUTORS.md'
        else:
            self.contrib_file = 'CONTRIBUTORS.md'
            
        file = open(self.contrib_file, 'r')
        for line in file:
            if line.startswith('#'):
                continue    
            contributors_list.append(line)
        file.close()
        return contributors_list
    @staticmethod
    def print():
        print(str(AppInfo()))
        return
    
    def __str__(self):
        self.newline = '\n'
        return f"""{self.project_name}
{'=' * 15}
Author: {self.author}
---
Contributors:
{'-' * 15}
{(self.newline.join(self.contributors)).replace(' ', '')}
"""
    def __repr__(self):
        return self.__str__()
if __name__ == "__main__":
    appinfo = AppInfo()
    print(str(appinfo))