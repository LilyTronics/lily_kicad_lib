"""
Checks the projects to the library.
"""

import os

from scripts.models.design_checker import DesignChecker


class ProjectsChecker:

    SCRIPT_PATH = os.path.dirname(__file__)
    PROJECTS_PATH = os.path.abspath(os.path.join(SCRIPT_PATH, "..", "..", "projects"))

    @classmethod
    def run(cls):
        report_messages = []
        for project_folder in map(lambda x: os.path.join(cls.PROJECTS_PATH, x), os.listdir(cls.PROJECTS_PATH)):
            if os.path.isdir(project_folder):
                report_messages.extend(DesignChecker.run(project_folder))
        return report_messages


if __name__ == "__main__":

    messages = ProjectsChecker.run()
    print(f"{len(messages)} messages")
    for message in messages:
        print(message)
