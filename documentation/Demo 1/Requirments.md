# Red Hat Beyond 07

Statement of Work (SOW)
***


## Milestones

### Demo 1 (March 13th): Project selection and setting up a DEV environment

The main purpose of the demo is to motivate you to come together as a project
development team and establish your shared working environment and process. As
such, we will monitor when and how you do the work of preparing for the demo,
and the process is as important (If not more so) as the final results you will
present.

As part of the preparation for this demo you should establish a new 
**public** channel in the Beyond Slack workspace for communications inside 
the team and with its mentors, get to know your teammates and your mentors 
and come up with the basic idea and name for your project.  

**Technical requirements**

To be ready for the demo, your project should include the following elements:

1. A working Vagrant environment that brings up the default Django web server
2. A basic Django application that includes a static web page showing the 
   name of your project and a short description about it
3. A GitHub repo in the Beyond organization with:
    1. A `README.md` file that introduces your project
    2. An MIT license file
    3. The contribution guide in a `CONTRIBUTING.md` file
    4. The code, as defined by other sections on this list
    
    (See below for detailed instructions about the contents of the 
   documentation files)
5. A basic GitHub workflow that executes Flake8 tests on files when there is a
   PR

Note that all these topics have been covered by the introduction exercise you
have been given.

**Work division**

To ensure that every member of your team plays an active role in preparing for
the demo, we require that you divide the work between you in the following way:

1. Student1: vagrant
2. Student2: bootstrap.sh
3. Student3: Django
4. Student4: Web page
5. Student5: Documentation files + flake8

**General guidelines**

1. Spend some time planning your work, understanding the order in which things
   need to be done and the dependencies between the various tasks
2. Ask your mentor(s) to create the main project repository for you in the
   Beyond organization.
3. Create GitHub issues to track the work your team needs to do and assign them
   to the students who will do them
4. You can subdivide the tasks above to smaller issues as needed, as long as
   you document what you plan clearly
5. Use PRs to make code changes to your project, link them to the relevant
   issues
6. Make sure you assign your teammates as well as your mentors as reviewers for
   your PRs
7. The review process can take a few days - make sure you send your PRs early
   enough, so they will be merged in time for the demo
8. You will be given a template for each demo with the specific details that are
   required
9. Designate a primary speaker for your team. Other members are encouraged to
   speak as well, but if so, plan who talks on what so you can all finish within
   the allocated time (15m).
10. It is recommended to pre-record technical demos to prevent technical issues
    from disturbing your demo
11. Please make sure all your teammates can successfully use Git to clone the
    team project and Vagrant to bring up the development environment on their
    machines.
