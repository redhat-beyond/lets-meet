# Red Hat Beyond 07

Statement of Work (SOW)
***


## Milestones

### Demo 2 (April 3rd): Data model and business logic

The purpose of this demo is to show your application's data model and data
manipulation logic.

Technical requirements

1. For each feature you're planning to add to your project should include:

    1. Data model classes
    2. Migration files for initializing the data model
    3. Migration files for creating test data for your DEV environment
    4. Data model functions and model manager classes for the more complex data 
       operation you expect to do in your applications
    5. Tests for the data model functions and classes

2. Your bootstrap script should run the data migrations when your Vagrant VM
   starts up
3. You should have a CI job (GitHub Workflows) in GitHub that runs your tests
4. In your presentation you should:
    1. Present all design aspects of the features you're working on
       including [ERDs](https://www.lucidchart.com/pages/how-to-draw-ERD)
       and [DFDs](https://www.lucidchart.com/pages/data-flow-diagram) (data
       design and flow documents).
    2. Show your data model via the Django admin UI
    3. Present your data manipulation functions via the Django shell
    4. Show your test code and explain what you've tested

**Work division**

It is recommended that you divide the work in your team in a "vertical" way -
this means that each team member will have one or more project features assigned
to them, and they will be responsible for implementing all aspects of said
features including the data model, the tests, the control logic and the UI. 
A technical way to achieve this in Django is to have each team member create 
and maintain one or more separate Django "apps". 

Working in this way will provide several benefits:

1. It will allow each team member to experience all the layers of the technical
   stack
2. It can reduce the amount of Git conflicts you may encounter as you work on
   your projects because different features can live in different files.
